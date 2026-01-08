import unittest

from fastapi.testclient import TestClient

from api import build_app


class TestAPI(unittest.TestCase):
    def setUp(self) -> None:
        app = build_app(mount_gradio=False)
        self.client = TestClient(app)

    def test_create_account_and_status(self) -> None:
        response = self.client.post(
            "/api/account",
            json={"username": "alice", "initial_deposit": 1000},
        )
        payload = response.json()
        self.assertTrue(payload["success"])
        token = payload["data"]["token"]

        status_response = self.client.get(
            "/api/status",
            headers={"X-Session-Token": token},
        )
        status_payload = status_response.json()
        self.assertTrue(status_payload["success"])
        self.assertEqual(status_payload["data"]["account"]["username"], "alice")

    def test_deposit_requires_session(self) -> None:
        response = self.client.post("/api/deposit", json={"amount": 100})
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"], "invalid_session")

    def test_buy_unknown_symbol(self) -> None:
        response = self.client.post(
            "/api/account",
            json={"username": "bob", "initial_deposit": 1000},
        )
        payload = response.json()
        token = payload["data"]["token"]

        trade_response = self.client.post(
            "/api/trade/buy",
            json={"symbol": "BAD", "quantity": 1},
            headers={"X-Session-Token": token},
        )
        trade_payload = trade_response.json()
        self.assertFalse(trade_payload["success"])
        self.assertEqual(trade_payload["error"], "unknown_symbol")


if __name__ == "__main__":
    unittest.main()
