import unittest

class Account:
    def __init__(self, account_id: str, initial_deposit: float):
        self.account_id = account_id
        self.balance = initial_deposit
        self.portfolio = {}  # Holds stock symbols and quantities
        self.transactions = []  # List of transactions made

    def deposit(self, amount: float) -> None:
        self.balance += amount
        self.transactions.append(f"Deposited: ${amount:.2f}")

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise ValueError("Insufficient funds for withdrawal.")
        self.balance -= amount
        self.transactions.append(f"Withdrew: ${amount:.2f}")

    def buy_shares(self, symbol: str, quantity: int) -> None:
        total_price = get_share_price(symbol) * quantity
        if total_price > self.balance:
            raise ValueError("Insufficient funds to buy shares.")
        self.balance -= total_price
        self.portfolio[symbol] = self.portfolio.get(symbol, 0) + quantity
        self.transactions.append(f"Bought: {quantity} shares of {symbol} at ${total_price:.2f}")

    def sell_shares(self, symbol: str, quantity: int) -> None:
        if symbol not in self.portfolio or self.portfolio[symbol] < quantity:
            raise ValueError("Insufficient shares to sell.")
        total_price = get_share_price(symbol) * quantity
        self.balance += total_price
        self.portfolio[symbol] -= quantity
        if self.portfolio[symbol] == 0:
            del self.portfolio[symbol]
        self.transactions.append(f"Sold: {quantity} shares of {symbol} at ${total_price:.2f}")

    def get_portfolio_value(self) -> float:
        total_value = self.balance
        for symbol, quantity in self.portfolio.items():
            total_value += get_share_price(symbol) * quantity
        return total_value

    def calculate_profit_loss(self, initial_deposit: float) -> float:
        return self.get_portfolio_value() - initial_deposit

    def get_holdings(self) -> dict:
        return self.portfolio

    def get_profit_loss(self, initial_deposit: float) -> float:
        return self.calculate_profit_loss(initial_deposit)

    def list_transactions(self) -> list:
        return self.transactions


def get_share_price(symbol: str) -> float:
    prices = {"AAPL": 150.00, "TSLA": 700.00, "GOOGL": 2800.00}
    return prices.get(symbol, 0.0)


class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = Account('12345', 1000.0)

    def test_initial_balance(self):
        self.assertEqual(self.account.balance, 1000.0)

    def test_deposit(self):
        self.account.deposit(500.0)
        self.assertEqual(self.account.balance, 1500.0)

    def test_withdraw(self):
        self.account.withdraw(300.0)
        self.assertEqual(self.account.balance, 700.0)

    def test_withdraw_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(1200.0)

    def test_buy_shares(self):
        self.account.buy_shares('AAPL', 3)  # Buying 3 shares of AAPL
        self.assertEqual(self.account.portfolio['AAPL'], 3)
        self.assertEqual(self.account.balance, 1000.0 - 3 * 150.0)

    def test_buy_shares_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', 10)  # More than can be purchased

    def test_sell_shares(self):
        self.account.buy_shares('AAPL', 3)
        self.account.sell_shares('AAPL', 1)
        self.assertEqual(self.account.portfolio['AAPL'], 2)

    def test_sell_shares_insufficient(self):
        self.account.buy_shares('AAPL', 3)
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', 4)

    def test_portfolio_value(self):
        self.account.buy_shares('AAPL', 3)
        self.assertAlmostEqual(self.account.get_portfolio_value(), 1000.0 - 3 * 150.0 + 3 * 150.0)

    def test_calculate_profit_loss(self):
        initial_deposit = 1000.0
        self.account.buy_shares('AAPL', 3)
        profit_loss = self.account.calculate_profit_loss(initial_deposit)
        self.assertAlmostEqual(profit_loss, 0.0, places=2)  # No profit/loss yet

    def test_list_transactions(self):
        self.account.deposit(500.0)
        self.account.withdraw(200.0)
        transactions = self.account.list_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertIn('Deposited: $500.00', transactions)
        self.assertIn('Withdrew: $200.00', transactions)

if __name__ == '__main__':
    unittest.main()