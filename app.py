"""
SmartChart — Enterprise Financial Charting & Algorithmic Trading Platform.
100% White-Label TradingView Replacement powered by LuxAlgo Open Ecosystem.
"""
import argparse
import sys
from pathlib import Path
from typing import Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from pydantic import BaseModel

from src.alt_data import AlternativeDataProvider
from src.broker import PaperBrokerEngine
from src.indicators import IndicatorEngine
from src.market_data import MarketDataProvider
from src.pine_engine import PineScriptEngine
from src.stats_engine import StatsSimulationEngine

app = FastAPI(
    title="SmartChart",
    description="Enterprise TradingView Alternative based on LuxAlgo Open Ecosystem",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

market_data = MarketDataProvider()
pine_engine = PineScriptEngine()
broker = PaperBrokerEngine(initial_balance=100000.0)
alt_data = AlternativeDataProvider()


# Pydantic Schemas
class PineExecuteRequest(BaseModel):
    code: str
    symbol: str = "BTCUSDT"
    interval: str = "1h"


class OrderRequest(BaseModel):
    symbol: str
    side: str
    order_type: str = "MARKET"
    qty: float
    price: float
    stop_loss: float | None = None
    take_profit: float | None = None


class MonteCarloRequest(BaseModel):
    account_size: float = 100000.0
    profit_target_pct: float = 10.0
    max_total_loss_pct: float = 10.0
    max_daily_loss_pct: float = 5.0
    win_rate_pct: float = 52.0
    risk_reward_ratio: float = 1.5
    risk_per_trade_pct: float = 1.0


# --- Web UI Endpoint ---
@app.get("/", response_class=HTMLResponse)
@app.head("/", response_class=HTMLResponse)
async def serve_index():
    candles = market_data.fetch_klines(symbol="BTCUSDT", interval="1h", limit=120)
    index_file = BASE_DIR / "templates" / "index.html"
    content = index_file.read_text(encoding="utf-8")
    import json
    initial_script = f"<script>window.INITIAL_CANDLES = {json.dumps(candles)};</script>"
    content = content.replace("<!-- INITIAL_DATA_PLACEHOLDER -->", initial_script)
    return HTMLResponse(content=content)


# --- Market Data Endpoints ---
@app.get("/api/market/symbols")
async def get_symbols():
    return market_data.get_available_symbols()


@app.get("/api/market/klines")
async def get_klines(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 200):
    candles = market_data.fetch_klines(symbol=symbol, interval=interval, limit=limit)
    return {"symbol": symbol, "interval": interval, "candles": candles}


# --- Indicator Suite Endpoints ---
@app.get("/api/indicators/compute")
async def compute_indicators(symbol: str = "BTCUSDT", interval: str = "1h"):
    candles = market_data.fetch_klines(symbol=symbol, interval=interval, limit=180)
    sma20 = IndicatorEngine.sma(candles, 20)
    ema50 = IndicatorEngine.ema(candles, 50)
    supertrend = IndicatorEngine.supertrend(candles, 10, 3.0)
    signals_data = IndicatorEngine.luxalgo_signals_and_overlays(candles)
    smc_data = IndicatorEngine.smart_money_concepts(candles)

    return {
        "symbol": symbol,
        "sma20": sma20,
        "ema50": ema50,
        "supertrend": supertrend,
        "signals": signals_data.get("signals", []),
        "smc": smc_data,
    }


# --- Pine Script v5/v6 Execution ---
@app.post("/api/pine/execute")
async def execute_pine(payload: PineExecuteRequest):
    candles = market_data.fetch_klines(symbol=payload.symbol, interval=payload.interval, limit=180)
    result = pine_engine.execute(payload.code, candles)
    return result


# --- Paper Broker Endpoints ---
@app.get("/api/trade/account")
async def get_account():
    # Update with latest mock prices
    prices = {s["symbol"]: s["base_price"] for s in market_data.get_available_symbols()}
    return broker.get_account_summary(current_prices=prices)


@app.post("/api/trade/order")
async def place_order(payload: OrderRequest):
    order = broker.place_order(
        symbol=payload.symbol,
        side=payload.side,
        order_type=payload.order_type,
        qty=payload.qty,
        price=payload.price,
        stop_loss=payload.stop_loss,
        take_profit=payload.take_profit,
    )
    return order


# --- Monte Carlo Simulator ---
@app.post("/api/stats/monte-carlo")
async def run_monte_carlo(payload: MonteCarloRequest):
    sim = StatsSimulationEngine.simulate_prop_challenge(
        account_size=payload.account_size,
        profit_target_pct=payload.profit_target_pct,
        max_total_loss_pct=payload.max_total_loss_pct,
        max_daily_loss_pct=payload.max_daily_loss_pct,
        win_rate_pct=payload.win_rate_pct,
        risk_reward_ratio=payload.risk_reward_ratio,
        risk_per_trade_pct=payload.risk_per_trade_pct,
        simulations_count=2000,
    )
    return sim


# --- Transparency & Alternative Feeds ---
@app.get("/api/data/congressional-trades")
async def get_congressional_trades():
    return alt_data.get_congressional_trades()


@app.get("/api/data/insider-trading")
async def get_insider_trades(symbol: str = "BTCUSDT"):
    return alt_data.get_insider_filings(symbol=symbol)


@app.get("/api/data/cot-positioning")
async def get_cot_positioning():
    return alt_data.get_cot_positioning()


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "SmartChart", "engine": "Vela-PineTS"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8100, help="Port to listen on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to listen on")
    args, unknown = parser.parse_known_args()

    port = args.port
    # If port was passed as positional or flag
    if len(sys.argv) > 2 and sys.argv[1] == "--port":
        port = int(sys.argv[2])

    print(f"Starting SmartChart on http://{args.host}:{port}")
    uvicorn.run("app:app", host=args.host, port=port, log_level="info", reload=False)
