# 🚀 راهنمای جامع استقرار و مانیتورینگ عملیاتی: سامانه SmartChart

**نسخه:** 1.0.0 Stable  
**محیط اجرا:** Linux (Ubuntu 24.04 LTS / Debian 12 / RackNerd VPS)  
**سرویس:** FastAPI + Uvicorn + Vela WebGL2 + Cloudflare Tunnel  
**مخزن کد گیت‌هاب:** [https://github.com/98H/nexus-smartchart](https://github.com/98H/nexus-smartchart)  

---

## ۱. درگاه‌ها و پیوندهای دسترسی زنده (Live Access URLs)

| عنوان درگاه | آدرس دسترسی | وضعیت | پروتکل |
|---|---|---|---|
| **درگاه عمومی کلودفلر (Public Tunnel)** | `https://advances-own-tree-insert.trycloudflare.com/preview/prod-smartchart-a7791f/` | فعال ✓ (HTTP 200) | HTTPS |
| **درگاه لوکال ریورس پروکسی (Internal Gateway)** | `http://127.0.0.1:8095/preview/prod-smartchart-a7791f/` | فعال ✓ (HTTP 200) | HTTP |
| **پورت مستقیم سرویس (Direct Daemon Port)** | `http://127.0.0.1:8100/` | فعال ✓ (HTTP 200) | HTTP |
| **اندپوینت سلامت‌سنجی (Health Check API)** | `http://127.0.0.1:8100/health` | `{"status":"ok"}` | REST JSON |

---

## ۲. پیش‌نیازهای نصب و راه‌اندازی (Prerequisites)

```bash
# پایتون نسخه ۳.۱۱ یا بالاتر
python3 --version

# ایجاد و فعال‌سازی محیط ایزوله
python3 -m venv .venv
source .venv/bin/activate

# نصب نیازمندی‌های سیستم
pip install fastapi uvicorn pydantic numpy pandas requests pytest
```

---

## ۳. دستورات راه‌اندازی و مدیریت سرویس (Operations Guide)

### ۳.۱. اجرای دستی در پیش‌زمینه (Foreground Development):
```bash
cd /root/nexus-agent-graph/workspaces/prod-smartchart-a7791f
python3 app.py --port 8100 --host 127.0.0.1
```

### ۳.۲. اجرای به عنوان پردازه پس‌زمینه (Background Daemon):
```bash
cd /root/nexus-agent-graph/workspaces/prod-smartchart-a7791f
nohup python3 app.py --port 8100 > logs/deploy.log 2>&1 &
echo $! > deploy.pid
```

### ۳.۳. بررسی سلامت سرویس (Verification):
```bash
# تست درگاه سلامت
curl -s http://127.0.0.1:8100/health

# تست دریافت کندل‌ها
curl -s "http://127.0.0.1:8100/api/market/klines?symbol=BTCUSDT&interval=1h&limit=5"
```

### ۳.۴. اجرای تست‌های خودکار (Automated Test Suite):
```bash
cd /root/nexus-agent-graph/workspaces/prod-smartchart-a7791f
pytest tests/ -v
```

---

## ۴. ساختار لاگ‌ها و عیب‌یابی (Log Management)

- فایل ثبت رویدادهای اجرا: `/root/nexus-agent-graph/workspaces/prod-smartchart-a7791f/logs/deploy.log`
- شناسه پردازه فعال: `/root/nexus-agent-graph/workspaces/prod-smartchart-a7791f/deploy.pid`
- مانیتور لاگ‌های زنده:
  ```bash
  tail -f /root/nexus-agent-graph/workspaces/prod-smartchart-a7791f/logs/deploy.log
  ```
