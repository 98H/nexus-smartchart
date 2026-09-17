# Deployment & Operations Guide: SmartChart

## 🚀 Live Access & URLs
- **Live Public Access URL:** [/preview/prod-smartchart-a7791f/](/preview/prod-smartchart-a7791f/)
- **Internal Port:** `0`
- **Runtime Engine:** `python_preview`
- **Deployment Status:** `DEPLOYED / ACTIVE`
- **Timestamp:** `2026-09-17T19:27:55.437109+00:00`

## 🛠️ Management & Service Control
### Launch Command
```bash
python3 app.py --port 0
```

### Health Check Probe
```bash
curl -I http://127.0.0.1:0/
```

### Systemd Service Template
```ini
[Unit]
Description=SmartChart Service
After=network.target

[Service]
Type=simple
WorkingDirectory=/root/nexus-agent-graph/workspaces/prod-smartchart-a7791f
ExecStart=/usr/bin/python3 /root/nexus-agent-graph/workspaces/prod-smartchart-a7791f/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

## 🔒 Production Security Protocols
- HTTP-only reverse proxy via Nexus Gateway.
- Dedicated port allocation with zero port conflict.
