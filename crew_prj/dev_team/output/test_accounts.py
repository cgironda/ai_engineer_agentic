import unittest
from unittest.mock import Mock

from crew_prj.dev_team.output.accounts import Account

# Assume Account class is imported from accounts module
# from accounts import Account

class TestAccount(unittest.TestCase):
    def setUp(self):
        self.initial_deposit = 1000.0
        self.account = Account('test_user', self.initial_deposit)
        self.mock_price_getter = Mock()
        self.mock_price_getter.side_effect = lambda symbol: {'AAPL': 150.0, 'TSLA': 700.0, 'GOOGL': 2800.0}.get(symbol, 0.0)

    def test_deposit(self):
        self.account.deposit(500)
        self.assertEqual(self.account.balance, 1500)

    def test_withdraw_success(self):
        result = self.account.withdraw(500)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 500)

    def test_withdraw_failure(self):
        result = self.account.withdraw(1500)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 1000)

    def test_buy_shares_success(self):
        result = self.account.buy_shares('AAPL', 5, self.mock_price_getter)
        self.assertTrue(result)
        self.assertEqual(self.account.holdings['AAPL'], 5)

    def test_buy_shares_failure(self):
        result = self.account.buy_shares('GOOGL', 1, self.mock_price_getter)
        self.assertFalse(result)
        self.assertNotIn('GOOGL', self.account.holdings)

    def test_sell_shares_success(self):
        self.account.buy_shares('AAPL', 5, self.mock_price_getter)
        result = self.account.sell_shares('AAPL', 5, self.mock_price_getter)
        self.assertTrue(result)
        self.assertEqual(self.account.holdings['AAPL'], 0)

    def test_sell_shares_failure(self):
        result = self.account.sell_shares('TSLA', 1, self.mock_price_getter)
        self.assertFalse(result)

    def test_calculate_portfolio_value(self):
        self.account.buy_shares('AAPL', 5, self.mock_price_getter)
        total_value = self.account.calculate_portfolio_value(self.mock_price_getter)
        self.assertEqual(total_value, self.account.balance + 750.0)

    def test_calculate_profit_or_loss(self):
        self.account.buy_shares('AAPL', 5, self.mock_price_getter)
        profit_or_loss = self.account.calculate_profit_or_loss(self.mock_price_getter)
        expected_profit = 750.0 - self.initial_deposit
        self.assertEqual(profit_or_loss, expected_profit)

    def test_report_holdings(self):
        self.account.buy_shares('AAPL', 5, self.mock_price_getter)
        self.assertEqual(self.account.report_holdings(), {'AAPL': 5})

    def test_report_profit_or_loss(self):
        self.account.buy_shares('AAPL', 5, self.mock_price_getter)
        profit_or_loss = self.account.report_profit_or_loss(self.mock_price_getter)
        expected_profit = 750.0 - self.initial_deposit
        self.assertEqual(profit_or_loss, expected_profit)

    def test_list_transactions(self):
        self.account.buy_shares('AAPL', 5, self.mock_price_getter)
        self.assertEqual(self.account.list_transactions(), [('buy', 'AAPL', 5, 150.0)])

if __name__ == '__main__':
    unittest.main()