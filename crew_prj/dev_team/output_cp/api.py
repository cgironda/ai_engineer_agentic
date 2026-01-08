from __future__ import annotations

from typing import Optional

import logging

from fastapi import FastAPI, Header
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
from constants import SESSION_HEADER
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
    "account_creation_failed": 400,
}


class CreateAccountRequest(BaseModel):
    username: str = Field(..., min_length=1)
    initial_deposit: float = Field(..., gt=0)


class AmountRequest(BaseModel):
    amount: float = Field(..., gt=0)


class TradeRequest(BaseModel):
    symbol: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)


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
    def api_create_account(payload: CreateAccountRequest):
        return _respond(create_account(store, payload.username, payload.initial_deposit))

    @app.post("/api/deposit")
    def api_deposit(
        payload: AmountRequest,
        x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER),
    ):
        return _respond(deposit(store, x_session_token, payload.amount))

    @app.post("/api/withdraw")
    def api_withdraw(
        payload: AmountRequest,
        x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER),
    ):
        return _respond(withdraw(store, x_session_token, payload.amount))

    @app.post("/api/trade/buy")
    def api_buy(
        payload: TradeRequest,
        x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER),
    ):
        return _respond(buy(store, x_session_token, payload.symbol, payload.quantity))

    @app.post("/api/trade/sell")
    def api_sell(
        payload: TradeRequest,
        x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER),
    ):
        return _respond(sell(store, x_session_token, payload.symbol, payload.quantity))

    @app.get("/api/status")
    def api_status(x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER)):
        return _respond(status(store, x_session_token))

    @app.get("/api/holdings")
    def api_holdings(x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER)):
        return _respond(holdings(store, x_session_token))

    @app.get("/api/transactions")
    def api_transactions(x_session_token: Optional[str] = Header(None, alias=SESSION_HEADER)):
        return _respond(transactions(store, x_session_token))

    @app.get("/api/prices")
    def api_prices():
        return _respond(prices())

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
