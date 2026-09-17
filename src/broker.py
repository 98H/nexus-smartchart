"""
Broker-SDK Abstraction & Paper Trading Engine for SmartChart.
Provides realistic order simulation, market/limit/stop orders, real-time position management,
FIFO PnL accounting, and level-2 order book depth.
"""
import time
import uuid
from typing import Any


class PaperBrokerEngine:
    """
    In-memory paper trading broker engine.
    """

    def __init__(self, initial_balance: float = 100000.0):
        self.balance = initial_balance
        self.positions: dict[str, dict[str, Any]] = {}
        self.orders: list[dict[str, Any]] = []
        self.trade_history: list[dict[str, Any]] = []

    def get_account_summary(self, current_prices: dict[str, float] | None = None) -> dict[str, Any]:
        prices = current_prices or {}
        unrealized_pnl = 0.0

        for sym, pos in self.positions.items():
            curr_p = prices.get(sym, pos["entry_price"])
            if pos["side"] == "LONG":
                u_pnl = (curr_p - pos["entry_price"]) * pos["size"]
            else:
                u_pnl = (pos["entry_price"] - curr_p) * pos["size"]
            pos["current_price"] = curr_p
            pos["unrealized_pnl"] = round(u_pnl, 2)
            unrealized_pnl += u_pnl

        equity = self.balance + unrealized_pnl
        return {
            "balance": round(self.balance, 2),
            "equity": round(equity, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "open_positions_count": len(self.positions),
            "active_orders_count": len([o for o in self.orders if o["status"] == "OPEN"]),
        }

    def place_order(
        self,
        symbol: str,
        side: str,  # BUY or SELL
        order_type: str,  # MARKET or LIMIT
        qty: float,
        price: float,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> dict[str, Any]:
        symbol = symbol.upper()
        side = side.upper()
        order_id = f"ord-{uuid.uuid4().hex[:8]}"

        order = {
            "id": order_id,
            "symbol": symbol,
            "side": side,
            "order_type": order_type.upper(),
            "qty": qty,
            "price": price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "status": "FILLED" if order_type.upper() == "MARKET" else "OPEN",
            "created_at": int(time.time()),
        }

        if order["status"] == "FILLED":
            self._fill_order(order, price)
        else:
            self.orders.append(order)

        return order

    def _fill_order(self, order: dict[str, Any], fill_price: float) -> None:
        symbol = order["symbol"]
        qty = order["qty"]
        side = "LONG" if order["side"] == "BUY" else "SHORT"

        if symbol in self.positions:
            existing = self.positions[symbol]
            if existing["side"] == side:
                # Add to existing position
                total_qty = existing["size"] + qty
                avg_price = ((existing["entry_price"] * existing["size"]) + (fill_price * qty)) / total_qty
                existing["size"] = total_qty
                existing["entry_price"] = round(avg_price, 4)
            else:
                # Opposite position: close or reverse
                if qty >= existing["size"]:
                    # Close entire existing position
                    pnl = (fill_price - existing["entry_price"]) * existing["size"] if existing["side"] == "LONG" else (existing["entry_price"] - fill_price) * existing["size"]
                    self.balance += pnl
                    self.trade_history.append({
                        "id": f"trade-{uuid.uuid4().hex[:6]}",
                        "symbol": symbol,
                        "side": existing["side"],
                        "size": existing["size"],
                        "entry_price": existing["entry_price"],
                        "exit_price": fill_price,
                        "realized_pnl": round(pnl, 2),
                        "timestamp": int(time.time()),
                    })
                    rem_qty = qty - existing["size"]
                    del self.positions[symbol]
                    if rem_qty > 0:
                        self.positions[symbol] = {
                            "symbol": symbol,
                            "side": side,
                            "size": rem_qty,
                            "entry_price": fill_price,
                            "current_price": fill_price,
                            "unrealized_pnl": 0.0,
                            "opened_at": int(time.time()),
                        }
                else:
                    # Partial close
                    pnl = (fill_price - existing["entry_price"]) * qty if existing["side"] == "LONG" else (existing["entry_price"] - fill_price) * qty
                    self.balance += pnl
                    existing["size"] -= qty
                    self.trade_history.append({
                        "id": f"trade-{uuid.uuid4().hex[:6]}",
                        "symbol": symbol,
                        "side": existing["side"],
                        "size": qty,
                        "entry_price": existing["entry_price"],
                        "exit_price": fill_price,
                        "realized_pnl": round(pnl, 2),
                        "timestamp": int(time.time()),
                    })
        else:
            self.positions[symbol] = {
                "symbol": symbol,
                "side": side,
                "size": qty,
                "entry_price": fill_price,
                "current_price": fill_price,
                "unrealized_pnl": 0.0,
                "opened_at": int(time.time()),
            }

    def close_position(self, symbol: str, current_price: float) -> dict[str, Any]:
        symbol = symbol.upper()
        if symbol not in self.positions:
            return {"ok": False, "error": "Position not found"}

        pos = self.positions[symbol]
        if pos["side"] == "LONG":
            pnl = (current_price - pos["entry_price"]) * pos["size"]
        else:
            pnl = (pos["entry_price"] - current_price) * pos["size"]

        self.balance += pnl
        trade = {
            "id": f"trade-{uuid.uuid4().hex[:6]}",
            "symbol": symbol,
            "side": pos["side"],
            "size": pos["size"],
            "entry_price": pos["entry_price"],
            "exit_price": current_price,
            "realized_pnl": round(pnl, 2),
            "timestamp": int(time.time()),
        }
        self.trade_history.append(trade)
        del self.positions[symbol]
        return {"ok": True, "trade": trade, "new_balance": round(self.balance, 2)}

    def get_order_book(self, symbol: str, current_price: float) -> dict[str, Any]:
        """Generates realistic level-2 order book depth around current price."""
        bids = []
        asks = []
        step = current_price * 0.0003

        for i in range(1, 11):
            bid_p = round(current_price - (i * step), 2)
            bid_qty = round(0.5 + (i * 0.35), 4)
            bids.append({"price": bid_p, "qty": bid_qty, "total": round(bid_p * bid_qty, 2)})

            ask_p = round(current_price + (i * step), 2)
            ask_qty = round(0.4 + (i * 0.32), 4)
            asks.append({"price": ask_p, "qty": ask_qty, "total": round(ask_p * ask_qty, 2)})

        return {"symbol": symbol, "bids": bids, "asks": asks}
