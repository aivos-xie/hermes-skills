# Weixin (WeChat) QR Login Setup — Workarounds

## Problem: `hermes gateway setup` interactive wizard is hard to drive

The setup wizard uses a curses-based interactive picker. On headless/SSH sessions
or when piping input, the arrow-key navigation doesn't work (escape sequences
are sent as literal text). PTY mode via `terminal(pty=True)` also struggles.

## Solution: Call `qr_login()` directly from Python

Write a two-phase script:

### Phase 1: Get QR URL
```python
import asyncio, aiohttp, sys, os, json, time
sys.path.insert(0, os.path.expanduser("~/.hermes/hermes-agent"))
from gateway.platforms.weixin import (
    ILINK_BASE_URL, EP_GET_BOT_QR, EP_GET_QR_STATUS,
    _api_get, _make_ssl_connector, QR_TIMEOUT_MS,
    save_weixin_account
)

async def get_qr():
    async with aiohttp.ClientSession(trust_env=True, connector=_make_ssl_connector()) as session:
        qr_resp = await _api_get(session, base_url=ILINK_BASE_URL,
                                  endpoint=f"{EP_GET_BOT_QR}?bot_type=3", timeout_ms=QR_TIMEOUT_MS)
        qrcode_value = str(qr_resp.get("qrcode") or "")
        qrcode_url = str(qr_resp.get("qrcode_img_content") or "")
        # Save state for polling
        with open("/tmp/weixin_login_state.json", "w") as f:
            json.dump({"qrcode_value": qrcode_value, "qrcode_url": qrcode_url}, f)
        print(f"QR_URL={qrcode_url}")

asyncio.run(get_qr())
```

### Phase 2: Poll for scan (run in background)
```python
async def poll():
    with open("/tmp/weixin_login_state.json") as f:
        state = json.load(f)
    qrcode_value = state["qrcode_value"]
    # ... poll EP_GET_QR_STATUS until status == "confirmed"
    # On confirm: save_weixin_account() + write WEIXIN_* to .env

asyncio.run(poll())
```

Run phase 1 to get URL, start phase 2 in background (`terminal(background=True, notify_on_complete=True)`),
then tell user to open the URL in WeChat or scan the QR.

## Critical: Set DM policy after login

After QR login, `WEIXIN_DM_POLICY` defaults to `open` but the account config
may not include it. Without it, all inbound DMs are rejected as "Unauthorized user".

**Always add to `.env` after login:**
```
WEIXIN_DM_POLICY=open
```

Then restart gateway: `sudo systemctl restart hermes-gateway`

## iLink Bot limitations

- QR login creates an **iLink bot identity** (e.g. `6b86ceb9ace7@im.bot`), NOT a regular WeChat account
- The bot **cannot be invited into ordinary WeChat groups**
- Group messages are typically NOT delivered to the bot
- Only DMs work reliably
- Requires `aiohttp` and `cryptography` Python packages

## Env vars written by the login script

```
WEIXIN_ACCOUNT_ID=xxx@im.bot
WEIXIN_TOKEN=xxx@im.bot:xxxxxx
WEIXIN_HOME_CHANNEL=user_id@im.wechat
WEIXIN_DM_POLICY=open
```

## Gateway restart

After env changes, restart is required:
```bash
sudo systemctl restart hermes-gateway
```

Note: `hermes gateway restart` may fail with "requires root" — use `sudo systemctl` instead.
