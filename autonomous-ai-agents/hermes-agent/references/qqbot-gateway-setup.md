# QQ Bot Gateway Setup

## Prerequisites
- `pip install qrcode` in the Hermes venv (for terminal QR display)
- QQ Bot registered at https://q.qq.com

## Method 1: QR Code Scan (Recommended)

The interactive `hermes gateway setup` menu is hard to control via terminal automation (arrow keys, selection numbers don't reliably map to menu items). Instead, call the onboard module directly:

```python
#!/usr/bin/env python3
"""QQ Bot QR code setup - direct call to onboard module."""
import sys
sys.path.insert(0, '/home/admin/.hermes/hermes-agent')

from gateway.platforms.qqbot.onboard import qr_register

result = qr_register(timeout_seconds=300)

if result:
    print(f"App ID: {result['app_id']}")
    print(f"Client Secret: {result['client_secret']}")
    print(f"User OpenID: {result['user_openid']}")
```

Save as `/tmp/qqbot_setup.py` and run in a background PTY process with watch_patterns for "scan complete", "App ID", "expired", "error".

## Method 2: Manual Config

If you already have App ID and Client Secret, skip the QR flow and configure directly.

## Configuration (IMPORTANT)

**Do NOT add `platforms:` section to config.yaml** — it causes `TypeError: string indices must be integers` because the gateway config loader expects a specific dict structure that conflicts with top-level YAML.

**Correct approach: use environment variables in `~/.hermes/.env`:**
```
QQ_APP_ID=1904042322
QQ_CLIENT_SECRET=XXXXXXXXXXXXXXXXXXXXXXXX
```

The gateway reads these automatically via `os.getenv("QQ_APP_ID")` and `os.getenv("QQ_CLIENT_SECRET")` in `gateway/platforms/qqbot/adapter.py`.

The `platform_toolsets` section in config.yaml should already have `qqbot: [hermes-qqbot]` — that part is fine. Only the `platforms:` top-level key is problematic.

## Pairing Approval

After first message from a new user, the bot responds with a pairing code:
```
Your pairing code: XXXXXXXX
hermes pairing approve qqbot XXXXXXXX
```

Run the approve command to authorize the user:
```bash
hermes pairing approve qqbot TSAY9N9G
```

## Restart Gateway After Config Changes

```bash
sudo systemctl restart hermes-gateway
```

Note: `hermes gateway restart` requires root. Use `sudo systemctl restart hermes-gateway`.

## Custom Stop Keyword via quick_commands

To add a custom stop keyword (e.g., "停" for Chinese users) that interrupts the bot:

In `~/.hermes/config.yaml`, replace `quick_commands: {}` with:
```yaml
quick_commands:
  停:
    type: alias
    target: stop
```

Restart gateway after changes.

## Connection Modes: WebSocket vs Webhook

Hermes QQ Bot uses **WebSocket mode** (long-poll connection to QQ servers). This is the default and recommended mode.

⚠️ **Do NOT configure a callback URL** in the QQ developer platform (q.qq.com → 配置事件回调地址). The platform warns: "成功配置 https 回调地址之后，基于 WebSocket 的回调服务不再支持" — once you set a callback URL, WebSocket mode is permanently disabled for that bot.

| | WebSocket (default) | Webhook (callback) |
|--|--|--|
| How it works | Bot connects to QQ servers | QQ pushes to your HTTPS endpoint |
| Public URL needed | ❌ No | ✅ Yes (HTTPS + domain) |
| Stability | Good | Better for high-traffic bots |
| Setup | QR scan or env vars | Requires nginx + SSL + callback URL config |

If you accidentally configured a callback URL and broke WebSocket mode, remove the callback URL in the developer platform and restart the gateway.

## Known Issues
- UTF-8 warning "Failed to write runtime status (connected) for qqbot" is cosmetic — QQ Bot still works
- QQ Bot file transfer: PDF and documents may not auto-download. See `qqbot-file-transfer.md` for workarounds.
