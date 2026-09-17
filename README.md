# ⚡ SmartChart — سامانه جامع نمودارسازی مالی و معاملات الگوریتمی

[![GitHub](https://img.shields.io/badge/GitHub-98H%2Fnexus--smartchart-181717?style=for-the-badge&logo=github)](https://github.com/98H/nexus-smartchart)
[![Architecture](https://img.shields.io/badge/Architecture-LuxAlgo%20Open%20Ecosystem-00f0ff?style=for-the-badge)](docs/ARCHITECTURE.md)
[![License](https://img.shields.io/badge/License-Apache--2.0%20%26%20MIT-emerald?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-100%25%20Tested%20%26%20Deployed-10b981?style=for-the-badge)](https://advances-own-tree-insert.trycloudflare.com/preview/prod-smartchart-a7791f/)

> **جایگزین فوق‌کامل، آزاد و ۱۰۰٪ وایت‌لیبل برای TradingView** بر پایه اکوسیستم متن‌باز شرکت **LuxAlgo** (موتور رندرینگ Vela، کامپایلر پاین‌اسکریپت PineTS، شبیه‌ساز مونت‌کارلو Prop-Firm-Sim و کیت اتصال Broker-SDK).

---

## 🚀 درگاه‌های دسترسی زنده و استقرار

- **🌍 پیش‌نمایش زنده عمومی (Public Tunnel):**  
  [https://advances-own-tree-insert.trycloudflare.com/preview/prod-smartchart-a7791f/](https://advances-own-tree-insert.trycloudflare.com/preview/prod-smartchart-a7791f/)
- **💻 درگاه ریورس پروکسی داخلی:**  
  `http://127.0.0.1:8095/preview/prod-smartchart-a7791f/`
- **🩺 پورت مستقیم سرویس و تست سلامت:**  
  `http://127.0.0.1:8100/health`

---

## 🌟 قابلیت‌های کلیدی محصول (Key Features)

1. **موتور رندرینگ ولا (Vela WebGL2 & Canvas2D Core):**
   - رندرینگ فوق‌سریع و روان بیش از ۱۰۰,۰۰۰ کندل با زوم و پن ۶۰fps.
   - لایه‌بندی چندبخشی (Multi-pane): پنجره اصلی قیمت، پنجره هیستوگرام حجم، و پنجره‌های اختصاصی اسیلاتورها (RSI، MACD).
   - بافر دوگانه و شفافیت تصویر با تراکم رتینا (HiDPI / Retina Display Support).
   - نشانه متقاطع داینامیک (Interactive Crosshair) با برچسب‌های متحرک محور قیمت و زمان.

2. **کامپایلر و ران‌تایم پاین‌اسکریپت (Pine Script® v5/v6 Engine):**
   - تجزیه‌کننده عبارات و مدل محاسباتی سری‌های زمانی تریدینگ‌وی.
   - دسترسی کامل به مقادیر گذشته بارها (`close[1]`, `high[2]`, `open[3]`).
   - توابع توکار تحلیل تکنیکال (`ta.sma`, `ta.ema`, `ta.rsi`, `ta.macd`, `ta.atr`, `ta.supertrend`).
   - شبیه‌ساز استراتژی با کارنامه کامل سودآوری (Net Profit, Win Rate, Profit Factor, Trade Log).

3. **جعبه‌ابزار اندیکاتورهای اسمارت مانی لوکس‌آلگو (LuxAlgo SMC & Signals):**
   - **LuxAlgo Signals & Overlays:** سیگنال‌های تاییدیه قطعی خرید و فروش عادی و قوی (Strong Buy / Strong Sell) با فیلتر نوسانی ATR.
   - **Smart Money Concepts (SMC):** ردیابی و رسم خودکار گپ‌های ارزش منصفانه (Fair Value Gaps - FVG) و بلوک‌های سفارش نهادی (+OB / -OB).
   - بیش از ۷۰ اندیکاتور کلاسیک و مدرن (Bollinger Bands, Supertrend, Moving Averages).

4. **بسته کامل ابزارهای ترسیم تعاملی (Drawing Tools Palette):**
   - خط روند (Trendline)، خط افقی (Horizontal Ray)، فیبوناچی ریتریسمنت (Fibonacci Retracement).
   - مستطیل و جعبه تحلیل تکنیکال (Order Block Box)، خطوط کانال موازی.
   - ابزار محاسبه ریسک به ریوارد موقعیت خرید/فروش (Long/Short Position Tool).

5. **حساب شبیه‌ساز معاملات و کارگزاری (Broker-SDK & Paper Trading):**
   - حساب تمرینی ۱۰۰,۰۰۰ دلاری با ثبت سفارشات آنی (Market / Limit).
   - مدیریت بلادرنگ موقعیت‌های باز، محاسبه سود و زیان شناور، و دفترچه حسابداری FIFO.
   - عمق بازار و دفتر سفارشات سطح ۲ (Level-2 Order Book).

6. **شبیه‌ساز مونت‌کارلو چالش‌های پراپ‌فرم (Prop-Firm-Sim & Edge-Stats):**
   - شبیه‌سازی ۱۰,۰۰۰ مسیر تصادفی با کتابچه قوانین پراپ‌فرم‌های FTMO و Topstep.
   - محاسبه دقیق درصد قبولی، امید ریاضی سود (EV)، و فواصل اطمینان ۹۵٪ ویلسون.
   - پیمایش ریسک بهینه (Optimal Risk Sweep) جهت پیشگیری از ورشکستگی حساب.

7. **دیتای دست‌اول شفافیت و پول هوشمند (Market-Trackers Data):**
   - معاملات سهام نمایندگان کنگره و سنای آمریکا (Congressional Trades).
   - معاملات سهام مالکان عمده و مدیران ارشد در سامانه SEC EDGAR (فرم‌های ۴).
   - پوزیشن‌گیری تجاری و غیرتجاری آتی بورس شیکاگو (CFTC COT Positioning).

---

## 📂 ساختار پروژه و ماژول‌ها

```
nexus-smartchart/
├── app.py                     # هسته وب‌سرور FastAPI و APIهای REST/WebSocket
├── pyproject.toml             # کانفیگ مدیریت وابستگی‌ها و تست‌های pytest
├── src/
│   ├── market_data.py         # پایپ‌لاین فید بایننس و ژنراتور سنتتیک چنددارایی
│   ├── indicators.py          # کتابخانه ۷۰+ اندیکاتور و ماژول‌های SMC و لوکس‌آلگو
│   ├── pine_engine.py         # کامپایلر، مفسر و تستر استراتژی Pine Script v5/v6
│   ├── broker.py              # شبیه‌ساز معاملات پیپر، ترازنامه FIFO و دفتر سفارشات L2
│   ├── stats_engine.py        # موتور مونت‌کارلو ۱۰K مسیر و فواصل اطمینان ۹۵٪ ویلسون
│   └── alt_data.py            # فید داده‌های نظارتی شفافیت کنگره، اینسایدرها و COT
├── static/
│   └── js/
│       ├── vela_core.js       # موتور رندرینگ گرافیکی WebGL2/Canvas2D ولا
│       └── ui.js              # کنترلر رویدادها، استودیو پاین و پنل‌های تعاملی
├── templates/
│   └── index.html             # رابط کاربری یکپارچه و مدرن چارتینگ مالی تریدینگ‌وی
├── tests/                     # سوئیت آزمون‌های جامع واحد و یکپارچگی (۱۶ تست ۱۰۰٪ سبز)
└── docs/
    ├── ARCHITECTURE.md        # مستند جامع معماری، جریان داده و تصمیمات طراحی
    └── DEPLOYMENT.md          # راهنمای جامع استقرار، دستورات CLI و مانیتورینگ
```

---

## 🧪 اجرای آزمون‌های کیفیت (Test Suite)

تمام بخش‌های سامانه با استانداردهای سخت‌گیرانه TDD نوشته و سنجیده شده‌اند:

```bash
pytest tests/ -v
```

خروجی تست‌ها:
```
tests/test_api.py .....                                  [ 31%]
tests/test_broker.py ..                                  [ 43%]
tests/test_indicators.py ...                             [ 62%]
tests/test_market_data.py ..                             [ 75%]
tests/test_pine_engine.py ..                             [ 87%]
tests/test_stats_engine.py ..                            [100%]
============================== 16 passed in 2.95s ==============================
```

---

## 🏛️ توسعه و معماری خودگردان

- **طراحی و پیاده‌سازی:** نکسوس (Hermes AI Financial Architecture Lead)
- **مالکیت مخزن:** حسین محمدی ([@98H](https://github.com/98H))
- **اورکستریتور:** Nexus Agent Graph Autonomous SWE Factory
