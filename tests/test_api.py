"""
API Endpoint Verification for SmartChart.
"""
import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_index_and_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

    res_html = client.get("/")
    assert res_html.status_code == 200
    assert "SmartChart" in res_html.text


def test_market_api(client):
    res_syms = client.get("/api/market/symbols")
    assert res_syms.status_code == 200
    assert len(res_syms.json()) > 0

    res_klines = client.get("/api/market/klines?symbol=BTCUSDT&interval=1h&limit=50")
    assert res_klines.status_code == 200
    assert len(res_klines.json()["candles"]) == 50


def test_indicators_api(client):
    res = client.get("/api/indicators/compute?symbol=BTCUSDT&interval=1h")
    assert res.status_code == 200
    data = res.json()
    assert "sma20" in data
    assert "ema50" in data
    assert "supertrend" in data
    assert "signals" in data
    assert "smc" in data


def test_pine_script_api(client):
    code = """//@version=5
indicator("API Test", overlay=true)
fast = ta.sma(close, 5)
plot(fast)
"""
    res = client.post("/api/pine/execute", json={"code": code, "symbol": "BTCUSDT", "interval": "1h"})
    assert res.status_code == 200
    data = res.json()
    assert data["version"] == 5
    assert len(data["plots"]) == 1


def test_trade_and_stats_api(client):
    # Place order
    res_order = client.post("/api/trade/order", json={
        "symbol": "ETHUSDT",
        "side": "BUY",
        "order_type": "MARKET",
        "qty": 2.0,
        "price": 3800.0,
    })
    assert res_order.status_code == 200
    assert res_order.json()["status"] == "FILLED"

    # Monte Carlo simulation
    res_mc = client.post("/api/stats/monte-carlo", json={
        "account_size": 100000.0,
        "win_rate_pct": 52.0,
        "risk_reward_ratio": 1.5,
    })
    assert res_mc.status_code == 200
    assert "pass_probability_pct" in res_mc.json()
