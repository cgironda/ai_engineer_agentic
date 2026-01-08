from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict, Optional

import gradio as gr
from fastapi import Body, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

from accounts import Account, PriceGetter, get_share_price


def structured_response(
    *,
    success: bool,
    message: str,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    response: Dict[str, Any] = {"success": success, "message": message}
    if data is not None:
        response["data"] = data
    if error:
        response["error"] = error
    if session_id:
        response["session_id"] = session_id
    return response


class SessionManager:
    def __init__(self, *, price_getter: PriceGetter):
        self._sessions: Dict[str, Account] = {}
        self.price_getter = price_getter

    def create_account(self, session_id: str, username: str, initial_deposit: float) -> Account:
        self._sessions[session_id] = Account(username=username, initial_deposit=initial_deposit)
        return self._sessions[session_id]

    def get_account(self, session_id: str) -> Account:
        if session_id not in self._sessions:
            raise KeyError("Account not found for this session. Create an account first.")
        return self._sessions[session_id]

    def account_snapshot(self, session_id: str) -> Dict[str, Any]:
        account = self.get_account(session_id)
        return account.to_dict(self.price_getter)


session_manager = SessionManager(price_getter=get_share_price)


def _ensure_session_id(session_id: Optional[str], *, allow_generate: bool = True) -> str:
    if session_id:
        return session_id
    if not allow_generate:
        raise HTTPException(status_code=400, detail="Session token is required")
    return uuid.uuid4().hex


class SessionScopedRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description="Client session identifier")

    def resolve_session(self) -> str:
        return _ensure_session_id(self.session_id)


class CreateAccountRequest(SessionScopedRequest):
    username: str = Field(..., min_length=1)
    initial_deposit: float = Field(0.0, ge=0.0)


class AmountRequest(SessionScopedRequest):
    amount: float = Field(..., gt=0.0)


class TradeRequest(SessionScopedRequest):
    symbol: str
    quantity: int = Field(..., gt=0)

    @validator("symbol")
    def validate_symbol(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Symbol is required")
        return value.upper()


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    session_id: Optional[str] = None


def _resolve_session_id(payload_session: Optional[str], header_session: Optional[str]) -> str:
    return _ensure_session_id(payload_session or header_session)


def _account_or_http_error(session_id: str) -> Account:
    try:
        return session_manager.get_account(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


fastapi_app = FastAPI(title="Trading Simulation API", version="0.2.0")
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()]
CORS_ALLOW_ALL = CORS_ORIGINS == ["*"]
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if CORS_ALLOW_ALL else CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@fastapi_app.post("/api/account/create", response_model=ApiResponse)
def api_create_account(
    payload: CreateAccountRequest = Body(...),
    x_session_id: Optional[str] = Header(default=None, alias="X-Session-Id"),
) -> Dict[str, Any]:
    session_id = _resolve_session_id(payload.session_id, x_session_id)
    try:
        account = session_manager.create_account(session_id, payload.username, payload.initial_deposit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return structured_response(
        success=True,
        message="Account created",
        data={"account": account.to_dict(get_share_price)},
        session_id=session_id,
    )


@fastapi_app.post("/api/account/deposit", response_model=ApiResponse)
def api_deposit(
    payload: AmountRequest = Body(...),
    x_session_id: Optional[str] = Header(default=None, alias="X-Session-Id"),
) -> Dict[str, Any]:
    session_id = _resolve_session_id(payload.session_id, x_session_id)
    account = _account_or_http_error(session_id)
    try:
        txn = account.deposit(payload.amount)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return structured_response(
        success=True,
        message="Deposit completed",
        data={"account": account.to_dict(get_share_price), "transaction": txn.as_dict()},
        session_id=session_id,
    )


@fastapi_app.post("/api/account/withdraw", response_model=ApiResponse)
def api_withdraw(
    payload: AmountRequest = Body(...),
    x_session_id: Optional[str] = Header(default=None, alias="X-Session-Id"),
) -> Dict[str, Any]:
    session_id = _resolve_session_id(payload.session_id, x_session_id)
    account = _account_or_http_error(session_id)
    try:
        txn = account.withdraw(payload.amount)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return structured_response(
        success=True,
        message="Withdrawal completed",
        data={"account": account.to_dict(get_share_price), "transaction": txn.as_dict()},
        session_id=session_id,
    )


@fastapi_app.post("/api/trade/buy", response_model=ApiResponse)
def api_buy(
    payload: TradeRequest = Body(...),
    x_session_id: Optional[str] = Header(default=None, alias="X-Session-Id"),
) -> Dict[str, Any]:
    session_id = _resolve_session_id(payload.session_id, x_session_id)
    account = _account_or_http_error(session_id)
    try:
        txn = account.buy_shares(payload.symbol, payload.quantity, get_share_price)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return structured_response(
        success=True,
        message=f"Bought {payload.quantity} {payload.symbol}",
        data={"account": account.to_dict(get_share_price), "transaction": txn.as_dict()},
        session_id=session_id,
    )


@fastapi_app.post("/api/trade/sell", response_model=ApiResponse)
def api_sell(
    payload: TradeRequest = Body(...),
    x_session_id: Optional[str] = Header(default=None, alias="X-Session-Id"),
) -> Dict[str, Any]:
    session_id = _resolve_session_id(payload.session_id, x_session_id)
    account = _account_or_http_error(session_id)
    try:
        txn = account.sell_shares(payload.symbol, payload.quantity, get_share_price)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return structured_response(
        success=True,
        message=f"Sold {payload.quantity} {payload.symbol}",
        data={"account": account.to_dict(get_share_price), "transaction": txn.as_dict()},
        session_id=session_id,
    )


@fastapi_app.get("/api/portfolio/value", response_model=ApiResponse)
def api_portfolio_value(x_session_id: Optional[str] = Header(default=None, alias="X-Session-Id")) -> Dict[str, Any]:
    session_id = _ensure_session_id(x_session_id, allow_generate=False)
    account = _account_or_http_error(session_id)
    return structured_response(
        success=True,
        message="Portfolio value retrieved",
        data={"portfolio_value": account.calculate_portfolio_value(get_share_price)},
        session_id=session_id,
    )


@fastapi_app.get("/api/portfolio/profit_loss", response_model=ApiResponse)
def api_profit_loss(x_session_id: Optional[str] = Header(default=None, alias="X-Session-Id")) -> Dict[str, Any]:
    session_id = _ensure_session_id(x_session_id, allow_generate=False)
    account = _account_or_http_error(session_id)
    return structured_response(
        success=True,
        message="Profit/Loss retrieved",
        data={"profit_loss": account.calculate_profit_or_loss(get_share_price)},
        session_id=session_id,
    )


@fastapi_app.get("/api/holdings", response_model=ApiResponse)
def api_holdings(x_session_id: Optional[str] = Header(default=None, alias="X-Session-Id")) -> Dict[str, Any]:
    session_id = _ensure_session_id(x_session_id, allow_generate=False)
    account = _account_or_http_error(session_id)
    return structured_response(
        success=True,
        message="Holdings retrieved",
        data={"holdings": account.report_holdings()},
        session_id=session_id,
    )


@fastapi_app.get("/api/transactions", response_model=ApiResponse)
def api_transactions(x_session_id: Optional[str] = Header(default=None, alias="X-Session-Id")) -> Dict[str, Any]:
    session_id = _ensure_session_id(x_session_id, allow_generate=False)
    account = _account_or_http_error(session_id)
    return structured_response(
        success=True,
        message="Transactions retrieved",
        data={"transactions": account.list_transactions()},
        session_id=session_id,
    )


@fastapi_app.get("/api/account/snapshot", response_model=ApiResponse)
def api_account_snapshot(x_session_id: Optional[str] = Header(default=None, alias="X-Session-Id")) -> Dict[str, Any]:
    session_id = _ensure_session_id(x_session_id, allow_generate=False)
    _account_or_http_error(session_id)
    snapshot = session_manager.account_snapshot(session_id)
    return structured_response(
        success=True,
        message="Account snapshot retrieved",
        data={"account": snapshot},
        session_id=session_id,
    )


def _format_response_string(response: Dict[str, Any]) -> str:
    return f"**{response['message']}**\n\n```json\n{json.dumps(response, indent=2)}\n```"


def _ensure_account_for_ui(session_id: str, username: Optional[str], initial_deposit: float) -> Account:
    try:
        return session_manager.get_account(session_id)
    except KeyError:
        return session_manager.create_account(session_id, username or "guest", initial_deposit)


def ui_create_account(session_id: str, username: str, initial_deposit: float) -> tuple[str, str]:
    session = _ensure_session_id(session_id)
    account = session_manager.create_account(session, username, initial_deposit or 0.0)
    response = structured_response(
        success=True,
        message="Account created",
        data={"account": account.to_dict(get_share_price)},
        session_id=session,
    )
    return session, _format_response_string(response)


def _run_account_action(
    session_id: str,
    action: str,
    *,
    amount: Optional[float] = None,
    symbol: Optional[str] = None,
    quantity: Optional[int] = None,
    username: Optional[str] = None,
    initial_deposit: float = 0.0,
) -> tuple[str, str]:
    if not session_id:
        raise ValueError("Session token is required. Use 'Set Session' first.")
    account = _ensure_account_for_ui(session_id, username, initial_deposit)
    try:
        if action == "deposit":
            txn = account.deposit(amount or 0.0)
            message = "Deposit completed"
        elif action == "withdraw":
            txn = account.withdraw(amount or 0.0)
            message = "Withdrawal completed"
        elif action == "buy":
            txn = account.buy_shares(symbol or "", int(quantity or 0), get_share_price)
            message = f"Bought {quantity} {symbol}"
        elif action == "sell":
            txn = account.sell_shares(symbol or "", int(quantity or 0), get_share_price)
            message = f"Sold {quantity} {symbol}"
        else:
            raise ValueError("Unsupported action")
    except ValueError as exc:
        response = structured_response(success=False, message="Operation failed", error=str(exc), session_id=session_id)
        return session_id, _format_response_string(response)

    response = structured_response(
        success=True,
        message=message,
        data={"account": account.to_dict(get_share_price), "transaction": txn.as_dict()},
        session_id=session_id,
    )
    return session_id, _format_response_string(response)


def ui_get_snapshot(session_id: str) -> tuple[str, str]:
    if not session_id:
        raise ValueError("Session token is required. Use 'Set Session' first.")
    snapshot = session_manager.account_snapshot(session_id)
    response = structured_response(success=True, message="Account snapshot", data={"account": snapshot}, session_id=session_id)
    return session_id, _format_response_string(response)


with gr.Blocks(title="Trading Simulator") as gradio_app:
    gr.Markdown("# Trading Simulator\nUse the controls below to manage your session, trade, and view the portfolio.")

    with gr.Row():
        session_input = gr.Textbox(label="Session Token", placeholder="Provide your token or leave blank to auto-create")
        set_session_btn = gr.Button("Set Session")
        session_display = gr.Markdown()

    def set_session(session_candidate: str) -> tuple[str, str]:
        session = _ensure_session_id(session_candidate)
        return session, f"Using session `{session}`"

    set_session_btn.click(set_session, inputs=session_input, outputs=[session_input, session_display])

    with gr.Tab("Create Account"):
        username = gr.Textbox(label="Username")
        initial_deposit = gr.Number(label="Initial Deposit", value=0.0)
        create_btn = gr.Button("Create")
        create_output = gr.Markdown()
        create_btn.click(
            ui_create_account,
            inputs=[session_input, username, initial_deposit],
            outputs=[session_input, create_output],
        )

    with gr.Tab("Cash"):
        deposit_amount = gr.Number(label="Deposit Amount", value=100.0)
        withdraw_amount = gr.Number(label="Withdraw Amount", value=50.0)
        deposit_btn = gr.Button("Deposit")
        withdraw_btn = gr.Button("Withdraw")
        cash_output = gr.Markdown()
        deposit_btn.click(
            lambda session, amount, user, seed: _run_account_action(
                session,
                "deposit",
                amount=amount,
                username=user,
                initial_deposit=seed,
            ),
            inputs=[session_input, deposit_amount, username, initial_deposit],
            outputs=[session_input, cash_output],
        )
        withdraw_btn.click(
            lambda session, amount, user, seed: _run_account_action(
                session,
                "withdraw",
                amount=amount,
                username=user,
                initial_deposit=seed,
            ),
            inputs=[session_input, withdraw_amount, username, initial_deposit],
            outputs=[session_input, cash_output],
        )

    with gr.Tab("Trading"):
        symbol = gr.Textbox(label="Symbol", value="AAPL")
        quantity = gr.Number(label="Quantity", value=1, precision=0)
        buy_btn = gr.Button("Buy")
        sell_btn = gr.Button("Sell")
        trade_output = gr.Markdown()
        buy_btn.click(
            lambda session, sym, qty, user, seed: _run_account_action(
                session,
                "buy",
                symbol=sym,
                quantity=int(qty or 0),
                username=user,
                initial_deposit=seed,
            ),
            inputs=[session_input, symbol, quantity, username, initial_deposit],
            outputs=[session_input, trade_output],
        )
        sell_btn.click(
            lambda session, sym, qty, user, seed: _run_account_action(
                session,
                "sell",
                symbol=sym,
                quantity=int(qty or 0),
                username=user,
                initial_deposit=seed,
            ),
            inputs=[session_input, symbol, quantity, username, initial_deposit],
            outputs=[session_input, trade_output],
        )

    with gr.Tab("Reports"):
        refresh_btn = gr.Button("Refresh Snapshot")
        report_output = gr.Markdown()
        refresh_btn.click(ui_get_snapshot, inputs=session_input, outputs=[session_input, report_output])


app = gr.mount_gradio_app(
    fastapi_app,
    gradio_app,
    path="/",
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
