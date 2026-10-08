import hashlib
import hmac
import time
from typing import Any, Dict, List

import requests


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = (
            "https://testnet.binance.vision"
            if testnet
            else "https://api.binance.com"
        )
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.api_secret)

    def _signed_get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.configured:
            raise RuntimeError("Binance API credentials are not configured")

        params = dict(params or {})
        params["timestamp"] = int(time.time() * 1000)
        query = "&".join(f"{key}={params[key]}" for key in params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature

        response = self.session.get(
            f"{self.base_url}{path}",
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def ping(self) -> bool:
        response = self.session.get(f"{self.base_url}/api/v3/ping", timeout=10)
        response.raise_for_status()
        return True

    def account(self) -> Dict[str, Any]:
        return self._signed_get("/api/v3/account")

    def non_zero_balances(self) -> List[Dict[str, str]]:
        account = self.account()
        return [
            {
                "asset": item["asset"],
                "free": item["free"],
                "locked": item["locked"],
            }
            for item in account.get("balances", [])
            if float(item["free"]) != 0.0 or float(item["locked"]) != 0.0
        ]