"""
Tests for Market Data Engine in SmartChart.
"""
from src.market_data import MarketDataProvider, DEFAULT_SYMBOLS


def test_symbols_list():
    provider = MarketDataProvider()
    symbols = provider.get_available_symbols()
    assert len(symbols) >= 5
    tickers = [s["symbol"] for s in symbols]
    assert "BTCUSDT" in tickers
    assert "ETHUSDT" in tickers


def test_synthetic_klines_generation():
    provider = MarketDataProvider()
    candles = provider.fetch_klines(symbol="BTCUSDT", interval="1h", limit=50)
    assert len(candles) == 50
    for c in candles:
        assert "open" in c
        assert "high" in c
        assert "low" in c
        assert "close" in c
        assert "volume" in c
        assert c["high"] >= max(c["open"], c["close"])
        assert c["low"] <= min(c["open"], c["close"])
