from __future__ import annotations

from typing import Optional

import logging

from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import (
    get_cors_origins,
    get_server_host,
    get_server_port,
    get_server_reload,
    get_session_ttl_seconds,
)
from constants import SESSION_COOKIE_NAME, SESSION_HEADER
from services import (
    buy,
    create_account,
    deposit,
    holdings,
    prices,
    sell,
    status,
    transactions,
    withdraw,
)
from session_store import SessionStore

logger = logging.getLogger(__name__)

ERROR_STATUS_BY_CODE = {
    "invalid_session": 401,
    "missing_username": 400,
    "invalid_initial_deposit": 400,
    "invalid_quantity": 400,
    "unknown_symbol": 400,
    "deposit_failed": 400,
    "withdraw_failed": 400,
    "buy_failed": 400,
    "sell_failed": 400,
    "account_creation_failed": 500,
}

TOKEN_RETURN_HEADER = "X-Return-Token"
COOKIE_SAMESITE = "lax"


class CreateAccountRequest(BaseModel):
    username: str = Field(..., min_length=1)
    initial_deposit: float = Field(..., gt=0)


class AmountRequest(BaseModel):
    amount: float = Field(..., gt=0)


class TradeRequest(BaseModel):
    symbol: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)


def _should_return_token(value: Optional[str]) -> bool:
    if not value:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_token(request: Request, header_token: Optional[str]) -> Optional[str]:
    if header_token:
        return header_token
    return request.cookies.get(SESSION_COOKIE_NAME)


def build_app(store: Optional[SessionStore] = None, mount_gradio: bool = True) -> FastAPI:
    store = store or SessionStore(ttl_seconds=get_session_ttl_seconds())
    app = FastAPI(title="Trading Account API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def _respond(payload):
        if payload.get("success"):
            return payload
        status_code = ERROR_STATUS_BY_CODE.get(payload.get("error"), 400)
        return JSONResponse(status_code=status_code, content=payload)

    @app.post("/api/account")
    def api_create_account(
        payload: CreateAccountRequest,
        request: Request,
        x_return_token: Optional[str] = Header(None, alias=TOKEN_RETURN_HEADER),
    ):
        result = create_account(store, payload.username, payload.initial_deposit)
        if not result.get("success"):
            return _respond(result)
        token = result.get("data", {}).get("token")
        response_payload = result
        if token and not _should_return_token(x_return_token):
            sanitized = dict(result)
            data = dict(result.get("data", {}))
            data.pop("token", None)
            sanitized["data"] = data
            response_payload = sanitized
        response = JSONResponse(content=response_payload)
        if token:
            ttl = get_session_ttl_seconds()
            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=token,
                max_age=ttl,
                httponly=True,
                samesite=COOKIE_SAMESITE,
            )
        return response

    @app.post("/api/deposit")
    def api_deposit(
        request: Request,
        payload: AmountRequest,
        x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER),
    ):
        token = _resolve_token(request, x_session_token)
        return _respond(deposit(store, token, payload.amount))

    @app.post("/api/withdraw")
    def api_withdraw(
        request: Request,
        payload: AmountRequest,
        x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER),
    ):
        token = _resolve_token(request, x_session_token)
        return _respond(withdraw(store, token, payload.amount))

    @app.post("/api/trade/buy")
    def api_buy(
        request: Request,
        payload: TradeRequest,
        x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER),
    ):
        token = _resolve_token(request, x_session_token)
        return _respond(buy(store, token, payload.symbol, payload.quantity))

    @app.post("/api/trade/sell")
    def api_sell(
        request: Request,
        payload: TradeRequest,
        x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER),
    ):
        token = _resolve_token(request, x_session_token)
        return _respond(sell(store, token, payload.symbol, payload.quantity))

    @app.get("/api/status")
    def api_status(
        request: Request,
        x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER),
    ):
        token = _resolve_token(request, x_session_token)
        return _respond(status(store, token))

    @app.get("/api/holdings")
    def api_holdings(
        request: Request,
        x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER),
    ):
        token = _resolve_token(request, x_session_token)
        return _respond(holdings(store, token))

    @app.get("/api/transactions")
    def api_transactions(
        request: Request,
        x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER),
    ):
        token = _resolve_token(request, x_session_token)
        return _respond(transactions(store, token))

    @app.get("/api/prices")
    def api_prices():
        return _respond(prices())

    class SessionRequest(BaseModel):
        token: str = Field(..., min_length=1)

    @app.post("/api/session")
    def api_session(payload: SessionRequest):
        account = store.get_account(payload.token)
        if account is None:
            return _respond({"success": False, "message": "Invalid session token.", "error": "invalid_session"})
        response = JSONResponse(
            content={
                "success": True,
                "message": "Session restored.",
                "data": {"account": status(store, payload.token).get("data", {}).get("account")},
            }
        )
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=payload.token,
            max_age=get_session_ttl_seconds(),
            httponly=True,
            samesite=COOKIE_SAMESITE,
        )
        return response

    @app.post("/api/logout")
    def api_logout(request: Request, x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER)):
        token = _resolve_token(request, x_session_token)
        if token:
            store.delete_session(token)
        response = JSONResponse(content={"success": True, "message": "Session cleared."})
        response.delete_cookie(SESSION_COOKIE_NAME)
        return response

    @app.get("/api/health")
    def api_health():
        return {"status": "ok"}

    if mount_gradio:
        try:
            import gradio as gr
            from gradio_app import demo as gradio_demo

            app = gr.mount_gradio_app(app, gradio_demo, path="/gradio")
        except Exception as exc:
            logger.exception("Failed to mount Gradio app: %s", exc)

    return app


app = build_app()


if __name__ == "__main__":
    try:
        import uvicorn
    except Exception:
        raise SystemExit("uvicorn is required to run the API server.")

    uvicorn.run(
        "api:app",
        host=get_server_host(),
        port=get_server_port(),
        reload=get_server_reload(),
    )
