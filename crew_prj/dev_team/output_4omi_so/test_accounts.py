import unittest
from unittest.mock import patch
from accounts import Transaction, Account, get_share_price


class TestGetSharePrice(unittest.TestCase):
    """Test cases for the get_share_price function."""
    
    def test_get_share_price_aapl(self):
        """Test getting price for AAPL."""
        self.assertEqual(get_share_price('AAPL'), 150.00)
    
    def test_get_share_price_tsla(self):
        """Test getting price for TSLA."""
        self.assertEqual(get_share_price('TSLA'), 700.00)
    
    def test_get_share_price_googl(self):
        """Test getting price for GOOGL."""
        self.assertEqual(get_share_price('GOOGL'), 2800.00)
    
    def test_get_share_price_unknown(self):
        """Test getting price for unknown symbol."""
        self.assertEqual(get_share_price('UNKNOWN'), 0.0)


class TestTransaction(unittest.TestCase):
    """Test cases for the Transaction class."""
    
    def test_transaction_initialization(self):
        """Test transaction is initialized correctly."""
        trans = Transaction('AAPL', 10, 'buy', 150.00)
        self.assertEqual(trans.symbol, 'AAPL')
        self.assertEqual(trans.quantity, 10)
        self.assertEqual(trans.transaction_type, 'buy')
        self.assertEqual(trans.price, 150.00)
        self.assertEqual(trans.total_value, 1500.00)
    
    def test_transaction_total_value_calculation(self):
        """Test total value is calculated correctly."""
        trans = Transaction('TSLA', 5, 'sell', 700.00)
        self.assertEqual(trans.total_value, 3500.00)


class TestAccount(unittest.TestCase):
    """Test cases for the Account class."""
    
    def setUp(self):
        """Set up test account before each test."""
        self.account = Account('TestUser', 10000.00)
    
    def test_account_initialization(self):
        """Test account is initialized correctly."""
        self.assertEqual(self.account.user_name, 'TestUser')
        self.assertEqual(self.account.initial_deposit, 10000.00)
        self.assertEqual(self.account.balance, 10000.00)
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(self.account.transactions, [])
    
    def test_deposit(self):
        """Test depositing funds."""
        self.account.deposit(5000.00)
        self.assertEqual(self.account.balance, 15000.00)
    
    def test_deposit_multiple_times(self):
        """Test multiple deposits."""
        self.account.deposit(1000.00)
        self.account.deposit(2000.00)
        self.assertEqual(self.account.balance, 13000.00)
    
    def test_withdraw_success(self):
        """Test successful withdrawal."""
        self.account.withdraw(3000.00)
        self.assertEqual(self.account.balance, 7000.00)
    
    def test_withdraw_exact_balance(self):
        """Test withdrawing exact balance."""
        self.account.withdraw(10000.00)
        self.assertEqual(self.account.balance, 0.00)
    
    def test_withdraw_insufficient_funds(self):
        """Test withdrawal with insufficient funds raises error."""
        with self.assertRaises(ValueError) as context:
            self.account.withdraw(15000.00)
        self.assertIn('negative balance', str(context.exception))
    
    def test_buy_shares_success(self):
        """Test successful share purchase."""
        self.account.buy_shares('AAPL', 10)
        self.assertEqual(self.account.balance, 8500.00)  # 10000 - (150 * 10)
        self.assertEqual(self.account.holdings['AAPL'], 10)
        self.assertEqual(len(self.account.transactions), 1)
    
    def test_buy_shares_multiple_times_same_symbol(self):
        """Test buying same symbol multiple times."""
        self.account.buy_shares('AAPL', 5)
        self.account.buy_shares('AAPL', 3)
        self.assertEqual(self.account.holdings['AAPL'], 8)
        self.assertEqual(len(self.account.transactions), 2)
    
    def test_buy_shares_different_symbols(self):
        """Test buying different symbols."""
        self.account.buy_shares('AAPL', 5)
        self.account.buy_shares('TSLA', 2)
        self.assertEqual(self.account.holdings['AAPL'], 5)
        self.assertEqual(self.account.holdings['TSLA'], 2)
    
    def test_buy_shares_insufficient_funds(self):
        """Test buying shares with insufficient funds."""
        with self.assertRaises(ValueError) as context:
            self.account.buy_shares('GOOGL', 10)  # 2800 * 10 = 28000 > 10000
        self.assertIn('Insufficient funds', str(context.exception))
        self.assertEqual(self.account.balance, 10000.00)  # Balance unchanged
        self.assertEqual(self.account.holdings, {})  # No holdings added
    
    def test_sell_shares_success(self):
        """Test successful share sale."""
        self.account.buy_shares('AAPL', 10)
        initial_balance = self.account.balance
        self.account.sell_shares('AAPL', 5)
        self.assertEqual(self.account.balance, initial_balance + 750.00)  # 150 * 5
        self.assertEqual(self.account.holdings['AAPL'], 5)
    
    def test_sell_all_shares(self):
        """Test selling all shares of a symbol."""
        self.account.buy_shares('AAPL', 10)
        self.account.sell_shares('AAPL', 10)
        self.assertEqual(self.account.holdings['AAPL'], 0)
    
    def test_sell_shares_not_owned(self):
        """Test selling shares not owned raises error."""
        with self.assertRaises(ValueError) as context:
            self.account.sell_shares('AAPL', 5)
        self.assertIn('Not enough shares', str(context.exception))
    
    def test_sell_shares_insufficient_quantity(self):
        """Test selling more shares than owned."""
        self.account.buy_shares('AAPL', 5)
        with self.assertRaises(ValueError) as context:
            self.account.sell_shares('AAPL', 10)
        self.assertIn('Not enough shares', str(context.exception))
    
    def test_get_portfolio_value_no_holdings(self):
        """Test portfolio value with no holdings."""
        self.assertEqual(self.account.get_portfolio_value(), 10000.00)
    
    def test_get_portfolio_value_with_holdings(self):
        """Test portfolio value with holdings."""
        self.account.buy_shares('AAPL', 10)  # Cost: 1500, Balance: 8500
        self.account.buy_shares('TSLA', 2)   # Cost: 1400, Balance: 7100
        # Portfolio = Balance + (AAPL holdings * price) + (TSLA holdings * price)
        # Portfolio = 7100 + (10 * 150) + (2 * 700) = 7100 + 1500 + 1400 = 10000
        self.assertEqual(self.account.get_portfolio_value(), 10000.00)
    
    def test_get_portfolio_value_after_transactions(self):
        """Test portfolio value after buy and sell transactions."""
        self.account.buy_shares('AAPL', 20)  # Cost: 3000, Balance: 7000
        self.account.sell_shares('AAPL', 10)  # Gain: 1500, Balance: 8500
        # Portfolio = 8500 + (10 * 150) = 10000
        self.assertEqual(self.account.get_portfolio_value(), 10000.00)
    
    def test_get_profit_loss_no_change(self):
        """Test profit/loss with no change."""
        self.assertEqual(self.account.get_profit_loss(), 0.00)
    
    def test_get_profit_loss_after_deposit(self):
        """Test profit/loss after deposit."""
        self.account.deposit(5000.00)
        self.assertEqual(self.account.get_profit_loss(), 5000.00)
    
    def test_get_profit_loss_after_withdrawal(self):
        """Test profit/loss after withdrawal."""
        self.account.withdraw(2000.00)
        self.assertEqual(self.account.get_profit_loss(), -2000.00)
    
    def test_get_profit_loss_with_trading(self):
        """Test profit/loss remains same after buying and holding."""
        self.account.buy_shares('AAPL', 10)
        # Value is same: cash reduced but holdings increased by same amount
        self.assertEqual(self.account.get_profit_loss(), 0.00)
    
    def test_list_holdings_empty(self):
        """Test listing holdings when empty."""
        holdings = self.account.list_holdings()
        self.assertEqual(holdings, {})
    
    def test_list_holdings_with_shares(self):
        """Test listing holdings with shares."""
        self.account.buy_shares('AAPL', 10)
        self.account.buy_shares('TSLA', 5)
        holdings = self.account.list_holdings()
        self.assertEqual(holdings, {'AAPL': 10, 'TSLA': 5})
    
    def test_list_holdings_returns_copy(self):
        """Test that list_holdings returns a copy, not reference."""
        self.account.buy_shares('AAPL', 10)
        holdings = self.account.list_holdings()
        holdings['AAPL'] = 999  # Modify the returned dict
        # Original holdings should be unchanged
        self.assertEqual(self.account.holdings['AAPL'], 10)
    
    def test_list_transactions_empty(self):
        """Test listing transactions when empty."""
        transactions = self.account.list_transactions()
        self.assertEqual(transactions, [])
    
    def test_list_transactions_with_buys(self):
        """Test listing buy transactions."""
        self.account.buy_shares('AAPL', 10)
        self.account.buy_shares('TSLA', 5)
        transactions = self.account.list_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0], ('buy', 'AAPL', 10, 150.00))
        self.assertEqual(transactions[1], ('buy', 'TSLA', 5, 700.00))
    
    def test_list_transactions_with_buys_and_sells(self):
        """Test listing mixed transactions."""
        self.account.buy_shares('AAPL', 10)
        self.account.sell_shares('AAPL', 5)
        transactions = self.account.list_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0], ('buy', 'AAPL', 10, 150.00))
        self.assertEqual(transactions[1], ('sell', 'AAPL', 5, 150.00))
    
    def test_transaction_order_preserved(self):
        """Test that transaction order is preserved."""
        self.account.buy_shares('AAPL', 5)
        self.account.buy_shares('TSLA', 3)
        self.account.sell_shares('AAPL', 2)
        self.account.buy_shares('GOOGL', 1)
        transactions = self.account.list_transactions()
        self.assertEqual(transactions[0][1], 'AAPL')
        self.assertEqual(transactions[1][1], 'TSLA')
        self.assertEqual(transactions[2][1], 'AAPL')
        self.assertEqual(transactions[3][1], 'GOOGL')


if __name__ == '__main__':
    unittest.main()