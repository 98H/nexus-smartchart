# Deployment & Operations Guide: SmartChart

## 🚀 Live Access URLs
- **Public Preview URL:** [https://river-alternatives-isolated-parker.trycloudflare.com/preview/prod-smartchart-a7791f/](https://river-alternatives-isolated-parker.trycloudflare.com/preview/prod-smartchart-a7791f/)
- **Local Gateway Path:** [/preview/prod-smartchart-a7791f/](/preview/prod-smartchart-a7791f/)
- **Internal Port:** `8101`
- **Process PID:** `3395285`
- **Runtime Engine:** `fastapi`
- **Health Status:** `FAILED`
- **Deployed Timestamp:** `2026-09-17T20:52:34.173445+00:00`

## 📋 Execution Command
```bash
/usr/local/lib/hermes-agent/venv/bin/python3 -m uvicorn app:app --host 127.0.0.1 --port 8101
```

## 🩺 Health Check Verification
```bash
curl -I http://127.0.0.1:8101/
```

## 📜 Live Deployment Logs
Logs are stored at `/root/nexus-agent-graph/workspaces/prod-smartchart-a7791f/logs/deploy.log`.
