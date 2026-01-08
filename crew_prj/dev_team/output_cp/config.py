import os
from typing import List, Optional


DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
DEFAULT_SESSION_TTL_SECONDS = 3600
DEFAULT_SERVER_HOST = "127.0.0.1"
DEFAULT_SERVER_PORT = 8000


def get_cors_origins() -> List[str]:
    raw = os.getenv("CORS_ORIGINS", "")
    if not raw:
        return DEFAULT_CORS_ORIGINS
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or DEFAULT_CORS_ORIGINS


def get_session_ttl_seconds() -> Optional[int]:
    raw = os.getenv("SESSION_TTL_SECONDS", "").strip()
    if not raw:
        return DEFAULT_SESSION_TTL_SECONDS
    if raw.lower() in {"none", "null", "disable", "disabled"}:
        return None
    try:
        return int(raw)
    except ValueError:
        return DEFAULT_SESSION_TTL_SECONDS


def get_server_host() -> str:
    return os.getenv("SERVER_HOST", DEFAULT_SERVER_HOST)


def get_server_port() -> int:
    raw = os.getenv("SERVER_PORT", "").strip()
    if not raw:
        return DEFAULT_SERVER_PORT
    try:
        return int(raw)
    except ValueError:
        return DEFAULT_SERVER_PORT


def get_server_reload() -> bool:
    raw = os.getenv("SERVER_RELOAD", "").strip().lower()
    if not raw:
        return False
    return raw in {"1", "true", "yes", "on"}
