"""Read local configuration without exposing secrets to the launcher."""

import os
import re
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
BOT_NAME = "elevenlabs demo"
load_dotenv(ROOT / ".env")


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Set {name} in .env before starting the demo.")
    return value


def tools_origin() -> str:
    value = require_env("ELEVENLABS_TOOLS_ORIGIN").rstrip("/")
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or parsed.path or parsed.query or parsed.fragment):
        raise ValueError("ELEVENLABS_TOOLS_ORIGIN must be a public HTTPS origin without a path.")
    return value


def agent_id() -> str:
    value = require_env("ELEVENLABS_AGENT_ID")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,256}", value):
        raise ValueError("ELEVENLABS_AGENT_ID must be the agent ID from ElevenLabs.")
    return value


def session_timeout() -> int:
    try:
        value = int(os.getenv("SESSION_TIMEOUT_SECONDS", "600"))
        if 60 <= value <= 3600:
            return value
    except ValueError:
        pass
    raise ValueError("SESSION_TIMEOUT_SECONDS must be between 60 and 3600.")


def validate_runtime_settings() -> None:
    require_env("RECALL_API_KEY")
    require_env("RECALL_API_BASE_URL")
    agent_id()
    tools_origin()
    session_timeout()
