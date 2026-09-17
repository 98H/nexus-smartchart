"""
Tests for Pine Script v5/v6 Execution Engine in SmartChart.
"""
from src.pine_engine import PineScriptEngine


def test_pine_script_indicator_execution():
    engine = PineScriptEngine()
    code = """//@version=5
indicator("My SMA Indicator", overlay=true)
fast = ta.sma(close, 5)
plot(fast, title="Fast SMA", color=color.blue)
"""
    candles = [
        {"time": 1000 + i, "open": 100 + i, "high": 105 + i, "low": 95 + i, "close": 101 + i, "volume": 500}
        for i in range(20)
    ]

    result = engine.execute(code, candles)
    assert result["version"] == 5
    assert len(result["plots"]) == 1
    assert result["plots"][0]["title"] == "Fast SMA"
    assert len(result["plots"][0]["values"]) == 20


def test_pine_script_strategy_backtest():
    engine = PineScriptEngine()
    code = """//@version=5
strategy("Cross Strategy", overlay=true)
fast = ta.ema(close, 9)
slow = ta.ema(close, 21)
plot(fast)
"""
    candles = [
        {"time": 1000 + i, "open": 100 + (i % 10), "high": 110, "low": 90, "close": 102 + (i % 10), "volume": 1000}
        for i in range(50)
    ]

    result = engine.execute(code, candles)
    assert result["strategy_stats"] is not None
    assert "net_profit" in result["strategy_stats"]
    assert "win_rate_pct" in result["strategy_stats"]
    assert "profit_factor" in result["strategy_stats"]
