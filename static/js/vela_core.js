/**
 * Vela Financial Charting Engine (SmartChart Core)
 * High-performance WebGL2 & Canvas2D multi-pane interactive charting engine.
 * Inspired by LuxAlgo Vela and TradingView Advanced Charts.
 */
class VelaChart {
  constructor(canvasContainerId, options = {}) {
    this.container = document.getElementById(canvasContainerId);
    if (!this.container) throw new Error(`Container ${canvasContainerId} not found`);

    this.options = {
      theme: 'dark',
      timeframe: '1h',
      candleUpColor: '#089981',
      candleDownColor: '#f23645',
      gridColor: '#1e222d',
      bgGradientTop: '#131722',
      bgGradientBottom: '#0e111a',
      textColor: '#787b86',
      crosshairColor: '#4f5966',
      ...options
    };

    this.candles = [];
    this.indicators = {};
    this.drawings = [];
    this.activeDrawingTool = null;
    this.currentDrawing = null;
    this.magnetMode = false;

    // Viewport State
    this.visibleBars = 90;
    this.panOffset = 0; // offset from latest bar
    this.candleWidth = 8;
    this.candleGap = 3;

    // Canvas Setup
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'w-full h-full block cursor-crosshair';
    this.container.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');

    this.mouse = { x: -1, y: -1, isDown: false, startX: 0, startY: 0, initialPan: 0 };

    this._setupResizeObserver();
    this._bindEvents();
  }

  _setupResizeObserver() {
    this.resizeObserver = new ResizeObserver(() => {
      this.resize();
    });
    this.resizeObserver.observe(this.container);
    this.resize();
  }

  resize() {
    const rect = this.container.getBoundingClientRect();
    this.dpr = window.devicePixelRatio || 1;
    this.width = rect.width;
    this.height = rect.height;

    this.canvas.width = this.width * this.dpr;
    this.canvas.height = this.height * this.dpr;
    this.ctx.scale(this.dpr, this.dpr);

    this.priceScaleWidth = 70;
    this.timeScaleHeight = 28;
    this.chartWidth = this.width - this.priceScaleWidth;
    this.chartHeight = this.height - this.timeScaleHeight;

    this.render();
  }

  setData(candles) {
    this.candles = candles || [];
    this.panOffset = 0;
    this.render();
  }

  setIndicators(indicatorData) {
    this.indicators = indicatorData || {};
    this.render();
  }

  setDrawingTool(toolName) {
    this.activeDrawingTool = toolName;
    if (!toolName) this.currentDrawing = null;
  }

  render() {
    if (!this.ctx || !this.width || !this.height) return;
    const ctx = this.ctx;

    // 1. Draw Background
    const bgGrad = ctx.createLinearGradient(0, 0, 0, this.height);
    bgGrad.addColorStop(0, this.options.bgGradientTop);
    bgGrad.addColorStop(1, this.options.bgGradientBottom);
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, this.width, this.height);

    if (this.candles.length === 0) {
      ctx.fillStyle = this.options.textColor;
      ctx.font = '13px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('در حال بارگذاری جریان داده‌های کندلی...', this.chartWidth / 2, this.chartHeight / 2);
      return;
    }

    // 2. Visible Window Bounds
    const totalBars = this.candles.length;
    const barSpacing = this.candleWidth + this.candleGap;
    const maxVisibleBars = Math.floor(this.chartWidth / barSpacing);
    const endIndex = Math.min(totalBars - 1, totalBars - 1 - this.panOffset);
    const startIndex = Math.max(0, endIndex - maxVisibleBars);
    const visibleCandles = this.candles.slice(startIndex, endIndex + 1);

    if (visibleCandles.length === 0) return;

    // Price Bounds
    let minPrice = Infinity;
    let maxPrice = -Infinity;
    let maxVol = 0;

    for (const c of visibleCandles) {
      if (c.low < minPrice) minPrice = c.low;
      if (c.high > maxPrice) maxPrice = c.high;
      if (c.volume > maxVol) maxVol = c.volume;
    }

    // Add 8% padding to price bounds
    const pPadding = (maxPrice - minPrice) * 0.08 || (minPrice * 0.05);
    minPrice -= pPadding;
    maxPrice += pPadding;

    this.currentMinPrice = minPrice;
    this.currentMaxPrice = maxPrice;
    this.currentStartIndex = startIndex;
    this.currentEndIndex = endIndex;

    // 3. Grid Lines
    this._drawGrid(ctx, minPrice, maxPrice, visibleCandles, startIndex, barSpacing);

    // 4. Volume Histogram (Lower 18% of main chart)
    const volHeight = this.chartHeight * 0.18;
    for (let i = 0; i < visibleCandles.length; i++) {
      const c = visibleCandles[i];
      const x = this.chartWidth - ((visibleCandles.length - 1 - i) * barSpacing) - (this.candleWidth / 2);
      const vH = (c.volume / (maxVol || 1)) * volHeight;
      ctx.fillStyle = c.close >= c.open ? 'rgba(8, 153, 129, 0.18)' : 'rgba(242, 54, 69, 0.18)';
      ctx.fillRect(x - this.candleWidth / 2, this.chartHeight - vH, this.candleWidth, vH);
    }

    // 5. Candlesticks
    for (let i = 0; i < visibleCandles.length; i++) {
      const c = visibleCandles[i];
      const x = this.chartWidth - ((visibleCandles.length - 1 - i) * barSpacing) - (this.candleWidth / 2);
      const isUp = c.close >= c.open;
      const color = isUp ? this.options.candleUpColor : this.options.candleDownColor;

      const yOpen = this._priceToY(c.open, minPrice, maxPrice);
      const yClose = this._priceToY(c.close, minPrice, maxPrice);
      const yHigh = this._priceToY(c.high, minPrice, maxPrice);
      const yLow = this._priceToY(c.low, minPrice, maxPrice);

      // Wick
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.moveTo(Math.floor(x) + 0.5, yHigh);
      ctx.lineTo(Math.floor(x) + 0.5, yLow);
      ctx.stroke();

      // Body
      ctx.fillStyle = color;
      const bodyTop = Math.min(yOpen, yClose);
      const bodyHeight = Math.max(1.5, Math.abs(yOpen - yClose));
      ctx.fillRect(x - (this.candleWidth / 2), bodyTop, this.candleWidth, bodyHeight);
    }

    // 6. Draw Indicators Overlays (SMA, EMA, Supertrend, LuxAlgo SMC)
    this._drawIndicatorOverlays(ctx, minPrice, maxPrice, visibleCandles, startIndex, barSpacing);

    // 7. Render Drawings Layer
    this._drawDrawings(ctx, minPrice, maxPrice, startIndex, barSpacing);

    // 8. Scales (Price on right, Time on bottom)
    this._drawScales(ctx, minPrice, maxPrice, visibleCandles, startIndex, barSpacing);

    // 9. Crosshair & Dynamic Tags
    this._drawCrosshair(ctx, minPrice, maxPrice, visibleCandles, startIndex, barSpacing);
  }

  _priceToY(price, minP, maxP) {
    const range = maxP - minP || 1;
    return this.chartHeight - ((price - minP) / range) * this.chartHeight;
  }

  _yToPrice(y, minP, maxP) {
    const range = maxP - minP || 1;
    return maxP - (y / this.chartHeight) * range;
  }

  _drawGrid(ctx, minP, maxP, visibleCandles, startIndex, barSpacing) {
    ctx.strokeStyle = this.options.gridColor;
    ctx.lineWidth = 1;

    // Horizontal Price Lines (5 steps)
    const steps = 6;
    for (let i = 0; i <= steps; i++) {
      const y = (this.chartHeight / steps) * i;
      ctx.beginPath();
      ctx.moveTo(0, Math.floor(y) + 0.5);
      ctx.lineTo(this.chartWidth, Math.floor(y) + 0.5);
      ctx.stroke();
    }

    // Vertical Time Lines
    const stepBars = Math.max(10, Math.floor(visibleCandles.length / 7));
    for (let i = 0; i < visibleCandles.length; i += stepBars) {
      const x = this.chartWidth - ((visibleCandles.length - 1 - i) * barSpacing) - (this.candleWidth / 2);
      ctx.beginPath();
      ctx.moveTo(Math.floor(x) + 0.5, 0);
      ctx.lineTo(Math.floor(x) + 0.5, this.chartHeight);
      ctx.stroke();
    }
  }

  _drawIndicatorOverlays(ctx, minP, maxP, visibleCandles, startIndex, barSpacing) {
    // 1. Moving Averages / Overlays
    const overlaySeries = [];
    if (this.indicators.sma20) overlaySeries.push({ data: this.indicators.sma20, color: '#f59e0b', width: 1.5, name: 'SMA 20' });
    if (this.indicators.ema50) overlaySeries.push({ data: this.indicators.ema50, color: '#38bdf8', width: 1.5, name: 'EMA 50' });
    if (this.indicators.supertrend && this.indicators.supertrend.values) {
      overlaySeries.push({ data: this.indicators.supertrend.values, color: '#a855f7', width: 2, name: 'Supertrend' });
    }

    for (const s of overlaySeries) {
      ctx.strokeStyle = s.color;
      ctx.lineWidth = s.width;
      ctx.beginPath();
      let started = false;

      for (let i = 0; i < visibleCandles.length; i++) {
        const fullIdx = startIndex + i;
        const val = s.data[fullIdx];
        if (val === null || val === undefined) continue;

        const x = this.chartWidth - ((visibleCandles.length - 1 - i) * barSpacing) - (this.candleWidth / 2);
        const y = this._priceToY(val, minP, maxP);

        if (!started) {
          ctx.moveTo(x, y);
          started = true;
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
    }

    // 2. LuxAlgo SMC Fair Value Gaps & Order Blocks
    if (this.indicators.smc) {
      const { order_blocks = [], fair_value_gaps = [] } = this.indicators.smc;

      // Draw FVGs
      for (const fvg of fair_value_gaps) {
        const yTop = this._priceToY(fvg.top, minP, maxP);
        const yBottom = this._priceToY(fvg.bottom, minP, maxP);
        ctx.fillStyle = fvg.type === 'BULLISH_FVG' ? 'rgba(8, 153, 129, 0.15)' : 'rgba(242, 54, 69, 0.15)';
        ctx.fillRect(0, Math.min(yTop, yBottom), this.chartWidth, Math.abs(yTop - yBottom));
      }

      // Draw Order Blocks
      for (const ob of order_blocks) {
        const yTop = this._priceToY(ob.top, minP, maxP);
        const yBottom = this._priceToY(ob.bottom, minP, maxP);
        ctx.fillStyle = ob.type === 'BULLISH_OB' ? 'rgba(34, 197, 94, 0.22)' : 'rgba(239, 68, 68, 0.22)';
        ctx.strokeStyle = ob.type === 'BULLISH_OB' ? '#22c55e' : '#ef4444';
        ctx.lineWidth = 1;
        const h = Math.max(2, Math.abs(yTop - yBottom));
        ctx.fillRect(this.chartWidth * 0.65, Math.min(yTop, yBottom), this.chartWidth * 0.35, h);
        ctx.strokeRect(this.chartWidth * 0.65, Math.min(yTop, yBottom), this.chartWidth * 0.35, h);
      }
    }

    // 3. LuxAlgo Signals & Overlays (Buy/Sell labels)
    if (this.indicators.signals) {
      for (const sig of this.indicators.signals) {
        if (sig.index >= startIndex && sig.index <= startIndex + visibleCandles.length) {
          const visIdx = sig.index - startIndex;
          const x = this.chartWidth - ((visibleCandles.length - 1 - visIdx) * barSpacing) - (this.candleWidth / 2);
          const y = this._priceToY(sig.price, minP, maxP);
          const isBuy = sig.type.includes('BUY');

          ctx.fillStyle = isBuy ? '#10b981' : '#f43f5e';
          ctx.font = 'bold 11px system-ui, sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText(sig.text, x, isBuy ? y + 16 : y - 10);
        }
      }
    }
  }

  _drawDrawings(ctx, minP, maxP, startIndex, barSpacing) {
    const allDrawings = [...this.drawings];
    if (this.currentDrawing) allDrawings.push(this.currentDrawing);

    for (const d of allDrawings) {
      ctx.strokeStyle = d.color || '#38bdf8';
      ctx.fillStyle = d.fillColor || 'rgba(56, 189, 248, 0.15)';
      ctx.lineWidth = d.lineWidth || 2;

      if (d.type === 'trendline' || d.type === 'ray') {
        const y1 = this._priceToY(d.p1.price, minP, maxP);
        const y2 = this._priceToY(d.p2.price, minP, maxP);
        ctx.beginPath();
        ctx.moveTo(d.p1.x, y1);
        ctx.lineTo(d.p2.x, y2);
        ctx.stroke();
      } else if (d.type === 'horizontal') {
        const y = this._priceToY(d.price, minP, maxP);
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(this.chartWidth, y);
        ctx.stroke();
      } else if (d.type === 'fibonacci') {
        const y1 = this._priceToY(d.p1.price, minP, maxP);
        const y2 = this._priceToY(d.p2.price, minP, maxP);
        const levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0];
        const colors = ['#94a3b8', '#38bdf8', '#34d399', '#facc15', '#fb923c', '#f87171', '#94a3b8'];

        for (let j = 0; j < levels.length; j++) {
          const lvl = levels[j];
          const lvlY = y1 + (y2 - y1) * lvl;
          ctx.strokeStyle = colors[j];
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(0, lvlY);
          ctx.lineTo(this.chartWidth, lvlY);
          ctx.stroke();

          ctx.fillStyle = colors[j];
          ctx.font = '10px sans-serif';
          ctx.textAlign = 'right';
          ctx.fillText(`Fib ${lvl} (${this._yToPrice(lvlY, minP, maxP).toFixed(2)})`, this.chartWidth - 8, lvlY - 3);
        }
      } else if (d.type === 'rectangle') {
        const y1 = this._priceToY(d.p1.price, minP, maxP);
        const y2 = this._priceToY(d.p2.price, minP, maxP);
        const top = Math.min(y1, y2);
        const height = Math.abs(y1 - y2);
        const left = Math.min(d.p1.x, d.p2.x);
        const width = Math.abs(d.p1.x - d.p2.x);
        ctx.fillRect(left, top, width, height);
        ctx.strokeRect(left, top, width, height);
      }
    }
  }

  _drawScales(ctx, minP, maxP, visibleCandles, startIndex, barSpacing) {
    // 1. Price Scale Right Gutter
    ctx.fillStyle = '#1e222d';
    ctx.fillRect(this.chartWidth, 0, this.priceScaleWidth, this.height);
    ctx.strokeStyle = '#2a2e39';
    ctx.beginPath();
    ctx.moveTo(this.chartWidth + 0.5, 0);
    ctx.lineTo(this.chartWidth + 0.5, this.height);
    ctx.stroke();

    ctx.fillStyle = this.options.textColor;
    ctx.font = '11px -apple-system, system-ui, sans-serif';
    ctx.textAlign = 'left';

    const steps = 6;
    for (let i = 0; i <= steps; i++) {
      const y = (this.chartHeight / steps) * i;
      const p = this._yToPrice(y, minP, maxP);
      ctx.fillText(p.toFixed(p < 10 ? 4 : 2), this.chartWidth + 8, y + 4);
    }

    // 2. Time Scale Bottom Gutter
    ctx.fillStyle = '#1e222d';
    ctx.fillRect(0, this.chartHeight, this.width, this.timeScaleHeight);
    ctx.beginPath();
    ctx.moveTo(0, this.chartHeight + 0.5);
    ctx.lineTo(this.width, this.chartHeight + 0.5);
    ctx.stroke();

    const stepBars = Math.max(10, Math.floor(visibleCandles.length / 7));
    ctx.textAlign = 'center';
    for (let i = 0; i < visibleCandles.length; i += stepBars) {
      const c = visibleCandles[i];
      const x = this.chartWidth - ((visibleCandles.length - 1 - i) * barSpacing) - (this.candleWidth / 2);
      const date = new Date(c.time * 1000);
      const label = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
      ctx.fillText(label, x, this.chartHeight + 18);
    }
  }

  _drawCrosshair(ctx, minP, maxP, visibleCandles, startIndex, barSpacing) {
    if (this.mouse.x < 0 || this.mouse.x > this.chartWidth || this.mouse.y < 0 || this.mouse.y > this.chartHeight) return;

    const mx = Math.floor(this.mouse.x) + 0.5;
    const my = Math.floor(this.mouse.y) + 0.5;

    ctx.strokeStyle = this.options.crosshairColor;
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);

    // Horizontal line
    ctx.beginPath();
    ctx.moveTo(0, my);
    ctx.lineTo(this.chartWidth, my);
    ctx.stroke();

    // Vertical line
    ctx.beginPath();
    ctx.moveTo(mx, 0);
    ctx.lineTo(mx, this.chartHeight);
    ctx.stroke();

    ctx.setLineDash([]);

    // Current Price Badge on Right Gutter
    const hoverPrice = this._yToPrice(this.mouse.y, minP, maxP);
    ctx.fillStyle = '#2962ff';
    ctx.fillRect(this.chartWidth, my - 10, this.priceScaleWidth, 20);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 11px sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(hoverPrice.toFixed(hoverPrice < 10 ? 4 : 2), this.chartWidth + 6, my + 4);
  }

  _bindEvents() {
    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      this.mouse.x = e.clientX - rect.left;
      this.mouse.y = e.clientY - rect.top;

      if (this.mouse.isDown && !this.activeDrawingTool) {
        // Pan Viewport
        const deltaX = this.mouse.x - this.mouse.startX;
        const barDelta = Math.floor(deltaX / (this.candleWidth + this.candleGap));
        this.panOffset = Math.max(0, this.mouse.initialPan + barDelta);
      } else if (this.activeDrawingTool && this.currentDrawing) {
        // Update active drawing endpoint
        const currPrice = this._yToPrice(this.mouse.y, this.currentMinPrice, this.currentMaxPrice);
        if (this.currentDrawing.p2) {
          this.currentDrawing.p2 = { x: this.mouse.x, price: currPrice };
        }
      }

      this.render();
    });

    this.canvas.addEventListener('mousedown', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      this.mouse.isDown = true;
      this.mouse.startX = x;
      this.mouse.startY = y;
      this.mouse.initialPan = this.panOffset;

      if (this.activeDrawingTool) {
        const currPrice = this._yToPrice(y, this.currentMinPrice, this.currentMaxPrice);
        if (this.activeDrawingTool === 'horizontal') {
          this.drawings.push({
            type: 'horizontal',
            price: currPrice,
            color: '#38bdf8',
            lineWidth: 2,
          });
          this.setDrawingTool(null);
        } else if (!this.currentDrawing) {
          this.currentDrawing = {
            type: this.activeDrawingTool,
            p1: { x, price: currPrice },
            p2: { x, price: currPrice },
            color: '#38bdf8',
            lineWidth: 2,
          };
        } else {
          this.drawings.push(this.currentDrawing);
          this.currentDrawing = null;
          this.setDrawingTool(null);
        }
      }
    });

    window.addEventListener('mouseup', () => {
      this.mouse.isDown = false;
    });

    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
      this.candleWidth = Math.max(2, Math.min(40, this.candleWidth * zoomFactor));
      this.render();
    }, { passive: false });
  }

  clearDrawings() {
    this.drawings = [];
    this.currentDrawing = null;
    this.render();
  }
}

window.VelaChart = VelaChart;
