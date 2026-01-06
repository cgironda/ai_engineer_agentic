class Account:
    def __init__(self, username: str, initial_deposit: float) -> None:
        self.username = username
        self.balance = initial_deposit
        self.initial_deposit = initial_deposit
        self.holdings = {}
        self.transactions = []

    def deposit(self, amount: float) -> None:
        self.balance += amount

    def withdraw(self, amount: float) -> bool:
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

    def buy_shares(self, symbol: str, quantity: int, price_getter: callable) -> bool:
        price = price_getter(symbol)
        total_cost = price * quantity
        if self.balance >= total_cost:
            self.balance -= total_cost
            if symbol in self.holdings:
                self.holdings[symbol] += quantity
            else:
                self.holdings[symbol] = quantity
            self.transactions.append(('buy', symbol, quantity, price))
            return True
        return False

    def sell_shares(self, symbol: str, quantity: int, price_getter: callable) -> bool:
        if symbol in self.holdings and self.holdings[symbol] >= quantity:
            price = price_getter(symbol)
            total_revenue = price * quantity
            self.holdings[symbol] -= quantity
            self.balance += total_revenue
            self.transactions.append(('sell', symbol, quantity, price))
            return True
        return False

    def calculate_portfolio_value(self, price_getter: callable) -> float:
        total_value = self.balance
        for symbol, quantity in self.holdings.items():
            total_value += price_getter(symbol) * quantity
        return total_value

    def calculate_profit_or_loss(self, price_getter: callable) -> float:
        return self.calculate_portfolio_value(price_getter) - self.initial_deposit

    def report_holdings(self) -> dict:
        return self.holdings

    def report_profit_or_loss(self, price_getter: callable) -> float:
        return self.calculate_profit_or_loss(price_getter)

    def list_transactions(self) -> list:
        return self.transactions

# Example Implementation of get_share_price for Testing:
def get_share_price(symbol: str) -> float:
    prices = {
        'AAPL': 150.0,
        'TSLA': 700.0,
        'GOOGL': 2800.0
    }
    return prices.get(symbol, 0.0)