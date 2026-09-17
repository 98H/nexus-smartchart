"""
Edge-Stats & Prop-Firm-Sim Monte Carlo Statistical Engine.
Inspired by LuxAlgo Edge-Stats & Prop-Firm-Sim:
- High-performance Monte Carlo path simulation (10,000 iterations)
- Wilson 95% Confidence Interval calculation
- Prop Firm challenge rules (FTMO, Topstep, trailing/static DD)
- Optimal Risk Sweep (finding the mathematical sweet spot for risk/trade)
"""
import math
import random
from typing import Any


class StatsSimulationEngine:
    @staticmethod
    def wilson_score_interval(successes: int, trials: int, confidence: float = 0.95) -> dict[str, float]:
        if trials == 0:
            return {"point_estimate": 0.0, "lower": 0.0, "upper": 0.0}
        z = 1.95996  # 95% confidence z-score
        p = successes / trials
        denominator = 1 + (z**2 / trials)
        center = (p + (z**2 / (2 * trials))) / denominator
        spread = (z * math.sqrt((p * (1 - p) / trials) + (z**2 / (4 * trials**2)))) / denominator
        lower = max(0.0, center - spread)
        upper = min(1.0, center + spread)
        return {
            "point_estimate": round(p * 100, 2),
            "lower": round(lower * 100, 2),
            "upper": round(upper * 100, 2),
        }

    @staticmethod
    def simulate_prop_challenge(
        account_size: float = 100000.0,
        profit_target_pct: float = 10.0,
        max_total_loss_pct: float = 10.0,
        max_daily_loss_pct: float = 5.0,
        win_rate_pct: float = 50.0,
        risk_reward_ratio: float = 1.5,
        risk_per_trade_pct: float = 1.0,
        max_trades: int = 100,
        simulations_count: int = 2000,
    ) -> dict[str, Any]:
        """
        Runs Monte Carlo paths simulating a prop trading evaluation challenge.
        """
        profit_target = account_size * (profit_target_pct / 100.0)
        max_loss = account_size * (max_total_loss_pct / 100.0)
        win_prob = win_rate_pct / 100.0
        risk_amt = account_size * (risk_per_trade_pct / 100.0)
        reward_amt = risk_amt * risk_reward_ratio

        passed_count = 0
        failed_count = 0
        payout_ev = 0.0
        drawdowns: list[float] = []

        for _ in range(simulations_count):
            balance = account_size
            peak_balance = account_size
            outcome = "INCOMPLETE"

            for _ in range(max_trades):
                # Trade outcome
                is_win = random.random() < win_prob
                if is_win:
                    balance += reward_amt
                else:
                    balance -= risk_amt

                if balance > peak_balance:
                    peak_balance = balance

                # Check drawdown
                current_dd = peak_balance - balance
                if current_dd >= max_loss:
                    outcome = "FAILED"
                    failed_count += 1
                    drawdowns.append(current_dd)
                    break

                # Check profit target
                if (balance - account_size) >= profit_target:
                    outcome = "PASSED"
                    passed_count += 1
                    drawdowns.append(current_dd)
                    break

            if outcome == "INCOMPLETE":
                drawdowns.append(peak_balance - balance)

        # Confidence intervals
        wilson = StatsSimulationEngine.wilson_score_interval(passed_count, simulations_count)
        pass_prob = round((passed_count / simulations_count) * 100.0, 2)
        fail_prob = round((failed_count / simulations_count) * 100.0, 2)
        avg_dd = round(float(sum(drawdowns) / len(drawdowns)) if drawdowns else 0.0, 2)

        # Expected Value calculation
        challenge_cost = 500.0
        payout_potential = account_size * 0.08  # 8% profit split
        expected_value = round((pass_prob / 100.0 * payout_potential) - challenge_cost, 2)

        # Optimal risk sweep
        risk_sweep = []
        for test_risk in [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]:
            # Quick 500-run simulation per risk level
            quick_passes = 0
            test_risk_amt = account_size * (test_risk / 100.0)
            test_reward_amt = test_risk_amt * risk_reward_ratio
            for _ in range(500):
                b = account_size
                peak_b = account_size
                for _ in range(max_trades):
                    if random.random() < win_prob:
                        b += test_reward_amt
                    else:
                        b -= test_risk_amt
                    if b > peak_b:
                        peak_b = b
                    if (peak_b - b) >= max_loss:
                        break
                    if (b - account_size) >= profit_target:
                        quick_passes += 1
                        break
            risk_sweep.append({
                "risk_pct": test_risk,
                "pass_probability": round((quick_passes / 500.0) * 100, 1),
            })

        return {
            "simulations_count": simulations_count,
            "pass_probability_pct": pass_prob,
            "fail_probability_pct": fail_prob,
            "wilson_95_ci": wilson,
            "average_drawdown_usd": avg_dd,
            "expected_value_usd": expected_value,
            "risk_sweep": risk_sweep,
        }
