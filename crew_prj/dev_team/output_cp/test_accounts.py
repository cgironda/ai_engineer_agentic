import unittest

from accounts import Account, get_share_price


class TestAccount(unittest.TestCase):
    """Unit tests for the account management backend."""

    def setUp(self) -> None:
        self.account = Account("test_user", 1000.0)

    def test_initialization(self) -> None:
        self.assertEqual(self.account.username, "test_user")
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(self.account.portfolio, {})
        self.assertEqual(self.account.transactions, [])

    def test_deposit(self) -> None:
        self.account.deposit(500)
        self.assertEqual(self.account.balance, 1500.0)
        self.assertIn("Deposited: 500", self.account.transactions)

        with self.assertRaises(ValueError):
            self.account.deposit(-100)

    def test_withdraw(self) -> None:
        self.account.withdraw(200)
        self.assertEqual(self.account.balance, 800.0)
        self.assertIn("Withdrew: 200", self.account.transactions)

        with self.assertRaises(ValueError):
            self.account.withdraw(900)

        with self.assertRaises(ValueError):
            self.account.withdraw(-50)

    def test_buy_shares(self) -> None:
        self.account.buy_shares("AAPL", 3)
        self.assertEqual(self.account.balance, 1000.0 - (150.0 * 3))
        self.assertEqual(self.account.portfolio["AAPL"], 3)
        self.assertIn("Bought: 3 shares of AAPL at 150.0 each", self.account.transactions)

        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", 100)

        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", -1)

    def test_sell_shares(self) -> None:
        self.account.buy_shares("AAPL", 3)
        self.account.sell_shares("AAPL", 2)
        self.assertEqual(self.account.portfolio["AAPL"], 1)

        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", 2)

        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", -1)

    def test_calculate_portfolio_value(self) -> None:
        self.account.buy_shares("AAPL", 3)
        expected_value = 1000.0 - (150.0 * 3) + (150.0 * 3)
        self.assertEqual(self.account.calculate_portfolio_value(), expected_value)

    def test_profit_loss(self) -> None:
        self.assertEqual(self.account.calculate_profit_loss(), 0.0)
        self.account.deposit(500)
        self.assertGreater(self.account.calculate_profit_loss(), 0.0)

    def test_report_holdings(self) -> None:
        self.account.buy_shares("AAPL", 3)
        self.assertEqual(self.account.report_holdings(), {"AAPL": 3})

    def test_report_transactions(self) -> None:
        self.account.deposit(100)
        self.assertIn("Deposited: 100", self.account.report_transactions())

    def test_get_share_price(self) -> None:
        for symbol, expected_price in (("AAPL", 150.0), ("TSLA", 700.0), ("GOOGL", 2800.0)):
            self.assertEqual(get_share_price(symbol), expected_price)


if __name__ == "__main__":
    unittest.main()
