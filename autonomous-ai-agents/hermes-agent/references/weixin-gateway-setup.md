# Weixin (WeChat) Gateway Setup - Automation Reference

## When to Use
When setting up or troubleshooting the Weixin/WeChat iLink Bot adapter for Hermes Agent.

## Key Pitfall: Interactive Setup Cannot Be Automated via PTY
`hermes gateway setup` uses a curses-based picker that doesn't accept escape sequences through `process(write)`. You **cannot** drive it programmatically via PTY. Use the direct Python script approach instead.

## Prerequisites
- Python packages: `aiohttp` and `cryptography` (already in Hermes venv)
- `qrcode` package for terminal QR display (also in venv)

## Two-Phase QR Login Script

### Why Two Phases?
When user is on mobile (JuiceSSH etc.), they can't scan a QR displayed on the same screen. Phase 1 gets the URL, phase 2 polls for scan confirmation.

### Phase 1: Get QR URL
```python
#!/usr/bin/env python3
import asyncio, aiohttp, sys, os, json
sys.path.insert(0, os.path.expanduser("~/.hermes/hermes-agent"))
from gateway.platforms.weixin import (
    ILINK_BASE_URL, EP_GET_BOT_QR, _api_get, _make_ssl_connector, QR_TIMEOUT_MS
)

async def main():
    async with aiohttp.ClientSession(trust_env=True, connector=_make_ssl_connector()) as session:
        qr_resp = await _api_get(session, base_url=ILINK_BASE_URL,
                                  endpoint=f"{EP_GET_BOT_QR}?bot_type=3", timeout_ms=QR_TIMEOUT_MS)
        qrcode_value = str(qr_resp.get("qrcode") or "")
        qrcode_url = str(qr_resp.get("qrcode_img_content") or "")
        with open("/tmp/weixin_login_state.json", "w") as f:
            json.dump({"qrcode_value": qrcode_value, "qrcode_url": qrcode_url}, f)
        print(f"QR_URL={qrcode_url}")

asyncio.run(main())
```

### Phase 2: Poll for Confirmation (run in background)
```python
#!/usr/bin/env python3
import asyncio, aiohttp, sys, os, time, json
sys.path.insert(0, os.path.expanduser("~/.hermes/hermes-agent"))
from gateway.platforms.weixin import (
    ILINK_BASE_URL, EP_GET_BOT_QR, EP_GET_QR_STATUS,
    _api_get, _make_ssl_connector, QR_TIMEOUT_MS, save_weixin_account
)

async def main():
    hermes_home = os.path.expanduser("~/.hermes")
    with open("/tmp/weixin_login_state.json") as f:
        state = json.load(f)
    qrcode_value = state["qrcode_value"]
    async with aiohttp.ClientSession(trust_env=True, connector=_make_ssl_connector()) as session:
        current_base_url = ILINK_BASE_URL
        deadline = time.monotonic() + 480
        refresh_count = 0
        while time.monotonic() < deadline:
            try:
                status_resp = await _api_get(session, base_url=current_base_url,
                    endpoint=f"{EP_GET_QR_STATUS}?qrcode={qrcode_value}", timeout_ms=QR_TIMEOUT_MS)
            except:
                await asyncio.sleep(2); continue
            status = str(status_resp.get("status") or "wait")
            if status == "confirmed":
                account_id = str(status_resp.get("ilink_bot_id") or "")
                token = str(status_resp.get("bot_token") or "")
                base_url = str(status_resp.get("baseurl") or ILINK_BASE_URL)
                user_id = str(status_resp.get("ilink_user_id") or "")
                save_weixin_account(hermes_home, account_id=account_id,
                                   token=token, base_url=base_url, user_id=user_id)
                # Write .env
                env_path = os.path.join(hermes_home, ".env")
                with open(env_path) as f: lines = f.readlines()
                lines = [l for l in lines if not l.strip().startswith("WEIXIN_")]
                lines += [f"\nWEIXIN_ACCOUNT_ID={account_id}\n",
                          f"WEIXIN_TOKEN={token}\n"]
                if user_id: lines.append(f"WEIXIN_HOME_CHANNEL={user_id}\n")
                with open(env_path, 'w') as f: f.writelines(lines)
                print(f"OK account_id={account_id}")
                return
            elif status == "expired":
                refresh_count += 1
                if refresh_count > 3: print("FAIL"); sys.exit(1)
                # Re-fetch QR (same as phase 1)
                qr_resp = await _api_get(session, base_url=ILINK_BASE_URL,
                    endpoint=f"{EP_GET_BOT_QR}?bot_type=3", timeout_ms=QR_TIMEOUT_MS)
                qrcode_value = str(qr_resp.get("qrcode") or "")
                state["qrcode_value"] = qrcode_value
                state["qrcode_url"] = str(qr_resp.get("qrcode_img_content") or "")
                with open("/tmp/weixin_login_state.json", "w") as f: json.dump(state, f)
            elif status == "scaned_but_redirect":
                rh = str(status_resp.get("redirect_host") or "")
                if rh: current_base_url = f"https://{rh}"
            await asyncio.sleep(2)

asyncio.run(main())
```

## Critical Post-Setup Step: Set DM Policy
After QR login succeeds, `WEIXIN_DM_POLICY=open` MUST be added to `~/.hermes/.env`.
Without it, the default policy rejects all incoming messages as "Unauthorized user".

```bash
echo 'WEIXIN_DM_POLICY=open' >> ~/.hermes/.env
sudo systemctl restart hermes-gateway
```

## iLink Bot Limitations
- Bot identity is `xxx@im.bot`, NOT a regular WeChat account
- Cannot be invited into ordinary WeChat groups
- Group messages typically not delivered (iLink limitation, not Hermes)
- Best used for DMs only

## Troubleshooting
| Symptom | Fix |
|---------|-----|
| "Unauthorized user" in logs | Add `WEIXIN_DM_POLICY=open` to `.env`, restart gateway |
| QR expired 3x | Script auto-refreshes up to 3 times, then exits. Re-run. |
| `aiohttp and cryptography required` | Already in Hermes venv, no action needed |
| Session expired (errcode=-14) | Re-run QR login flow |
