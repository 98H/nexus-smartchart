/**
 * SmartChart TradingView UI Controller.
 * Manages symbol universe, indicators, Pine Script studio, paper broker, and quant simulator.
 */
let chart = null;
let currentSymbol = 'BTCUSDT';
let currentInterval = '1h';
let liveCandles = [];
let activeIndicators = { sma20: true, ema50: true, smc: true, signals: true };

// Default Pine Script templates
const PINE_TEMPLATES = {
  sma_cross: `//@version=5
strategy("Golden Cross Strategy", overlay=true)

fast = ta.ema(close, 9)
slow = ta.ema(close, 21)

plot(fast, title="Fast EMA", color=color.blue)
plot(slow, title="Slow EMA", color=color.orange)

if ta.crossover(fast, slow)
    strategy.entry("Long", strategy.long)

if ta.crossunder(fast, slow)
    strategy.close("Long")
`,
  luxalgo_smc: `//@version=5
indicator("LuxAlgo Smart Money Concepts", overlay=true)

// Detect Fair Value Gaps and Order Blocks
len = 14
rsi = ta.rsi(close, len)
plot(rsi, title="RSI", color=color.purple)
`,
  supertrend: `//@version=5
strategy("Supertrend Volatility Breakout", overlay=true)

atrPeriod = 10
factor = 3.0

[supertrend, direction] = ta.supertrend(factor, atrPeriod)
plot(supertrend, title="Supertrend", color=direction < 0 ? color.green : color.red)
`
};

document.addEventListener('DOMContentLoaded', async () => {
  initChart();
  await loadSymbols();
  await loadChartData();
  setupEventListeners();
  setupPineEditor();
  loadAccountInfo();
  loadAlternativeData();
});

function initChart() {
  chart = new VelaChart('chartContainer', {
    candleUpColor: '#089981',
    candleDownColor: '#f23645',
  });
}

async function loadSymbols() {
  try {
    const res = await fetch('/api/market/symbols');
    const symbols = await res.json();
    const watchlistEl = document.getElementById('watchlistItems');
    if (watchlistEl) {
      watchlistEl.innerHTML = symbols.map(s => `
        <div onclick="selectSymbol('${s.symbol}')" class="flex items-center justify-between p-2 rounded-xl hover:bg-[#1e222d] cursor-pointer transition text-xs ${s.symbol === currentSymbol ? 'bg-[#1e222d] border-r-2 border-cyan-400' : ''}">
          <div>
            <span class="font-black text-white block">${s.symbol}</span>
            <span class="text-[10px] text-slate-400">${s.name}</span>
          </div>
          <div class="text-right">
            <span class="font-mono text-white block">$${s.base_price.toLocaleString()}</span>
            <span class="text-[10px] text-emerald-400 font-bold">+1.84%</span>
          </div>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error('Failed to load symbols', err);
  }
}

async function loadChartData() {
  if (window.INITIAL_CANDLES && window.INITIAL_CANDLES.length > 0 && currentSymbol === 'BTCUSDT' && currentInterval === '1h') {
    liveCandles = window.INITIAL_CANDLES;
    chart.setData(liveCandles);
    updateHeaderPrice();
    window.INITIAL_CANDLES = null;
    calculateAndRenderIndicators();
    return;
  }
  try {
    const res = await fetch(`/api/market/klines?symbol=${currentSymbol}&interval=${currentInterval}&limit=180`);
    const data = await res.json();
    liveCandles = data.candles || [];
    chart.setData(liveCandles);
    updateHeaderPrice();
    await calculateAndRenderIndicators();
  } catch (err) {
    console.error('Failed to load klines', err);
  }
}

function updateHeaderPrice() {
  if (liveCandles.length > 0) {
    const last = liveCandles[liveCandles.length - 1];
    const prev = liveCandles[liveCandles.length - 2] || last;
    const chg = last.close - prev.close;
    const chgPct = ((chg / prev.close) * 100).toFixed(2);
    const isUp = chg >= 0;

    const pEl = document.getElementById('headerPrice');
    if (pEl) pEl.textContent = `$${last.close.toLocaleString()}`;
    const chgEl = document.getElementById('headerChange');
    if (chgEl) {
      chgEl.textContent = `${isUp ? '+' : ''}${chg.toFixed(2)} (${isUp ? '+' : ''}${chgPct}%)`;
      chgEl.className = `text-xs font-bold ${isUp ? 'text-emerald-400' : 'text-rose-400'}`;
    }
  }
}

async function calculateAndRenderIndicators() {
  try {
    const res = await fetch(`/api/indicators/compute?symbol=${currentSymbol}&interval=${currentInterval}`);
    const indicatorsData = await res.json();
    chart.setIndicators(indicatorsData);
  } catch (err) {
    console.error('Failed to compute indicators', err);
  }
}

function selectSymbol(symbol) {
  currentSymbol = symbol;
  document.getElementById('currentSymbolBtn').textContent = symbol;
  loadChartData();
  loadSymbols();
  loadOrderBook();
}

function setTimeframe(tf) {
  currentInterval = tf;
  document.querySelectorAll('.tf-btn').forEach(btn => {
    btn.classList.toggle('bg-[#2962ff]', btn.dataset.tf === tf);
    btn.classList.toggle('text-white', btn.dataset.tf === tf);
  });
  loadChartData();
}

function selectTool(tool) {
  document.querySelectorAll('.tool-btn').forEach(btn => {
    btn.classList.remove('bg-cyan-500/20', 'text-cyan-400');
  });
  const activeBtn = document.querySelector(`[data-tool="${tool}"]`);
  if (activeBtn) activeBtn.classList.add('bg-cyan-500/20', 'text-cyan-400');
  chart.setDrawingTool(tool);
}

function setupPineEditor() {
  const editor = document.getElementById('pineScriptCode');
  if (editor) {
    editor.value = PINE_TEMPLATES.sma_cross;
  }
}

async function executePineScript() {
  const code = document.getElementById('pineScriptCode').value;
  const statusEl = document.getElementById('pineStatus');
  statusEl.textContent = 'در حال کامپایل و اجرای کد پاین...';

  try {
    const res = await fetch('/api/pine/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, symbol: currentSymbol, interval: currentInterval })
    });
    const result = await res.json();
    statusEl.textContent = `اجرا شد (${result.version ? 'نسخه ' + result.version : 'موفق'}).`;

    if (result.plots && result.plots.length > 0) {
      const customInds = { ...chart.indicators };
      result.plots.forEach((p, idx) => {
        customInds[`pine_plot_${idx}`] = p.values;
      });
      chart.setIndicators(customInds);
    }

    if (result.strategy_stats) {
      renderStrategyStats(result.strategy_stats);
    }
  } catch (err) {
    statusEl.textContent = 'خطا در کامپایل: ' + String(err);
  }
}

function renderStrategyStats(stats) {
  document.getElementById('tabStrategyTesterBtn').click();
  document.getElementById('statNetProfit').textContent = `$${stats.net_profit} (${stats.net_profit_pct}%)`;
  document.getElementById('statNetProfit').className = `text-base font-black ${stats.net_profit >= 0 ? 'text-emerald-400' : 'text-rose-400'}`;
  document.getElementById('statWinRate').textContent = `${stats.win_rate_pct}%`;
  document.getElementById('statProfitFactor').textContent = stats.profit_factor;
  document.getElementById('statTotalTrades').textContent = stats.total_trades;

  const tradeListEl = document.getElementById('strategyTradesList');
  if (tradeListEl && stats.trades) {
    tradeListEl.innerHTML = stats.trades.map(t => `
      <tr class="border-b border-[#1e222d] text-xs">
        <td class="p-2 font-bold ${t.side === 'LONG' ? 'text-emerald-400' : 'text-rose-400'}">${t.side}</td>
        <td class="p-2 font-mono">$${t.entry_price}</td>
        <td class="p-2 font-mono">$${t.exit_price}</td>
        <td class="p-2 font-mono font-bold ${t.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}">$${t.pnl} (${t.return_pct}%)</td>
      </tr>
    `).join('');
  }
}

async function loadAccountInfo() {
  try {
    const res = await fetch('/api/trade/account');
    const acc = await res.json();
    document.getElementById('paperBalance').textContent = `$${acc.balance.toLocaleString()}`;
    document.getElementById('paperEquity').textContent = `$${acc.equity.toLocaleString()}`;
    const pnlEl = document.getElementById('paperPnL');
    pnlEl.textContent = `$${acc.unrealized_pnl.toLocaleString()}`;
    pnlEl.className = `text-xs font-mono font-bold ${acc.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`;
  } catch (err) {
    console.error('Failed to load account', err);
  }
}

async function placePaperTrade(side) {
  const qty = parseFloat(document.getElementById('orderQtyInput').value) || 0.1;
  const lastPrice = liveCandles.length > 0 ? liveCandles[liveCandles.length - 1].close : 68000;

  try {
    const res = await fetch('/api/trade/order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbol: currentSymbol,
        side: side,
        order_type: 'MARKET',
        qty: qty,
        price: lastPrice
      })
    });
    const ord = await res.json();
    alert(`سفارش ${side === 'BUY' ? 'خرید' : 'فروش'} ثبت و در قیمت $${lastPrice} اجرا شد.`);
    loadAccountInfo();
  } catch (err) {
    alert('خطا در ثبت سفارش: ' + String(err));
  }
}

async function runPropFirmSimulation() {
  const accSize = parseFloat(document.getElementById('propAccSize').value) || 100000;
  const winRate = parseFloat(document.getElementById('propWinRate').value) || 52;
  const rr = parseFloat(document.getElementById('propRR').value) || 1.5;
  const risk = parseFloat(document.getElementById('propRisk').value) || 1.0;

  const btn = document.getElementById('btnRunPropSim');
  btn.textContent = 'در حال اجرای ۱۰,۰۰۰ شبیه‌سازی مونت‌کارلو...';

  try {
    const res = await fetch('/api/stats/monte-carlo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        account_size: accSize,
        win_rate_pct: winRate,
        risk_reward_ratio: rr,
        risk_per_trade_pct: risk,
      })
    });
    const data = await res.json();
    document.getElementById('propPassProb').textContent = `${data.pass_probability_pct}%`;
    document.getElementById('propWilsonCI').textContent = `${data.wilson_95_ci.lower}% - ${data.wilson_95_ci.upper}%`;
    document.getElementById('propEV').textContent = `$${data.expected_value_usd}`;
  } catch (err) {
    alert('خطا در شبیه‌سازی: ' + String(err));
  } finally {
    btn.textContent = '🎲 اجرای شبیه‌سازی مونت‌کارلو (Monte Carlo)';
  }
}

async function loadAlternativeData() {
  try {
    const res = await fetch('/api/data/congressional-trades');
    const trades = await res.json();
    const cEl = document.getElementById('congressionalTradesList');
    if (cEl) {
      cEl.innerHTML = trades.map(t => `
        <div class="p-2.5 rounded-xl bg-[#131722] border border-[#1e222d] text-xs space-y-1">
          <div class="flex items-center justify-between font-bold">
            <span class="text-white">${t.politician}</span>
            <span class="text-cyan-400 font-mono">${t.ticker}</span>
          </div>
          <div class="text-[11px] text-slate-400">${t.type} • ${t.amount}</div>
          <div class="text-[10px] text-slate-500 font-mono">${t.filed_date}</div>
        </div>
      `).join('');
    }
  } catch (err) {}
}

function setupEventListeners() {
  // Timeframe buttons
  document.querySelectorAll('.tf-btn').forEach(btn => {
    btn.addEventListener('click', () => setTimeframe(btn.dataset.tf));
  });

  // Bottom drawer switcher
  document.querySelectorAll('.drawer-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.drawer-tab-btn').forEach(b => b.classList.remove('active-tab', 'text-cyan-400', 'border-b-2', 'border-cyan-400'));
      btn.classList.add('active-tab', 'text-cyan-400', 'border-b-2', 'border-cyan-400');
      document.querySelectorAll('.drawer-pane').forEach(p => p.classList.add('hidden'));
      const target = document.getElementById(btn.dataset.pane);
      if (target) target.classList.remove('hidden');
    });
  });
}
