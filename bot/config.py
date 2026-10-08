import os
from dataclasses import dataclass
from typing import Set


def _csv_ints(value: str) -> Set[int]:
    result: Set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if item:
            result.add(int(item))
    return result


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    allowed_user_ids: Set[int]
    binance_api_key: str
    binance_api_secret: str
    binance_testnet: bool
    trading_enabled: bool
    poll_interval_seconds: int


def load_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    return Settings(
        telegram_token=token,
        allowed_user_ids=_csv_ints(os.getenv("TELEGRAM_ALLOWED_USER_IDS", "")),
        binance_api_key=os.getenv("BINANCE_API_KEY", "").strip(),
        binance_api_secret=os.getenv("BINANCE_API_SECRET", "").strip(),
        binance_testnet=os.getenv("BINANCE_TESTNET", "true").lower() == "true",
        trading_enabled=os.getenv("TRADING_ENABLED", "false").lower() == "true",
        poll_interval_seconds=int(os.getenv("POLL_INTERVAL_SECONDS", "2")),
    )
