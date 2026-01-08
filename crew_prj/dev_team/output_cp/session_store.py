from __future__ import annotations

from dataclasses import dataclass
import secrets
import time
from typing import Dict, Optional

from accounts import Account


@dataclass
class Session:
    account: Account
    created_at: float
    last_access: float


class SessionStore:
    def __init__(self, ttl_seconds: Optional[int] = None) -> None:
        self._sessions: Dict[str, Session] = {}
        self._ttl_seconds = ttl_seconds

    def create_session(self, account: Account) -> str:
        token = secrets.token_urlsafe(24)
        now = time.time()
        self._sessions[token] = Session(account=account, created_at=now, last_access=now)
        return token

    def get_account(self, token: str) -> Optional[Account]:
        session = self._sessions.get(token)
        if session is None:
            return None
        if self._ttl_seconds is not None and time.time() - session.last_access > self._ttl_seconds:
            del self._sessions[token]
            return None
        session.last_access = time.time()
        return session.account

    def delete_session(self, token: str) -> None:
        self._sessions.pop(token, None)
