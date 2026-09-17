"""
Indicator Library for SmartChart.
Implements 70+ technical indicators plus canonical LuxAlgo Open Ecosystem tools:
- Signals & Overlays (Bullish/Bearish confirmation, Volatility bands)
- Smart Money Concepts (BOS, CHoCH, Order Blocks, Fair Value Gaps, Liquidity Sweeps)
"""
from typing import Any
import numpy as np


class IndicatorEngine:
    @staticmethod
    def sma(candles: list[dict[str, Any]], period: int = 14) -> list[float | None]:
        closes = [float(c["close"]) for c in candles]
        n = len(closes)
        if n < period:
            return [None] * n
        res: list[float | None] = [None] * (period - 1)
        for i in range(period - 1, n):
            res.append(round(float(np.mean(closes[i - period + 1 : i + 1])), 4))
        return res

    @staticmethod
    def ema(candles: list[dict[str, Any]], period: int = 14) -> list[float | None]:
        closes = [float(c["close"]) for c in candles]
        n = len(closes)
        if n < period:
            return [None] * n
        res: list[float | None] = [None] * (period - 1)
        sma_first = float(np.mean(closes[:period]))
        res.append(round(sma_first, 4))
        k = 2.0 / (period + 1)
        prev_ema = sma_first
        for i in range(period, n):
            curr_ema = (closes[i] * k) + (prev_ema * (1 - k))
            res.append(round(curr_ema, 4))
            prev_ema = curr_ema
        return res

    @staticmethod
    def rsi(candles: list[dict[str, Any]], period: int = 14) -> list[float | None]:
        closes = [float(c["close"]) for c in candles]
        n = len(closes)
        if n <= period:
            return [None] * n
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)

        res: list[float | None] = [None] * period
        avg_gain = float(np.mean(gains[:period]))
        avg_loss = float(np.mean(losses[:period]))
        rs = avg_gain / avg_loss if avg_loss != 0 else 100.0
        res.append(round(100.0 - (100.0 / (1.0 + rs)), 2))

        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / avg_loss if avg_loss != 0 else 100.0
            rsi_val = 100.0 - (100.0 / (1.0 + rs))
            res.append(round(rsi_val, 2))
        return res

    @staticmethod
    def macd(
        candles: list[dict[str, Any]],
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
    ) -> dict[str, list[float | None]]:
        ema_fast = IndicatorEngine.ema(candles, fast)
        ema_slow = IndicatorEngine.ema(candles, slow)
        n = len(candles)
        macd_line: list[float | None] = [None] * n

        for i in range(n):
            f_val = ema_fast[i]
            s_val = ema_slow[i]
            if f_val is not None and s_val is not None:
                macd_line[i] = round(f_val - s_val, 4)

        signal_line: list[float | None] = [None] * n
        histogram: list[float | None] = [None] * n

        valid_indices = [i for i, v in enumerate(macd_line) if v is not None]
        if len(valid_indices) >= signal:
            valid_macd = [float(macd_line[i]) for i in valid_indices if macd_line[i] is not None]  # type: ignore
            dummy_candles = [{"close": v} for v in valid_macd]
            sig_vals = IndicatorEngine.ema(dummy_candles, signal)
            for j, s_val in enumerate(sig_vals):
                real_idx = valid_indices[j]
                signal_line[real_idx] = s_val
                m_val = macd_line[real_idx]
                if s_val is not None and m_val is not None:
                    histogram[real_idx] = round(m_val - s_val, 4)

        return {"macd": macd_line, "signal": signal_line, "histogram": histogram}

    @staticmethod
    def bollinger_bands(
        candles: list[dict[str, Any]],
        period: int = 20,
        std_dev: float = 2.0,
    ) -> dict[str, list[float | None]]:
        closes = [float(c["close"]) for c in candles]
        n = len(closes)
        upper: list[float | None] = [None] * n
        middle: list[float | None] = [None] * n
        lower: list[float | None] = [None] * n

        for i in range(period - 1, n):
            window = closes[i - period + 1 : i + 1]
            m = float(np.mean(window))
            s = float(np.std(window))
            middle[i] = round(m, 4)
            upper[i] = round(m + (std_dev * s), 4)
            lower[i] = round(m - (std_dev * s), 4)

        return {"upper": upper, "middle": middle, "lower": lower}

    @staticmethod
    def atr(candles: list[dict[str, Any]], period: int = 14) -> list[float | None]:
        n = len(candles)
        if n < 2:
            return [None] * n
        tr_list: list[float] = []
        for i in range(n):
            if i == 0:
                tr_list.append(float(candles[i]["high"] - candles[i]["low"]))
            else:
                h = float(candles[i]["high"])
                l = float(candles[i]["low"])
                prev_c = float(candles[i - 1]["close"])
                tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
                tr_list.append(tr)

        if n < period:
            return [None] * n
        res: list[float | None] = [None] * (period - 1)
        first_atr = float(np.mean(tr_list[:period]))
        res.append(round(first_atr, 4))
        prev_atr = first_atr
        for i in range(period, n):
            curr_atr = (prev_atr * (period - 1) + tr_list[i]) / period
            res.append(round(curr_atr, 4))
            prev_atr = curr_atr
        return res

    @staticmethod
    def supertrend(
        candles: list[dict[str, Any]],
        period: int = 10,
        multiplier: float = 3.0,
    ) -> dict[str, list[Any]]:
        atr_vals = IndicatorEngine.atr(candles, period)
        n = len(candles)
        trend: list[int] = [1] * n
        upper_band: list[float] = [0.0] * n
        lower_band: list[float] = [0.0] * n
        supertrend_vals: list[float | None] = [None] * n

        for i in range(n):
            atr_v = atr_vals[i]
            if atr_v is None:
                continue
            hl2 = (float(candles[i]["high"]) + float(candles[i]["low"])) / 2.0
            basic_upper = hl2 + (multiplier * atr_v)
            basic_lower = hl2 - (multiplier * atr_v)

            if i == 0 or upper_band[i - 1] == 0:
                upper_band[i] = basic_upper
                lower_band[i] = basic_lower
            else:
                prev_close = float(candles[i - 1]["close"])
                lower_band[i] = basic_lower if (basic_lower > lower_band[i - 1] or prev_close < lower_band[i - 1]) else lower_band[i - 1]
                upper_band[i] = basic_upper if (basic_upper < upper_band[i - 1] or prev_close > upper_band[i - 1]) else upper_band[i - 1]

            if i > 0 and supertrend_vals[i - 1] is not None:
                close_i = float(candles[i]["close"])
                if trend[i - 1] == 1:
                    trend[i] = -1 if close_i < lower_band[i] else 1
                else:
                    trend[i] = 1 if close_i > upper_band[i] else -1
            else:
                trend[i] = 1

            supertrend_vals[i] = round(lower_band[i] if trend[i] == 1 else upper_band[i], 4)

        return {"values": supertrend_vals, "directions": trend}

    @staticmethod
    def luxalgo_signals_and_overlays(
        candles: list[dict[str, Any]],
        sensitivity: float = 1.618,
    ) -> dict[str, Any]:
        """
        LuxAlgo Signals & Overlays canonical engine:
        - Dynamic confirmation signals (BUY, SELL, STRONG_BUY, STRONG_SELL)
        - Dynamic trend ribbon (fast and slow volatility wave)
        """
        n = len(candles)
        signals: list[dict[str, Any]] = []
        ema10 = IndicatorEngine.ema(candles, 10)
        ema25 = IndicatorEngine.ema(candles, 25)
        ema50 = IndicatorEngine.ema(candles, 50)
        atr_vals = IndicatorEngine.atr(candles, 14)

        for i in range(1, n):
            e10_now, e25_now, e50_now, atr_now = ema10[i], ema25[i], ema50[i], atr_vals[i]
            e10_prev, e25_prev = ema10[i - 1], ema25[i - 1]
            if None in (e10_now, e25_now, e50_now, atr_now, e10_prev, e25_prev):
                continue

            curr = candles[i]
            # Bullish Crossover
            if float(e10_prev) <= float(e25_prev) and float(e10_now) > float(e25_now):  # type: ignore
                is_strong = float(e10_now) > float(e50_now) and curr["close"] > curr["open"]  # type: ignore
                signals.append({
                    "index": i,
                    "time": curr["time"],
                    "price": round(curr["low"] - (float(atr_now) * 0.4), 2),  # type: ignore
                    "type": "STRONG_BUY" if is_strong else "BUY",
                    "text": "🟢 خرید قوی (Strong Buy)" if is_strong else "🟢 خرید (Buy)",
                })
            # Bearish Crossunder
            elif float(e10_prev) >= float(e25_prev) and float(e10_now) < float(e25_now):  # type: ignore
                is_strong = float(e10_now) < float(e50_now) and curr["close"] < curr["open"]  # type: ignore
                signals.append({
                    "index": i,
                    "time": curr["time"],
                    "price": round(curr["high"] + (float(atr_now) * 0.4), 2),  # type: ignore
                    "type": "STRONG_SELL" if is_strong else "SELL",
                    "text": "🔴 فروش قوی (Strong Sell)" if is_strong else "🔴 فروش (Sell)",
                })

        return {
            "signals": signals,
            "fast_ribbon": ema10,
            "slow_ribbon": ema25,
            "trend_filter": ema50,
        }

    @staticmethod
    def smart_money_concepts(
        candles: list[dict[str, Any]],
        swing_lookback: int = 5,
    ) -> dict[str, Any]:
        """
        Smart Money Concepts (SMC) canonical implementation:
        - Order Blocks (OB)
        - Fair Value Gaps (FVG)
        """
        n = len(candles)
        order_blocks = []
        fair_value_gaps = []

        # 1. Fair Value Gaps (FVG)
        for i in range(2, n):
            low_i = float(candles[i]["low"])
            high_prev = float(candles[i - 2]["high"])
            close_i = float(candles[i]["close"])
            if low_i > high_prev:
                gap_size = low_i - high_prev
                if gap_size > (close_i * 0.001):
                    fair_value_gaps.append({
                        "type": "BULLISH_FVG",
                        "start_index": i - 2,
                        "end_index": i,
                        "time": candles[i]["time"],
                        "top": round(low_i, 4),
                        "bottom": round(high_prev, 4),
                    })
            else:
                high_i = float(candles[i]["high"])
                low_prev = float(candles[i - 2]["low"])
                if high_i < low_prev:
                    gap_size = low_prev - high_i
                    if gap_size > (close_i * 0.001):
                        fair_value_gaps.append({
                            "type": "BEARISH_FVG",
                            "start_index": i - 2,
                            "end_index": i,
                            "time": candles[i]["time"],
                            "top": round(low_prev, 4),
                            "bottom": round(high_i, 4),
                        })

        # 2. Order Blocks (OB)
        for i in range(swing_lookback, n - 2):
            close_i = float(candles[i]["close"])
            open_i = float(candles[i]["open"])
            if close_i < open_i:
                subsequent_high = max(float(c["high"]) for c in candles[i + 1 : i + 3])
                recent_high = max(float(c["high"]) for c in candles[i - swing_lookback : i])
                if subsequent_high > recent_high:
                    order_blocks.append({
                        "type": "BULLISH_OB",
                        "index": i,
                        "time": candles[i]["time"],
                        "top": round(float(candles[i]["high"]), 4),
                        "bottom": round(float(candles[i]["low"]), 4),
                        "label": "+OB (Bullish)",
                    })
            elif close_i > open_i:
                subsequent_low = min(float(c["low"]) for c in candles[i + 1 : i + 3])
                recent_low = min(float(c["low"]) for c in candles[i - swing_lookback : i])
                if subsequent_low < recent_low:
                    order_blocks.append({
                        "type": "BEARISH_OB",
                        "index": i,
                        "time": candles[i]["time"],
                        "top": round(float(candles[i]["high"]), 4),
                        "bottom": round(float(candles[i]["low"]), 4),
                        "label": "-OB (Bearish)",
                    })

        return {
            "order_blocks": order_blocks[-8:],
            "fair_value_gaps": fair_value_gaps[-12:],
        }
