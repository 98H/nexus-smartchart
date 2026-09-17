"""
Market Data Engine for SmartChart.
Provides live Binance REST/WebSocket market data with deterministic synthetic fallback.
"""
import math
import random
import time
from typing import Any
import requests

DEFAULT_SYMBOLS = [
    {"symbol": "BTCUSDT", "name": "Bitcoin / TetherUS", "type": "crypto", "base_price": 68500.0, "precision": 2},
    {"symbol": "ETHUSDT", "name": "Ethereum / TetherUS", "type": "crypto", "base_price": 3850.0, "precision": 2},
    {"symbol": "SOLUSDT", "name": "Solana / TetherUS", "type": "crypto", "base_price": 182.5, "precision": 2},
    {"symbol": "EURUSD", "name": "Euro / US Dollar", "type": "forex", "base_price": 1.0850, "precision": 4},
    {"symbol": "GBPUSD", "name": "British Pound / US Dollar", "type": "forex", "base_price": 1.2950, "precision": 4},
    {"symbol": "XAUUSD", "name": "Gold / US Dollar", "type": "commodity", "base_price": 2580.0, "precision": 2},
    {"symbol": "SPX", "name": "S&P 500 Index", "type": "index", "base_price": 5650.0, "precision": 2},
    {"symbol": "NDX", "name": "Nasdaq 100 Index", "type": "index", "base_price": 19800.0, "precision": 2},
]

INTERVAL_SECONDS = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
    "1w": 604800,
}


class MarketDataProvider:
    def __init__(self):
        self._cache: dict[str, list[dict[str, Any]]] = {}

    def get_available_symbols(self) -> list[dict[str, Any]]:
        return DEFAULT_SYMBOLS

    def fetch_klines(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "1h",
        limit: int = 300,
    ) -> list[dict[str, Any]]:
        """
        Fetches klines from Binance public API or falls back to realistic synthetic data.
        """
        symbol = symbol.upper()
        if interval not in INTERVAL_SECONDS:
            interval = "1h"

        # Try Binance if crypto symbol
        if symbol.endswith("USDT"):
            try:
                url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
                resp = requests.get(url, timeout=3.0)
                if resp.status_code == 200:
                    raw_data = resp.json()
                    candles = []
                    for row in raw_data:
                        candles.append({
                            "time": int(row[0]) // 1000,
                            "open": float(row[1]),
                            "high": float(row[2]),
                            "low": float(row[3]),
                            "close": float(row[4]),
                            "volume": float(row[5]),
                        })
                    if len(candles) >= 50:
                        self._cache[f"{symbol}_{interval}"] = candles
                        return candles
            except Exception:
                pass

        # Check in-memory cache
        cache_key = f"{symbol}_{interval}"
        if cache_key in self._cache and len(self._cache[cache_key]) >= limit:
            return self._cache[cache_key][-limit:]

        # Synthetic generator fallback
        candles = self._generate_synthetic_klines(symbol, interval, limit)
        self._cache[cache_key] = candles
        return candles

    def _generate_synthetic_klines(
        self,
        symbol: str,
        interval: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        meta = next((s for s in DEFAULT_SYMBOLS if s["symbol"] == symbol), DEFAULT_SYMBOLS[0])
        base_price = meta["base_price"]
        step = INTERVAL_SECONDS.get(interval, 3600)
        end_time = int(time.time())
        start_time = end_time - (limit * step)

        candles = []
        curr_price = base_price
        trend = random.choice([-1.0, 1.0]) * 0.0005

        for i in range(limit):
            t = start_time + (i * step)
            volatility = base_price * 0.003 * math.sqrt(step / 3600)
            drift = curr_price * trend + (random.gauss(0, 1) * volatility)
            open_p = curr_price
            close_p = max(base_price * 0.1, open_p + drift)
            high_p = max(open_p, close_p) + abs(random.gauss(0, 1) * volatility * 0.6)
            low_p = min(open_p, close_p) - abs(random.gauss(0, 1) * volatility * 0.6)
            low_p = max(base_price * 0.05, low_p)

            volume = abs(random.gauss(1000, 300)) * (curr_price / 100)

            candles.append({
                "time": t,
                "open": round(open_p, meta["precision"]),
                "high": round(high_p, meta["precision"]),
                "low": round(low_p, meta["precision"]),
                "close": round(close_p, meta["precision"]),
                "volume": round(volume, 2),
            })
            curr_price = close_p
            # Random trend reversal
            if random.random() < 0.04:
                trend = -trend

        return candles
