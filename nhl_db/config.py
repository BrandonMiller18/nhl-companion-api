import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env from API service root directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

RECORDS_BASE = "https://records.nhl.com/site/api"
NHL_WEB_BASE = "https://api-web.nhle.com/v1"


def get_env(name: str, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


