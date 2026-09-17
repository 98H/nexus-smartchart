"""
Tests for Indicator Library in SmartChart.
"""
from src.indicators import IndicatorEngine


def test_moving_averages_and_rsi():
    # Construct 30 dummy candles
    candles = [{"open": 100.0 + i, "high": 105.0 + i, "low": 98.0 + i, "close": 102.0 + i, "volume": 1000} for i in range(30)]

    sma = IndicatorEngine.sma(candles, period=14)
    assert len(sma) == 30
    assert sma[0] is None
    assert sma[13] is not None
    assert isinstance(sma[13], float)

    ema = IndicatorEngine.ema(candles, period=14)
    assert len(ema) == 30
    assert ema[13] is not None

    rsi = IndicatorEngine.rsi(candles, period=14)
    assert len(rsi) == 30
    assert rsi[14] is not None
    last_rsi = rsi[-1]
    assert last_rsi is not None and 0 <= last_rsi <= 100


def test_macd_and_bollinger():
    candles = [{"open": 100.0 + (i % 5), "high": 106.0, "low": 97.0, "close": 101.0 + (i % 3), "volume": 1000} for i in range(40)]

    macd_res = IndicatorEngine.macd(candles)
    assert "macd" in macd_res
    assert "signal" in macd_res
    assert "histogram" in macd_res

    bb_res = IndicatorEngine.bollinger_bands(candles, period=20)
    assert "upper" in bb_res
    assert "middle" in bb_res
    assert "lower" in bb_res


def test_luxalgo_suite():
    candles = []
    # Up wave followed by down wave
    for i in range(35):
        p = 100.0 + (i * 2.0 if i < 20 else (40 - i) * 2.0)
        candles.append({
            "time": 1700000000 + (i * 3600),
            "open": p - 1.0,
            "high": p + 2.0,
            "low": p - 2.0,
            "close": p,
            "volume": 2500,
        })

    sig_res = IndicatorEngine.luxalgo_signals_and_overlays(candles)
    assert "signals" in sig_res
    assert "fast_ribbon" in sig_res

    smc_res = IndicatorEngine.smart_money_concepts(candles)
    assert "order_blocks" in smc_res
    assert "fair_value_gaps" in smc_res
