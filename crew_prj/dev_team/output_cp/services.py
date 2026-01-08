from __future__ import annotations

from typing import Any, Dict, Optional

from accounts import Account, get_share_price
from constants import SUPPORTED_SYMBOLS
from responses import error, ok
from session_store import SessionStore


def _account_snapshot(account: Account) -> Dict[str, Any]:
    return {
        "username": account.username,
        "balance": account.balance,
        "initial_deposit": account.initial_deposit,
        "portfolio_value": account.calculate_portfolio_value(),
        "profit_loss": account.calculate_profit_loss(),
    }


def _holdings_snapshot(account: Account) -> Dict[str, Any]:
    holdings = account.report_holdings()
    return {
        "holdings": holdings,
        "holding_values": {
            symbol: get_share_price(symbol) * quantity
            for symbol, quantity in holdings.items()
        },
    }


def _transactions_snapshot(account: Account) -> Dict[str, Any]:
    return {"transactions": account.report_transactions()}


def _require_account(store: SessionStore, token: Optional[str]) -> Optional[Account]:
    if not token:
        return None
    return store.get_account(token)


def create_account(store: SessionStore, username: str, initial_deposit: float) -> Dict[str, Any]:
    if not username:
        return error("Username is required.", "missing_username")
    if initial_deposit <= 0:
        return error("Initial deposit must be greater than zero.", "invalid_initial_deposit")
    try:
        account = Account(username, float(initial_deposit))
    except Exception as exc:
        return error(str(exc), "account_creation_failed")

    token = store.create_session(account)
    data = {
        "token": token,
        "account": _account_snapshot(account),
        "holdings": _holdings_snapshot(account),
    }
    return ok(f"Account created for {username}.", data)


def deposit(store: SessionStore, token: Optional[str], amount: float) -> Dict[str, Any]:
    account = _require_account(store, token)
    if account is None:
        return error("Session token is missing or invalid.", "invalid_session")
    try:
        account.deposit(float(amount))
    except Exception as exc:
        return error(str(exc), "deposit_failed")
    return ok("Deposit completed.", {"account": _account_snapshot(account)})


def withdraw(store: SessionStore, token: Optional[str], amount: float) -> Dict[str, Any]:
    account = _require_account(store, token)
    if account is None:
        return error("Session token is missing or invalid.", "invalid_session")
    try:
        account.withdraw(float(amount))
    except Exception as exc:
        return error(str(exc), "withdraw_failed")
    return ok("Withdrawal completed.", {"account": _account_snapshot(account)})


def buy(store: SessionStore, token: Optional[str], symbol: str, quantity: int) -> Dict[str, Any]:
    account = _require_account(store, token)
    if account is None:
        return error("Session token is missing or invalid.", "invalid_session")
    symbol = symbol.strip().upper()
    if symbol not in SUPPORTED_SYMBOLS:
        return error(f"Unknown symbol '{symbol}'.", "unknown_symbol")
    if quantity <= 0:
        return error("Quantity must be greater than zero.", "invalid_quantity")

    try:
        price = get_share_price(symbol)
        account.buy_shares(symbol, int(quantity))
    except Exception as exc:
        return error(str(exc), "buy_failed")

    return ok(
        f"Bought {quantity} shares of {symbol}.",
        {
            "trade": {
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "total": price * quantity,
            },
            "account": _account_snapshot(account),
            "holdings": _holdings_snapshot(account),
        },
    )


def sell(store: SessionStore, token: Optional[str], symbol: str, quantity: int) -> Dict[str, Any]:
    account = _require_account(store, token)
    if account is None:
        return error("Session token is missing or invalid.", "invalid_session")
    symbol = symbol.strip().upper()
    if symbol not in SUPPORTED_SYMBOLS:
        return error(f"Unknown symbol '{symbol}'.", "unknown_symbol")
    if quantity <= 0:
        return error("Quantity must be greater than zero.", "invalid_quantity")

    try:
        price = get_share_price(symbol)
        account.sell_shares(symbol, int(quantity))
    except Exception as exc:
        return error(str(exc), "sell_failed")

    return ok(
        f"Sold {quantity} shares of {symbol}.",
        {
            "trade": {
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "total": price * quantity,
            },
            "account": _account_snapshot(account),
            "holdings": _holdings_snapshot(account),
        },
    )


def status(store: SessionStore, token: Optional[str]) -> Dict[str, Any]:
    account = _require_account(store, token)
    if account is None:
        return error("Session token is missing or invalid.", "invalid_session")
    return ok("Account status retrieved.", {"account": _account_snapshot(account)})


def holdings(store: SessionStore, token: Optional[str]) -> Dict[str, Any]:
    account = _require_account(store, token)
    if account is None:
        return error("Session token is missing or invalid.", "invalid_session")
    data = {"account": _account_snapshot(account)}
    data.update(_holdings_snapshot(account))
    return ok("Holdings retrieved.", data)


def transactions(store: SessionStore, token: Optional[str]) -> Dict[str, Any]:
    account = _require_account(store, token)
    if account is None:
        return error("Session token is missing or invalid.", "invalid_session")
    data = {"account": _account_snapshot(account)}
    data.update(_transactions_snapshot(account))
    return ok("Transactions retrieved.", data)


def prices() -> Dict[str, Any]:
    return ok(
        "Prices retrieved.",
        {
            "symbols": {
                symbol: get_share_price(symbol)
                for symbol in SUPPORTED_SYMBOLS
            }
        },
    )
