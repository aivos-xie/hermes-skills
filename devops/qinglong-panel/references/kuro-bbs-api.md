# 库街区 (Kuro BBS) API — 鸣潮/战双签到

## Overview

库街区 is Kuro Games' community app (for 鸣潮/Wuthering Waves and 战双/Punishing Gray Raven).
Supports daily sign-in via API with a bearer token.

**Source:** [TomyJan/Kuro-API-Collection](https://github.com/TomyJan/Kuro-API-Collection) (master branch)

## Authentication

Token-based. Pass token in request header on all authenticated calls.

### Send SMS Code

```
POST https://api.kurobbs.com/user/getSmsCode

Headers:
  osVersion: Android
  devCode: 073A9EFAC18FC50616DD15808DAE719DBCB904B7
  countryCode: CN
  source: android
  version: 2.2.0
  versionCode: 2200
  channelId: 2
  Content-Type: application/x-www-form-urlencoded
  User-Agent: okhttp/3.11.0

Body: mobile=PHONE_NUMBER&geeTestData=

Response: {"code":200,"data":{"geeTest":true/false}}
```

**CRITICAL PITFALL:** `geeTest: true` means captcha IS required and SMS was NOT sent.
`geeTest: false` means SMS was sent successfully. The API always returns code 200 regardless.

**As of 2026-06, GeeTest captcha is required for SMS sending from server IPs.**
**As of 2026-06, GeeTest captcha is required for SMS sending from server IPs.** Cannot automate token acquisition server-side. GeeTest v4 proxy approach (serving SDK locally) was attempted but the captcha UI doesn't render even with all resources correctly proxied.

**Recommended token acquisition (ranked by ease):**
1. **Reverse proxy (best for phone users):** Build a Node.js server that proxies `kurobbs.com`, injects JS to intercept login API response AND polls cookie/localStorage for JWT token. User just opens `http://YOUR_IP:PORT` and logs in normally. Token auto-displayed on success page for user to copy. Key injection points: override `fetch()` and `XMLHttpRequest.open()` to redirect `api.kurobbs.com` → `/__api/*`, plus `setInterval` polling `document.cookie` for `token=` or `user_token=` (JWT starts with `eyJ`, length > 20). Mobile detection by kurobbs.com may show download prompt — check `pre-route.js` behavior. See `references/geetest-v4-proxy.md` for complete implementation.
2. **PC browser:** Login on `kurobbs.com` → F12 → Console → `document.cookie.match(/token=([^;]+)/)?.[1]` → copy result
3. **Phone browser:** Login on `kurobbs.com` → same JS extraction (paste in address bar)
4. **Phone app + packet capture:** Install HttpCanary/Reqable → capture API traffic → extract token from `sdkLogin` response

**Key headers for sign-in APIs (APP token required):**
```
osversion: Android, devcode: 2fba3859fe9bfe9099f2696b8648c2c6, version: 1.0.9, versioncode: 1090
```
Do NOT mix with `getSmsCode` headers (version: 2.2.0, versionCode: 2200) — they use different devCode values.

### Login with SMS Code

```
POST https://api.kurobbs.com/user/sdkLogin

Headers:
  osversion: Android
  devcode: 2fba3859fe9bfe9099f2696b8648c2c6
  distinct_id: 765485e7-30ce-4496-9a9c-a2ac1c03c02c
  countrycode: CN
  source: android
  lang: zh-Hans
  version: 1.0.9
  versioncode: 1090
  content-type: application/x-www-form-urlencoded
  user-agent: okhttp/3.10.0

Body: code=SMS_CODE&devCode=2fba3859fe9bfe9099f2696b8648c2c6&gameList=&mobile=PHONE

Response: {"code":200,"data":{"token":"eyJhbG...","userId":"10065669","userName":"...",...}}
```

**Pitfall:** APP token and Web token are NOT interchangeable. Web tokens (from `user_token` cookie on kurobbs.com) return code 220 on all APP APIs. APP token needed for sign-in APIs — must come from `sdkLogin` endpoint.

## Sign-in APIs (require APP token in header)

### Get user info

```
POST https://api.kurobbs.com/user/mineV2
Body: type=1
```

### Get game roles

```
POST https://api.kurobbs.com/gamer/role/default
Body: queryUserId=USER_ID
```

### Reward sign-in (签到奖励)

```
POST https://api.kurobbs.com/encourage/signIn/v2
Body: gameId=2&serverId=SERVER_ID&roleId=ROLE_ID&userId=USER_ID&reqMonth=06
```

- `reqMonth`: 2-digit month (e.g. "06" for June)
- `gameId`: 2 for 鸣潮, 1 for 战双

### Community sign-in (社区签到)

```
POST https://api.kurobbs.com/user/signIn
Body: gameId=2
```

## Common Headers for Authenticated Requests

```javascript
{
  'osversion': 'Android',
  'devcode': '2fba3859fe9bfe9099f2696b8648c2c6',
  'countrycode': 'CN',
  'ip': '10.0.2.233',
  'model': '2211133C',
  'source': 'android',
  'lang': 'zh-Hans',
  'version': '1.0.9',
  'versioncode': '1090',
  'token': TOKEN,  // from login response
  'content-type': 'application/x-www-form-urlencoded; charset=utf-8',
  'accept-encoding': 'gzip',
  'user-agent': 'okhttp/3.10.0'
}
```

## Working Script Reference

See `leeezep/kurobbs_auto_checkin` on GitHub for a complete Python implementation.
The script uses requests + loguru + pydantic. A lightweight Node.js version with just `https` module also works for QingLong.

## GeeTest v4 Captcha — Reverse Proxy Solution (WORKING)

SMS sending requires GeeTest v4 captcha. Server IPs always get `geeTest: true`.

**Working solution**: Build a Node.js reverse proxy server (port 5701) that:
1. Proxies the entire `www.kurobbs.com` website transparently
2. Injects JS intercept script at START of `<head>` to override fetch/XHR
3. Intercepts `sdkLogin` / `sdkLoginForH5` responses to capture token automatically
4. Also polls cookies/localStorage/sessionStorage for JWT token as fallback
5. Saves token to QingLong env var `KURO_TOKEN` via internal `/__capture` endpoint
6. User opens `http://YOUR_IP:5701` on phone, logs in normally, token auto-saved

**PITFALL: Do NOT try local GeeTest SDK hosting** — The 1MB obfuscated main JS has anti-proxy checks. Captcha UI never renders even with all resources correctly proxied. Use reverse proxy of kurobbs.com instead.

**PITFALL: SPA needs ALL CDN domains proxied** — kurobbs.com is a Vue SPA. HTML comes from `www.kurobbs.com` but CSS/JS come from `web-static.kurobbs.com` and images from `prod-alicdn-community.kurobbs.com`. Only proxying the main domain results in a blank/broken page. Must proxy all 3 CDN domains + API. See `references/geetest-v4-proxy.md` "CDN Domains" section for complete route table.

**Verified working (2026-06-09):** Full SPA loads on mobile with all 4 domain routes.

**PITFALL: CDN returns `content-length: 0`** — ByteDance CDN (Byte-nginx) returns `content-length: 0` in headers even when sending actual content. MUST delete `content-length` from proxied headers and let Node.js recalculate. Otherwise browser shows blank/garbled page.

**PITFALL: Missing charset** — Upstream sends `content-type: text/html` without `charset=utf-8`. Mobile browsers may pick wrong encoding → 乱码. Always append `; charset=utf-8`.

**PITFALL: Strip security headers** — Remove `content-security-policy`, `x-frame-options`, `strict-transport-security`, `content-encoding`, `transfer-encoding`. Rewrite `set-cookie` to strip `domain=` and `secure` flags.

See `references/geetest-v4-proxy.md` for complete implementation with intercept script and server template.

## GeeTest v4 Captcha — Proxy Solution

SMS sending requires GeeTest v4 captcha. Server IPs always get `geeTest: true`.

**Working solution**: Build a Node.js proxy server (port 5701) that:
1. Pre-downloads GeeTest SDK files from `static.geetest.com` (serves without restrictions)
2. Proxies the `/load` and `/verify` JSONP APIs to `gcaptcha4.geetest.com`
3. Proxies captcha images from `/captcha_v4/` paths
4. User opens page on phone, completes slide captcha, gets SMS, logs in
5. Token auto-saved to QingLong env var `KURO_TOKEN`

**Critical pitfall**: GeeTest JSONP callback must be `geetest_` + 13-digit timestamp (e.g., `geetest_1718000000000`). Generic callbacks like `test_cb` return `-50004 jsonp xss`.

**SDK config for proxy**:
```javascript
initGeetest4({
    captchaId: '3f7e2d848ce0cb7e7d019d621e556ce2',
    product: 'bind',
    protocol: location.protocol + '//',
    apiServers: [location.host],
    staticServers: [location.host]
}, callback);
```

See `references/geetest-v4-proxy.md` for complete implementation details.

## Token Lifecycle

- APP login invalidates previous APP token (only one active at a time)
- Token appears to be long-lived (JWT, not short-expiry)
- Store in QingLong env var `KURO_TOKEN`

**CRITICAL:** Web token (from `user_token` cookie on kurobbs.com) is NOT the same as APP token. Web tokens return `code=220` ("登录已过期") on all APP API endpoints. Must obtain token through `sdkLogin` endpoint (APP login flow) or the reverse proxy page.

## Reverse Proxy Token Server (port 5701)

**Script:** `/tmp/kuro_token_server.js` — Node.js reverse proxy of kurobbs.com with JS injection and CDN proxying (4 domains).

**Key pitfalls:**
- CDN (ByteDance Byte-nginx) may send gzip-compressed responses even with `Accept-Encoding: identity`. Must decompress with `zlib.gunzipSync()` before processing, otherwise browser shows garbled text (乱码/锟斤拷).
- Always set `Accept-Encoding: identity` in proxy request headers AND decompress response based on `content-encoding` header.
- Strip `content-length`, `content-encoding`, `content-md5` from upstream headers; set `content-type: text/html; charset=utf-8` explicitly.
- Inject intercept script at START of `<head>` before SPA's JS loads.
- Override BOTH `fetch()` and `XMLHttpRequest` to catch all login API calls.
- Poll `user_token` from cookies/localStorage every 1s as fallback.
- Port 5701 is open in firewalld already.

## QingLong Env API Pitfall

- `POST /api/envs` needs array body: `[{name, value}]`
- `PUT /api/envs` needs single object body: `{id, name, value}` — NOT array! Array returns 400.
