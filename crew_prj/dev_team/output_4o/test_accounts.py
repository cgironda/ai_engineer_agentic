import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from accounts import Account, get_share_price


def fixed_clock():
    return datetime(2024, 1, 1, tzinfo=timezone.utc)


class AccountTests(unittest.TestCase):
    def setUp(self) -> None:
        self.account = Account("alice", 1000.0, clock=fixed_clock)

    def test_deposit_increases_balance_and_records_transaction(self):
        txn = self.account.deposit(250.0)
        self.assertEqual(self.account.balance, 1250.0)
        self.assertEqual(txn.type, "deposit")
        self.assertEqual(len(self.account.transactions), 2)  # initial + new

    def test_withdraw_fails_on_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(5000.0)

    def test_buy_and_sell_round_trip(self):
        buy_txn = self.account.buy_shares("AAPL", 2, get_share_price)
        self.assertEqual(buy_txn.type, "buy")
        self.assertEqual(self.account.holdings["AAPL"], 2)
        sell_txn = self.account.sell_shares("AAPL", 1, get_share_price)
        self.assertEqual(sell_txn.type, "sell")
        self.assertEqual(self.account.holdings["AAPL"], 1)

    def test_profit_or_loss_calculation(self):
        self.account.buy_shares("AAPL", 1, get_share_price)  # spend 150
        self.account.sell_shares("AAPL", 1, get_share_price)  # receive 150
        pnl = self.account.calculate_profit_or_loss(get_share_price)
        self.assertEqual(pnl, 0.0)

    def test_holdings_report_is_copy(self):
        holdings = self.account.report_holdings()
        holdings["MISMATCH"] = 100
        self.assertNotIn("MISMATCH", self.account.holdings)


if __name__ == "__main__":
    unittest.main()
