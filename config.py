import os
from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Environment variable '{name}' is missing")
    return value


BOT_TOKEN = _require_env("BOT_TOKEN")
GOOGLE_SCRIPT_URL = _require_env("GOOGLE_SCRIPT_URL")
API_KEY = _require_env("API_KEY")
SUPER_ADMIN_ID = int(_require_env("SUPER_ADMIN_ID"))
ADMIN_LOG_CHAT_ID = int(_require_env("ADMIN_LOG_CHAT_ID"))
