# QingLong Setup

- **URL**: http://localhost:5700 (also http://8.162.25.142:5700)
- **User**: aivos
- **Password**: xyh14717461758@ (recovered from SQLite DB on 2026-06-08)
- **Version**: 2.20.2
- **Docker container**: name=qinglong, ID=f0ded63d1505
- **OS**: Alibaba Cloud Linux 3 (2-core 1.8G)
- **Existing tasks**: 
  - [ID=1] QQ每日打卡 — **BROKEN**, daily 08:30, script `qqSign.js`. Should be deleted.
  - [ID=2] 鸣潮签到 — created, daily 08:30, script `mc_sign.js`. Missing `KURO_TOKEN` env var. Task disabled until user provides token.

## GeeTest Captcha Blocks Token Acquisition

Attempted to build a local web page (port 5701) to help user get Kuro BBS token via SMS login.
**Failed:** GeeTest v4 captcha is required for SMS sending from server IPs. The captcha requires user interaction (slide puzzle) that can't be automated server-side.

Port 5701 was opened in firewalld (`firewall-cmd --add-port=5701/tcp --permanent`) but the approach didn't work due to captcha.

**Viable token acquisition methods:**
1. User installs packet capture app (HttpCanary/Reqable) on Android → captures token from 库街区 app
2. User logs in on kurobbs.com mobile browser → extracts token from cookies/localStorage
3. User finds token in 库街区 app settings (if available)

## Firewalld Port Management

This server runs `firewalld` (not raw iptables). To open ports:
```bash
sudo firewall-cmd --add-port=PORT/tcp --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```
Also need to open port in Alibaba Cloud security group via web console.

## QQ每日打卡 — PERMANENTLY BROKEN

The QQ空间 web APIs are fully deprecated as of 2026-06. No workaround exists.

- `user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_publish` → 500
- `h5.qzone.qq.com/webapp/feed/signIn` → 404
- `mobile.qzone.qq.com/signIn` → 403
- Source repo `qqdxm/ql` on GitHub → 404 (deleted)

User should disable or delete task ID=1. Script at `/ql/data/scripts/qqSign.js` is dead code.
