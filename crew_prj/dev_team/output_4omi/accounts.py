class Account:
    def __init__(self, account_id: str, initial_deposit: float):
        """Initialize a new trading account with an account ID and an initial deposit."""
        self.account_id = account_id
        self.balance = initial_deposit
        self.portfolio = {}  # Holds stock symbols and quantities.
        self.transactions = []  # List of transaction descriptions.

    def deposit(self, amount: float) -> None:
        """Deposit funds into the trading account."""
        self.balance += amount
        self.transactions.append(f"Deposited: ${amount:.2f}")

    def withdraw(self, amount: float) -> None:
        """Withdraw funds from the trading account."""
        if amount > self.balance:
            raise ValueError("Insufficient funds for withdrawal.")
        self.balance -= amount
        self.transactions.append(f"Withdrew: ${amount:.2f}")

    def buy_shares(self, symbol: str, quantity: int) -> None:
        """Buy shares of a stock using available funds."""
        total_price = get_share_price(symbol) * quantity
        if total_price > self.balance:
            raise ValueError("Insufficient funds to buy shares.")

        self.balance -= total_price
        self.portfolio[symbol] = self.portfolio.get(symbol, 0) + quantity
        self.transactions.append(
            f"Bought: {quantity} shares of {symbol} at ${total_price:.2f}"
        )

    def sell_shares(self, symbol: str, quantity: int) -> None:
        """Sell shares of a stock."""
        if symbol not in self.portfolio or self.portfolio[symbol] < quantity:
            raise ValueError("Insufficient shares to sell.")

        total_price = get_share_price(symbol) * quantity
        self.balance += total_price
        self.portfolio[symbol] -= quantity

        if self.portfolio[symbol] == 0:
            del self.portfolio[symbol]

        self.transactions.append(
            f"Sold: {quantity} shares of {symbol} at ${total_price:.2f}"
        )

    def get_portfolio_value(self) -> float:
        """Return the total value of the portfolio (cash + holdings)."""
        total_value = self.balance
        for symbol, quantity in self.portfolio.items():
            total_value += get_share_price(symbol) * quantity
        return total_value

    def calculate_profit_loss(self, initial_deposit: float) -> float:
        """Calculate the profit or loss relative to the initial deposit."""
        return self.get_portfolio_value() - initial_deposit

    def get_holdings(self) -> dict:
        """Return the current holdings as a symbol -> quantity mapping."""
        return self.portfolio

    def get_profit_loss(self, initial_deposit: float) -> float:
        """Return the profit or loss at the current point in time."""
        return self.calculate_profit_loss(initial_deposit)

    def list_transactions(self) -> list:
        """Return a list of recorded transactions."""
        return self.transactions


def get_share_price(symbol: str) -> float:
    """Return the current price of a share for a given symbol."""
    prices = {
        "AAPL": 150.00,
        "TSLA": 700.00,
        "GOOGL": 2800.00,
    }
    return prices.get(symbol, 0.0)
