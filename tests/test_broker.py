"""
Tests for Broker-SDK & Paper Trading Engine in SmartChart.
"""
from src.broker import PaperBrokerEngine


def test_broker_order_placement_and_pnl():
    broker = PaperBrokerEngine(initial_balance=100000.0)

    # Buy 1 BTC at $60,000
    order = broker.place_order(
        symbol="BTCUSDT",
        side="BUY",
        order_type="MARKET",
        qty=1.0,
        price=60000.0,
    )
    assert order["status"] == "FILLED"
    assert "BTCUSDT" in broker.positions
    assert broker.positions["BTCUSDT"]["size"] == 1.0

    # Account summary with price at $65,000 (+$5,000 profit)
    summary = broker.get_account_summary(current_prices={"BTCUSDT": 65000.0})
    assert summary["unrealized_pnl"] == 5000.0
    assert summary["equity"] == 105000.0

    # Close position at $65,000
    close_res = broker.close_position("BTCUSDT", current_price=65000.0)
    assert close_res["ok"] is True
    assert close_res["new_balance"] == 105000.0
    assert "BTCUSDT" not in broker.positions


def test_order_book():
    broker = PaperBrokerEngine()
    ob = broker.get_order_book("BTCUSDT", current_price=68000.0)
    assert len(ob["bids"]) == 10
    assert len(ob["asks"]) == 10
    assert ob["bids"][0]["price"] < 68000.0
    assert ob["asks"][0]["price"] > 68000.0
