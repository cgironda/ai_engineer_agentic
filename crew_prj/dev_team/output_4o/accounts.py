from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

PriceGetter = Callable[[str], float]
Clock = Callable[[], datetime]


def default_clock() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Transaction:
    type: str
    symbol: Optional[str]
    quantity: Optional[int]
    price: Optional[float]
    amount: Optional[float]
    timestamp: datetime

    def as_dict(self) -> Dict[str, object]:
        return {
            "type": self.type,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "price": self.price,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Account:
    username: str
    initial_deposit: float
    clock: Clock = default_clock
    balance: float = field(init=False)
    holdings: Dict[str, int] = field(init=False, default_factory=dict)
    transactions: List[Transaction] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        if self.initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative")
        self.balance = 0.0
        if self.initial_deposit > 0:
            self.deposit(self.initial_deposit)

    def _validate_amount(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

    def _validate_symbol(self, symbol: str) -> None:
        if not symbol or not symbol.strip():
            raise ValueError("Symbol is required")

    def _validate_quantity(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

    def _record(self, *, type_: str, symbol: Optional[str], quantity: Optional[int], price: Optional[float], amount: Optional[float]) -> Transaction:
        txn = Transaction(
            type=type_,
            symbol=symbol,
            quantity=quantity,
            price=price,
            amount=amount,
            timestamp=self.clock(),
        )
        self.transactions.append(txn)
        return txn

    def deposit(self, amount: float) -> Transaction:
        self._validate_amount(amount)
        self.balance += amount
        return self._record(type_="deposit", symbol=None, quantity=None, price=None, amount=amount)

    def withdraw(self, amount: float) -> Transaction:
        self._validate_amount(amount)
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return self._record(type_="withdraw", symbol=None, quantity=None, price=None, amount=amount)

    def buy_shares(self, symbol: str, quantity: int, price_getter: PriceGetter) -> Transaction:
        self._validate_symbol(symbol)
        self._validate_quantity(quantity)
        price = price_getter(symbol)
        if price <= 0:
            raise ValueError(f"Price unavailable for {symbol}")
        total_cost = price * quantity
        if self.balance < total_cost:
            raise ValueError("Insufficient funds for purchase")
        self.balance -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        return self._record(type_="buy", symbol=symbol, quantity=quantity, price=price, amount=total_cost)

    def sell_shares(self, symbol: str, quantity: int, price_getter: PriceGetter) -> Transaction:
        self._validate_symbol(symbol)
        self._validate_quantity(quantity)
        if self.holdings.get(symbol, 0) < quantity:
            raise ValueError("Insufficient shares to sell")
        price = price_getter(symbol)
        if price <= 0:
            raise ValueError(f"Price unavailable for {symbol}")
        total_revenue = price * quantity
        self.holdings[symbol] -= quantity
        self.balance += total_revenue
        return self._record(type_="sell", symbol=symbol, quantity=quantity, price=price, amount=total_revenue)

    def calculate_portfolio_value(self, price_getter: PriceGetter) -> float:
        total_value = self.balance
        for symbol, quantity in self.holdings.items():
            price = price_getter(symbol)
            if price <= 0:
                continue
            total_value += price * quantity
        return round(total_value, 2)

    def calculate_profit_or_loss(self, price_getter: PriceGetter) -> float:
        return round(self.calculate_portfolio_value(price_getter) - self.initial_deposit, 2)

    def report_holdings(self) -> Dict[str, int]:
        return dict(self.holdings)

    def list_transactions(self) -> List[Dict[str, object]]:
        return [txn.as_dict() for txn in self.transactions]

    def to_dict(self, price_getter: PriceGetter) -> Dict[str, object]:
        return {
            "username": self.username,
            "balance": self.balance,
            "holdings": self.report_holdings(),
            "portfolio_value": self.calculate_portfolio_value(price_getter),
            "profit_or_loss": self.calculate_profit_or_loss(price_getter),
            "transactions": self.list_transactions(),
        }


def get_share_price(symbol: str) -> float:
    prices = {
        "AAPL": 150.0,
        "TSLA": 700.0,
        "GOOGL": 2800.0,
        "MSFT": 400.0,
        "NFLX": 500.0,
    }
    return prices.get(symbol.upper(), 0.0)
