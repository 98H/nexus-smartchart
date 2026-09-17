"""
Tests for StatsSimulationEngine (Monte Carlo & Prop-Firm-Sim) in SmartChart.
"""
from src.stats_engine import StatsSimulationEngine


def test_wilson_interval():
    ci = StatsSimulationEngine.wilson_score_interval(successes=50, trials=100)
    assert ci["point_estimate"] == 50.0
    assert 35.0 < ci["lower"] < 50.0
    assert 50.0 < ci["upper"] < 65.0


def test_prop_challenge_monte_carlo():
    res = StatsSimulationEngine.simulate_prop_challenge(
        account_size=100000.0,
        profit_target_pct=10.0,
        max_total_loss_pct=10.0,
        win_rate_pct=55.0,
        risk_reward_ratio=1.5,
        risk_per_trade_pct=1.0,
        simulations_count=200,
    )
    assert "pass_probability_pct" in res
    assert 0 <= res["pass_probability_pct"] <= 100
    assert "wilson_95_ci" in res
    assert "expected_value_usd" in res
    assert len(res["risk_sweep"]) > 0
