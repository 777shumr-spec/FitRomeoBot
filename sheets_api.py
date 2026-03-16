import requests
from typing import Any, Dict, Optional

from config import GOOGLE_SCRIPT_URL, API_KEY


class SheetsAPIError(Exception):
    pass


def _post(action: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = {
        "key": API_KEY,
        "action": action,
        "data": data or {}
    }

    try:
        response = requests.post(
            GOOGLE_SCRIPT_URL,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise SheetsAPIError(f"HTTP error while calling Apps Script: {e}") from e

    try:
        result = response.json()
    except ValueError as e:
        raise SheetsAPIError(f"Invalid JSON response: {response.text}") from e

    if not result.get("ok"):
        raise SheetsAPIError(result.get("error", "Unknown Apps Script error"))

    return result


def ping() -> Dict[str, Any]:
    return _post("ping")


def get_settings() -> Dict[str, Any]:
    return _post("get_settings")


def upsert_user(
    telegram_id: int,
    username: str = "",
    first_name: str = "",
    last_name: str = "",
    notes: str = ""
) -> Dict[str, Any]:
    return _post("upsert_user", {
        "telegram_id": str(telegram_id),
        "username": username or "",
        "first_name": first_name or "",
        "last_name": last_name or "",
        "notes": notes or ""
    })


def create_access_request(
    telegram_id: int,
    username: str = "",
    first_name: str = "",
    last_name: str = ""
) -> Dict[str, Any]:
    return _post("create_access_request", {
        "telegram_id": str(telegram_id),
        "username": username or "",
        "first_name": first_name or "",
        "last_name": last_name or ""
    })


def get_user_status(telegram_id: int) -> Dict[str, Any]:
    return _post("get_user_status", {
        "telegram_id": str(telegram_id)
    })


def get_allowed_groups(telegram_id: int) -> Dict[str, Any]:
    return _post("get_allowed_groups", {
        "telegram_id": str(telegram_id)
    })


def get_subgroups_by_group(group_id: str) -> Dict[str, Any]:
    return _post("get_subgroups_by_group", {
        "group_id": group_id
    })


def get_videos_by_subgroup(subgroup_id: str) -> Dict[str, Any]:
    return _post("get_videos_by_subgroup", {
        "subgroup_id": subgroup_id
    })


def write_log(
    telegram_id: int,
    username: str,
    group_id: str,
    subgroup_id: str,
    video_id: str,
    action: str
) -> Dict[str, Any]:
    return _post("write_log", {
        "telegram_id": str(telegram_id),
        "username": username or "",
        "group_id": group_id or "",
        "subgroup_id": subgroup_id or "",
        "video_id": video_id or "",
        "action": action
    })


def set_user_status(
    telegram_id: int,
    status: str,
    access_mode: str = "",
    processed_by: str = ""
) -> Dict[str, Any]:
    return _post("set_user_status", {
        "telegram_id": str(telegram_id),
        "status": status,
        "access_mode": access_mode,
        "processed_by": processed_by
    })


def list_users() -> Dict[str, Any]:
    return _post("list_users")


def list_pending_requests() -> Dict[str, Any]:
    return _post("list_pending_requests")
