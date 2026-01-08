from typing import Any, Dict, Optional


def ok(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response: Dict[str, Any] = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return response


def error(message: str, error_code: Optional[str] = None) -> Dict[str, Any]:
    response: Dict[str, Any] = {"success": False, "message": message}
    if error_code is not None:
        response["error"] = error_code
    return response
