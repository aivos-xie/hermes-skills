# GeeTest v4 SDK Proxy Pattern

> **⚠️ SUPERSEDED (2026-06-09)**: This reverse proxy approach no longer works because **kurobbs.com web version does not support login** — only the APP can log in. Use **mitmproxy MITM proxy** instead (see `kurobbs-signin` skill). The technical details below are kept for GeeTest reference only.

Building a web page that proxies the GeeTest v4 captcha SDK to bypass server-side IP restrictions.

## Problem

GeeTest v4 captcha blocks server-side requests with `geeTest: true` (SMS not sent). The SDK JS files on `gcaptcha4.geetest.com` return 403 from server IPs. Need to build a browser-based captcha flow proxied through own server.

## Key Findings

### JSONP Callback Format (CRITICAL)

GeeTest API validates the `callback` parameter. Only `geetest_` prefix followed by a 13-digit timestamp works:

```
# FAILS - generic callback
?callback=test_cb           → {"code":"-50004","msg":"jsonp xss"}
?callback=test123           → {"code":"-50004","msg":"jsonp xss"}
?callback=geetest_12345     → {"code":"-50004","msg":"jsonp xss"}  (too short)

# WORKS - timestamp-length number
?callback=geetest_1718000000000  → geetest_1718000000000({"status":"success",...})
```

The SDK generates: `geetest_` + `parseInt(Math.random() * 10000) + Date.now()` (13-digit timestamp).

### Static Resource CDN

`static.geetest.com` serves all resources without referer/origin checks:
- SDK loader: `https://static.geetest.com/v4/gt4.js` (15KB) - entry point with `initGeetest4()`
- Main captcha JS: `https://static.geetest.com/v4/static/v1.9.6-1adb4a/js/gcaptcha4.js` (1MB) - full captcha UI/logic
- GCT resource: `https://static.geetest.com/v4/gct/gct4.{hash}.js` (3KB) - fingerprint logic
- CSS: `https://static.geetest.com/v4/static/v1.9.6-1adb4a/css/gcaptcha4.css` (110KB)

`gcaptcha4.geetest.com` blocks all static resource downloads (403). Always use `static.geetest.com`.

### SDK Configuration Override

```javascript
initGeetest4({
    captchaId: 'YOUR_CAPTCHA_ID',
    product: 'bind',
    protocol: location.protocol + '//',
    apiServers: [location.host],      // redirect API calls to proxy
    staticServers: [location.host]    // redirect resource loads to proxy
}, function(captcha) { ... });
```

### Required Proxy Routes

| Route | Proxy to | Purpose |
|-------|----------|---------|
| `/load?...` | `gcaptcha4.geetest.com/load?...` | JSONP captcha config (passthrough) |
| `/verify?...` | `gcaptcha4.geetest.com/verify?...` | JSONP verification (passthrough) |
| `/v4/static/...` | `static.geetest.com/v4/static/...` | SDK JS/CSS |
| `/v4/gct/...` | `static.geetest.com/v4/gct/...` | GCT resource |
| `/captcha_v4/...` | `gcaptcha4.geetest.com/captcha_v4/...` | Captcha images |
| `/monitor/...` | Absorb (204) | SDK telemetry |

### Load API Response

```
GET /load?captcha_id=XXX returns (JSONP wrapped):
{
  "status": "success",
  "data": {
    "lot_number": "...",
    "captcha_type": "slide",
    "slice": "captcha_v4/.../slice/hash.png",
    "bg": "captcha_v4/.../bg/hash.png",
    "ypos": 41,
    "gct_path": "/v4/gct/gct4.hash.js",
    "static_path": "/v4/static/v1.9.6-1adb4a",
    "pow_detail": {"version":"1","bits":0,"datetime":"...","hashfunc":"md5"}
  }
}
```

No `staticServers` or `apiServers` in response — SDK uses config values.

### GeeTest v4 Verification Params

After user solves captcha, SDK calls `/verify` with:
- `lot_number` - from load response
- `captcha_output` - encrypted answer (computed by SDK/GCT)
- `pass_token` - hash token (computed by SDK/GCT)
- `gen_time` - unix timestamp of solution
- `captcha_id` - the captcha ID

The `captcha_output` and `pass_token` are computed by the obfuscated GCT JS, NOT simple MD5. Cannot be generated server-side without the SDK.

## Working Node.js Server Template

```javascript
const server = http.createServer(async (req, res) => {
    const path = url.parse(req.url).pathname;
    const qs = url.parse(req.url).query || '';

    if (path === '/') {
        // Serve HTML page
    } else if (path === '/load') {
        // JSONP passthrough - DO NOT modify callback
        const resp = await proxyGeetest('/load?' + qs);
        res.writeHead(200, {'Content-Type': 'application/javascript'});
        res.end(resp.body);
    } else if (path === '/verify') {
        const resp = await proxyGeetest('/verify?' + qs);
        res.writeHead(200, {'Content-Type': 'application/javascript'});
        res.end(resp.body);
    } else if (path.startsWith('/v4/')) {
        // Static resources from static.geetest.com
        const resp = await httpsGet('https://static.geetest.com' + path);
        res.writeHead(200, {'Content-Type': 'application/javascript'});
        res.end(resp.body);
    } else if (path.startsWith('/captcha_v4/')) {
        // Captcha images
        const resp = await httpsGet('https://gcaptcha4.geetest.com' + path);
        res.writeHead(200, {'Content-Type': 'image/png'});
        res.end(resp.body);
    } else if (path.startsWith('/monitor/')) {
        res.writeHead(204); res.end();
    }
});
```

## Status: WORKING VIA REVERSE PROXY (2026-06-08)

### What Didn't Work

Hosting GeeTest SDK locally (downloading all resources, serving from own server, redirecting `apiServers`/`staticServers`):
- SDK loader, main JS (1MB), GCT (3KB), CSS all served correctly
- Load API JSONP passthrough works
- **But the captcha UI never renders** — the 1MB obfuscated main JS has anti-proxy checks or requires specific DOM context

### What WORKS: Reverse Proxy + JS Interception

Proxy the **entire kurobbs.com website** and inject JS to intercept the login API response:

```javascript
// Node.js server on port 5701
const server = http.createServer(async (req, res) => {
    const path = url.parse(req.url).pathname;

    // 1. Token capture endpoint
    if (path === '/__capture' && req.method === 'POST') {
        // Save token to QingLong env var
        let body = ''; req.on('data', c => body += c);
        req.on('end', async () => {
            const { token } = JSON.parse(body);
            await saveToQingLong(qlToken, token);
            res.writeHead(200); res.end('{"ok":true}');
        });
        return;
    }

    // 2. Success page
    if (path === '/__success') {
        res.writeHead(200, {'Content-Type': 'text/html'});
        res.end('<h1>✅ Token 获取成功！</h1>');
        return;
    }

    // 3. API proxy: /__api/xxx -> api.kurobbs.com/xxx
    let targetHost, targetPath;
    if (path.startsWith('/__api/')) {
        targetHost = 'api.kurobbs.com';
        targetPath = path.replace('/__api', '') + (parsed.search || '');
    } else {
        targetHost = 'www.kurobbs.com';
        targetPath = path + (parsed.search || '');
    }

    const resp = await proxyHttps(targetHost, targetPath, req.method, req.headers, bodyBuf);

    // 4. For HTML responses: inject interception script
    if (ct.includes('text/html')) {
        let html = resp.body.toString('utf8');
        html = html.replace('<head>', '<head>' + INTERCEPT_SCRIPT);
        // ...
    }
});
```

The interception script (injected at start of `<head>`):

```javascript
(function(){
  var HOST = location.origin;

  // Override fetch — redirect api.kurobbs.com calls through proxy
  var _f = window.fetch;
  window.fetch = function(input, init) {
    var u = typeof input === 'string' ? input : (input?.url || '');
    if (u.indexOf('api.kurobbs.com') >= 0) {
      u = u.replace('https://api.kurobbs.com', HOST + '/__api');
      if (typeof input === 'string') input = u;
      else input = new Request(u, input);
    }
    return _f.call(this, input, init).then(function(resp) {
      // Check login response for token
      if (u.indexOf('sdkLogin') >= 0 || u.indexOf('sdkLoginForH5') >= 0) {
        resp.clone().json().then(function(d) {
          if (d.code === 200 && d.data && d.data.token) {
            _f(HOST + '/__capture', {
              method:'POST', headers:{'Content-Type':'application/json'},
              body: JSON.stringify({token: d.data.token})
            }).then(function(){ location.href = HOST + '/__success'; });
          }
        }).catch(function(){});
      }
      return resp;
    });
  };

  // Override XMLHttpRequest — same redirection
  var _o = XMLHttpRequest.prototype.open;
  var _s = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function(m, u) {
    if (u && u.indexOf('api.kurobbs.com') >= 0)
      u = u.replace('https://api.kurobbs.com', HOST + '/__api');
    this.__url = u;
    return _o.apply(this, arguments);
  };
  XMLHttpRequest.prototype.send = function(body) {
    var xhr = this;
    xhr.addEventListener('load', function() {
      try {
        if (xhr.__url && (xhr.__url.indexOf('sdkLogin') >= 0 || xhr.__url.indexOf('sdkLoginForH5') >= 0)) {
          var d = JSON.parse(xhr.responseText);
          if (d.code === 200 && d.data && d.data.token) {
            fetch(HOST + '/__capture', {method:'POST', headers:{'Content-Type':'application/json'},
              body: JSON.stringify({token: d.data.token})
            }).then(function(){ location.href = HOST + '/__success'; });
          }
        }
      } catch(e){}
    });
    return _s.apply(this, arguments);
  };
})();
```

### Why This Works

1. The SPA loads normally from kurobbs.com (CSS, JS, images from CDN)
2. Our intercept script runs FIRST (injected at start of `<head>`)
3. When user logs in, SPA calls `api.kurobbs.com/user/sdkLogin` → our fetch/XHR override redirects to `/__api/user/sdkLogin` → our proxy forwards to real API
4. Login response contains `token` → intercept script POSTs to `/__capture` → saved to QingLong
5. User redirected to success page

### Response Header Handling

Strip security headers that block proxying:
- `content-security-policy` — blocks inline scripts
- `x-frame-options` — blocks iframe embedding
- `strict-transport-security` — forces HTTPS
- `content-encoding` / `transfer-encoding` — conflicts with content-length rewrite

Rewrite cookies:
```javascript
c.replace(/domain=[^;]*/gi, '')
 .replace(/secure;?/gi, '')
 .replace(/samesite=\w+/gi, 'samesite=lax')
```

### Pitfalls for Reverse Proxy Approach

- **Inject script at START of `<head>`** — must run before SPA's JS loads, otherwise fetch/XHR already bound
- **Intercept BOTH fetch and XMLHttpRequest** — SPA may use either
- **Clone response before reading** — `resp.clone().json()` because response body can only be read once
- **Rewrite cookie domain/security** — otherwise browser rejects cookies from different origin
- **API path rewrite**: `/__api/xxx` → `api.kurobbs.com/xxx` (strip prefix)
- **Monitor both `sdkLogin` and `sdkLoginForH5`** — web version may use either endpoint
- **CDN `content-length: 0`**: ByteDance CDN returns `content-length: 0` even with actual body. MUST delete and recalculate in proxy, or browser shows blank/garbled page.
- **Missing charset**: Upstream `text/html` lacks `charset=utf-8`. Mobile browsers pick wrong encoding → 乱码. Always append `; charset=utf-8` to proxied HTML responses.

## Dual Capture Strategy (Most Reliable)

The API interception approach (overriding fetch/XHR to detect `sdkLogin` response) is **not always reliable** — the SPA may use a different request method, or the intercept script may not run before the SPA binds its own handlers.

**Most reliable approach: combine API interception WITH cookie/localStorage polling:**

```javascript
// Polling script — runs every 1 second, checks for token in storage
var sent = false;
function checkAndSend() {
    if (sent) return;
    var token = null;
    // Check cookies
    document.cookie.split(';').forEach(function(c) {
        c = c.trim();
        if (c.indexOf('token=') === 0) token = c.substring(6);
        if (c.indexOf('user_token=') === 0) token = c.substring(11);
    });
    // Check localStorage/sessionStorage
    if (!token) try { token = localStorage.getItem('token'); } catch(e){}
    if (!token) try { token = localStorage.getItem('user_token'); } catch(e){}
    if (!token) try { token = sessionStorage.getItem('token'); } catch(e){}
    // Must be a JWT
    if (token && token.length > 20 && token.indexOf('eyJ') === 0) {
        sent = true;
        fetch(HOST + '/__capture', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({token: token})
        }).then(function(){ location.href = HOST + '/__success'; });
    }
}
setInterval(checkAndSend, 1000);
```

**Inject BOTH scripts** — the API intercept (for immediate capture) AND the polling script (as fallback). The polling catches tokens stored in cookies/localStorage regardless of how the login API was called.

## CDN Domains for kurobbs.com Reverse Proxy

kurobbs.com is a Vue SPA. The HTML loads from `www.kurobbs.com`, but ALL CSS/JS/images come from separate CDN domains. **If you only proxy `www.kurobbs.com` and `api.kurobbs.com`, the page loads but appears broken — no styles, no JavaScript, just empty shell.**

Complete list of domains to proxy:

| Route prefix | Target host | Content |
|---|---|---|
| `/` (default) | `www.kurobbs.com` | HTML pages |
| `/_api/*` | `api.kurobbs.com` | REST API calls |
| `/_static/*` | `web-static.kurobbs.com` | CSS, JS bundles, icons |
| `/_cdn/*` | `prod-alicdn-community.kurobbs.com` | Images, fonts, misc assets |

**URL rewriting in HTML/JS/CSS** — Replace ALL occurrences of these domains in proxied responses:
```
https://api.kurobbs.com          → /_api
https://web-static.kurobbs.com   → /_static
https://prod-alicdn-community.kurobbs.com → /_cdn
```

This applies to HTML, JavaScript, and CSS files — the SPA may reference these domains in any of them.

**Route config pattern (Node.js):**
```javascript
const ROUTES = [
    { prefix: '/_api/',    target: 'api.kurobbs.com',                    strip: '/_api' },
    { prefix: '/_static/', target: 'web-static.kurobbs.com',             strip: '/_static' },
    { prefix: '/_cdn/',    target: 'prod-alicdn-community.kurobbs.com',  strip: '/_cdn' },
];
// Default fallback: www.kurobbs.com
```

**Verified working (2026-06-09):** All CDN routes return 200 and the full SPA loads correctly on mobile.

## Pitfalls

- **Do NOT add callback parameter manually** — SDK generates correct `geetest_xxx` callback. Proxy must passthrough query string as-is.
- **Do NOT use `gcaptcha4.geetest.com` for static resources** — returns 403. Use `static.geetest.com`.
- **Do NOT try to compute `captcha_output`/`pass_token` server-side** — they're generated by obfuscated GCT JS.
- **Load API returns JSONP by default** — `({...})` wrapper. With callback param: `geetest_xxx({...})`. Both are JavaScript, not JSON.
- **GCT hash changes** — the `gct_path` in load response contains a hash that may change. Always use the path from the load response, don't hardcode.
- **Captcha UI may not render** — even with all resources proxied, the 1MB obfuscated main JS may have additional checks. Don't spend too long debugging; use the reverse proxy approach instead.
- **API interception alone is unreliable** — the SPA may bind fetch/XHR before your inject runs, or use a different method. Always add cookie/localStorage polling as backup.
- **QingLong envs API requires array body** — `POST /api/envs` and `PUT /api/envs` need `[{...}]` not `{...}`. Sending single object returns 400 "value must be an array". This fails silently in try/catch — always verify the env was actually created.
