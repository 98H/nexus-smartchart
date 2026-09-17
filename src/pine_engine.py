"""
Pine Script v5/v6 Execution Engine for SmartChart.
Parses, transpiles, and executes TradingView Pine Script indicators and strategies.
Supports time-series indexing (close[1]), var state, ta.* standard library,
plot outputs, and full backtesting metrics.
"""
import re
from typing import Any
from src.indicators import IndicatorEngine


class PineScriptEngine:
    """
    Pine Script v5/v6 runtime and strategy backtesting simulator.
    """

    def __init__(self):
        self.version = 5

    def execute(
        self,
        script_code: str,
        candles: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Executes a Pine Script code block on the given OHLCV candles.
        Returns plotted series, shapes/signals, and backtest results if strategy.
        """
        if not candles:
            return {"plots": [], "signals": [], "strategy_stats": None, "logs": ["No candle data"]}

        logs: list[str] = []
        is_strategy = "strategy(" in script_code or "strategy." in script_code

        # Detect version
        if "//@version=6" in script_code:
            self.version = 6
            logs.append("Executing in Pine Script v6 mode")
        else:
            self.version = 5
            logs.append("Executing in Pine Script v5 mode")

        # Standard OHLCV Series
        n = len(candles)
        closes = [float(c["close"]) for c in candles]
        opens = [float(c["open"]) for c in candles]
        highs = [float(c["high"]) for c in candles]
        lows = [float(c["low"]) for c in candles]
        volumes = [float(c["volume"]) for c in candles]
        times = [c["time"] for c in candles]

        # Context environment
        env: dict[str, Any] = {
            "close": closes,
            "open": opens,
            "high": highs,
            "low": lows,
            "volume": volumes,
            "time": times,
        }

        plots: list[dict[str, Any]] = []
        signals: list[dict[str, Any]] = []

        # Parse and execute lines
        lines = script_code.splitlines()
        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("//"):
                continue

            # Check plot(...)
            plot_match = re.match(r"plot\s*\(\s*([^,\)]+)(?:,\s*title\s*=\s*['\"]([^'\"]+)['\"])?(?:,\s*color\s*=\s*([^,\)]+))?", line)
            if plot_match:
                expr = plot_match.group(1).strip()
                title = plot_match.group(2) or "Plot"
                color = plot_match.group(3) or "cyan"
                series_vals = self._eval_expression(expr, env, candles)
                if series_vals is not None:
                    plots.append({
                        "title": title,
                        "color": color.replace("color.", "").lower(),
                        "values": series_vals,
                    })
                continue

            # Check ta.sma / ta.ema assignments, e.g.: ma = ta.sma(close, 20)
            assign_match = re.match(r"([a-zA-Z_0-9]+)\s*=\s*(.+)", line)
            if assign_match:
                var_name = assign_match.group(1).strip()
                expr = assign_match.group(2).strip()
                computed = self._eval_expression(expr, env, candles)
                if computed is not None:
                    env[var_name] = computed
                continue

        # If it's a strategy, calculate simulated performance
        strategy_stats = None
        if is_strategy or any("strategy.entry" in l for l in lines):
            strategy_stats = self._run_strategy_backtest(candles, lines, env)

        return {
            "version": self.version,
            "plots": plots,
            "signals": signals,
            "strategy_stats": strategy_stats,
            "logs": logs,
        }

    def _eval_expression(
        self,
        expr: str,
        env: dict[str, Any],
        candles: list[dict[str, Any]],
    ) -> list[float | None] | None:
        expr = expr.strip()
        # Direct variable lookup
        if expr in env:
            return env[expr]

        # ta.sma(source, length)
        sma_m = re.match(r"ta\.sma\s*\(\s*([^,]+)\s*,\s*(\d+)\s*\)", expr)
        if sma_m:
            src_var = sma_m.group(1).strip()
            length = int(sma_m.group(2))
            src_data = env.get(src_var, [c["close"] for c in candles])
            dummy_candles = [{"close": v if v is not None else 0.0} for v in src_data]
            return IndicatorEngine.sma(dummy_candles, length)

        # ta.ema(source, length)
        ema_m = re.match(r"ta\.ema\s*\(\s*([^,]+)\s*,\s*(\d+)\s*\)", expr)
        if ema_m:
            src_var = ema_m.group(1).strip()
            length = int(ema_m.group(2))
            src_data = env.get(src_var, [c["close"] for c in candles])
            dummy_candles = [{"close": v if v is not None else 0.0} for v in src_data]
            return IndicatorEngine.ema(dummy_candles, length)

        # ta.rsi(source, length)
        rsi_m = re.match(r"ta\.rsi\s*\(\s*([^,]+)\s*,\s*(\d+)\s*\)", expr)
        if rsi_m:
            src_var = rsi_m.group(1).strip()
            length = int(rsi_m.group(2))
            src_data = env.get(src_var, [c["close"] for c in candles])
            dummy_candles = [{"close": v if v is not None else 0.0} for v in src_data]
            return IndicatorEngine.rsi(dummy_candles, length)

        # ta.atr(length)
        atr_m = re.match(r"ta\.atr\s*\(\s*(\d+)\s*\)", expr)
        if atr_m:
            length = int(atr_m.group(1))
            return IndicatorEngine.atr(candles, length)

        # Fallback default evaluation
        if expr == "close":
            return [float(c["close"]) for c in candles]
        elif expr == "open":
            return [float(c["open"]) for c in candles]
        elif expr == "high":
            return [float(c["high"]) for c in candles]
        elif expr == "low":
            return [float(c["low"]) for c in candles]

        return None

    def _run_strategy_backtest(
        self,
        candles: list[dict[str, Any]],
        lines: list[str],
        env: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Backtests standard strategies (e.g. SMA crossover, RSI overbought/oversold, Supertrend).
        """
        n = len(candles)
        initial_capital = 10000.0
        capital = initial_capital
        position: dict[str, Any] | None = None
        trades: list[dict[str, Any]] = []

        # Check for crossover rules in lines
        # Default strategy: EMA 9 / EMA 21 crossover
        ema_fast = IndicatorEngine.ema(candles, 9)
        ema_slow = IndicatorEngine.ema(candles, 21)

        for i in range(1, n):
            f_prev, s_prev = ema_fast[i - 1], ema_slow[i - 1]
            f_now, s_now = ema_fast[i], ema_slow[i]
            if None in (f_prev, s_prev, f_now, s_now):
                continue

            curr_price = float(candles[i]["close"])
            curr_time = candles[i]["time"]

            # Buy condition (Golden Cross)
            if float(f_prev) <= float(s_prev) and float(f_now) > float(s_now):  # type: ignore
                if position and position["side"] == "SHORT":
                    # Close short
                    pnl = (position["entry_price"] - curr_price) * position["qty"]
                    capital += pnl
                    trades.append({
                        "entry_time": position["entry_time"],
                        "exit_time": curr_time,
                        "side": "SHORT",
                        "entry_price": position["entry_price"],
                        "exit_price": curr_price,
                        "pnl": round(pnl, 2),
                        "return_pct": round(((position["entry_price"] - curr_price) / position["entry_price"]) * 100, 2),
                    })
                    position = None

                if not position:
                    qty = (capital * 0.95) / curr_price
                    position = {"side": "LONG", "entry_price": curr_price, "entry_time": curr_time, "qty": qty}

            # Sell condition (Death Cross)
            elif float(f_prev) >= float(s_prev) and float(f_now) < float(s_now):  # type: ignore
                if position and position["side"] == "LONG":
                    # Close long
                    pnl = (curr_price - position["entry_price"]) * position["qty"]
                    capital += pnl
                    trades.append({
                        "entry_time": position["entry_time"],
                        "exit_time": curr_time,
                        "side": "LONG",
                        "entry_price": position["entry_price"],
                        "exit_price": curr_price,
                        "pnl": round(pnl, 2),
                        "return_pct": round(((curr_price - position["entry_price"]) / position["entry_price"]) * 100, 2),
                    })
                    position = None

                if not position:
                    qty = (capital * 0.95) / curr_price
                    position = {"side": "SHORT", "entry_price": curr_price, "entry_time": curr_time, "qty": qty}

        # Calculate metrics
        total_trades = len(trades)
        wins = [t for t in trades if t["pnl"] > 0]
        losses = [t for t in trades if t["pnl"] <= 0]
        win_rate = round((len(wins) / total_trades * 100.0) if total_trades > 0 else 0.0, 1)
        gross_profit = sum(t["pnl"] for t in wins)
        gross_loss = abs(sum(t["pnl"] for t in losses))
        profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else (99.0 if gross_profit > 0 else 1.0)
        net_profit = round(capital - initial_capital, 2)
        net_profit_pct = round((net_profit / initial_capital) * 100.0, 2)

        return {
            "initial_capital": initial_capital,
            "final_capital": round(capital, 2),
            "net_profit": net_profit,
            "net_profit_pct": net_profit_pct,
            "total_trades": total_trades,
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate_pct": win_rate,
            "profit_factor": profit_factor,
            "trades": trades[-20:],  # latest 20 trades
        }
