---
name: userscript-saas
description: "Build and deploy Tampermonkey userscripts with backend API for paid SaaS services (key systems, user accounts, recharge codes). Covers the full stack: FastAPI backend, SQLite database, userscript frontend, multi-server deployment."
version: 1.0.0
author: aivos
platforms: [linux]
metadata:
  hermes:
    tags: [tampermonkey, userscript, saas, fastapi, sqlite, deployment]
---

# Userscript SaaS Builder

Build paid userscript services with backend API support. Used for browser automation tools (like 超星学习通) that need user authentication, usage tracking, and monetization.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐
│  Tampermonkey   │────▶│  FastAPI Backend  │
│  Userscript     │     │  (Python/SQLite)  │
│  (JS/GM_xml)    │     │                   │
└─────────────────┘     └──────────────────┘
        │                        │
        ▼                        ▼
   Browser DOM              SQLite DB
   (video/DOM)          (users/keys/codes)
```

## Backend Stack

- **Framework**: Flask or FastAPI + uvicorn
- **Database**: SQLite (no external deps)
- **Auth**: Account username/password + recharge codes (v3 pattern, keys removed)
- **API**: RESTful JSON, CORS enabled

## Key Patterns

### 1a. User Account System — Email-Only (v4 pattern, preferred)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,   -- auto-generated from email prefix
    password TEXT NOT NULL,
    email TEXT UNIQUE,               -- primary identifier
    balance INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recharge_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    times INTEGER DEFAULT 100,
    used_by TEXT,                    -- stores email, not username
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE password_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    code TEXT NOT NULL,              -- 6-digit verification code
    expires_at TIMESTAMP NOT NULL,
    used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 1b. User Account System — Username-Based (v3 pattern, legacy)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    nickname TEXT DEFAULT '',
    credits INTEGER DEFAULT 0,
    total_used INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### 2a. API Endpoints — Email-Only (v4 pattern, preferred)
```
POST /api/register         - {email, password}          → auto_login, auto username from prefix
POST /api/login            - {email, password}          → username, balance
POST /api/forgot-password  - {email}                    → sends verification code via SMTP
POST /api/reset-password   - {email, code, new_password}→ reset + login
POST /api/recharge         - {email, code}              → balance update
POST /api/query            - {email, question}          → deducts 1 from balance
```

### 2b. API Endpoints — Username-Based (v3 pattern, legacy)
```
POST /api/register    - {username, password, nickname}
POST /api/login       - {username, password}
POST /api/user-info   - {user_id}
POST /api/recharge    - {user_id, code}
POST /search          - {title, options, type, user_id|key}
POST /admin/generate-recharge - {token, count, credits}
GET  /admin/users     - ?token=xxx
GET  /admin/recharge-codes - ?token=xxx
```

### 3. Userscript Auth Flow
```javascript
// Store in GM_setValue
let currentUser = GM_getValue('current_user', null);
// Login → save user_id + credits
// Search → send user_id (not password)
// Recharge → update credits in stored user
```

### 4. Tampermonkey API Calls
```javascript
GM_xmlhttpRequest({
    method: 'POST',
    url: API_URL + '/search',
    headers: {'Content-Type': 'application/json'},
    data: JSON.stringify({title, options, type, user_id: currentUser.id}),
    onload: (res) => { /* handle response */ }
});
```

### 5. Video Automation (chaoxing-specific)
- **iframe穿透**: `iframe.contentDocument.querySelector('video')`
- **倍速保持**: setInterval 1s 检查 playbackRate
- **防暂停**: setInterval 1s 检查 paused 状态
- **弹窗关闭**: MutationObserver + setInterval 检查弹窗DOM
- **自动下一集**: video.addEventListener('ended', ...)
- **视频免费**: 不经过 /search 接口，纯前端操作

### 6. Database Migration Pattern
When adding columns to existing SQLite:
```python
try:
    conn.execute('ALTER TABLE xxx ADD COLUMN new_col TYPE')
except:
    pass  # Column already exists
```
Always add `try/except` - SQLite doesn't support IF NOT EXISTS for ALTER TABLE.

## Deployment Checklist

1. Upload app.py to server via sshpass/scp
2. Create systemd service (use correct Python venv path)
3. Open firewall port (`firewall-cmd --add-port=XXX/tcp --permanent`)
4. Test all endpoints with curl
5. Upload userscript to server
6. Add static file routes in FastAPI
7. Verify script download works

## Pitfalls

- **SQLite schema mismatch**: Old DB won't have new columns. Always check and migrate.
- **SSH key auth**: Use sshpass with password, not key-based auth (user's setup)
- **systemd Python path**: Must use venv Python (`/path/to/venv/bin/python3`), not system python
- **CORS**: Always add CORSMiddleware with `allow_origins=["*"]`
- **GM_xmlhttpRequest**: Must use this, not fetch(), for cross-origin requests in userscripts
- **Key format**: `CX-XXXX--XXXX` (note double dash) for compatibility
- **Key vs Account**: v3 removed standalone key system entirely. Use account+recharge codes only. Keys cause problems: users lose access when switching browsers, can't share across devices. Account system is superior.
- **Email-only auth (v4)**: v4 removed username registration entirely. Users register with email+password only. Username is auto-generated from email prefix (e.g. `user@example.com` → `user`). If prefix exists, appends counter (`user1`, `user2`). All API params use `email` not `username`. This is the preferred pattern for new deployments.
- **QQ邮箱 SMTP**: For sending verification codes in China. SMTP server: `smtp.qq.com`, port 465 (SSL). Auth uses QQ邮箱授权码 (not QQ password). Get authorization code: QQ邮箱设置 → 账户 → POP3/SMTP服务 → 开启 → 生成授权码. Code pattern:
  ```python
  import smtplib
  from email.mime.text import MIMEText

  def send_email(to_addr, subject, body):
      try:
          smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)
          smtp.login('QQ号@qq.com', '授权码')  # NOT QQ password
          msg = MIMEText(body, 'plain', 'utf-8')
          msg['Subject'] = subject
          msg['From'] = 'QQ号@qq.com'
          msg['To'] = to_addr
          smtp.sendmail('QQ号@qq.com', [to_addr], msg.as_string())
          smtp.quit()
          return True
      except Exception as e:
          print(f'发送邮件失败: {e}')
          return False
  ```
  Other SMTP servers: 163邮箱 (`smtp.163.com:465`), Gmail (`smtp.gmail.com:587` TLS).
- **Verification code flow**: Generate 6-digit code → store in `password_resets` table with expiry (10min) → send via SMTP → user enters code → verify against DB → reset password → mark code as used. NEVER return code in API response (was for testing only).
- **File corruption when patching Python**: When using find-and-replace on Python files, if the replacement spans across function boundaries (e.g. replacing a function CALL that's adjacent to a function DEFINITION), the patch can corrupt the file by destroying function signatures or body indentation. SAFER approach: for complex patches, rewrite the entire file rather than doing surgical replacements. Always verify with `python3 -c "import py_compile; py_compile.compile('app.py', doraise=True)"` after patching.
- **Recharge code features**: v3.2 added self-defined codes (user picks their own code string) and copyable codes (click-to-copy in admin panel). Custom codes are useful for branded codes like "VIP2024". Batch-generated codes use `RC-XXXXXXXX` format.
- **Flask vs FastAPI**: Both work. Flask is simpler for small projects (no uvicorn needed). FastAPI is better for async, docs, and type validation. For simple SaaS backends, Flask is sufficient.
- **subprocess.run pitfall**: On older Python (<3.7), `capture_output=True` and `text=True` kwargs don't exist. Use `subprocess.Popen` with `communicate()` instead:
  ```python
  proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = proc.communicate(timeout=120)
  return jsonify({'stdout': stdout.decode('utf-8', errors='replace'), ...})
  ```
- **Flask route after if __name__**: Routes defined AFTER `if __name__ == '__main__':` are SILENTLY IGNORED. This causes 404s with no error in logs. Always put routes BEFORE the if block. When appending to existing files, insert before `if __name__`, not after.
- **Multi-server deployment**: Use SSH key forwarding to control multiple servers from one API. Generate key on controller, add public key to targets, configure SSH aliases in ~/.ssh/config. Then `ssh hz-server "command"` works through the API.

## Admin Panel Best Practices

- **Mobile-first**: Users often manage from phones. Use responsive CSS, large touch targets, horizontal scrolling tabs.
- **Chinese UI**: For Chinese user base, all labels/messages in Chinese.
- **Click-to-copy**: Add `navigator.clipboard.writeText()` for codes/keys. Show toast notification on copy.
- **Custom codes**: Let admin input their own code string (e.g. "VIP2024") in addition to batch generation.
- **Tab navigation**: Use `display:none/block` toggling for tabs. Keep it simple, no frameworks needed.

## Announcement & Price Management

For SaaS apps that need admin-controlled announcements and pricing displayed on user-facing pages:

### Database Tables
```sql
CREATE TABLE IF NOT EXISTS announcements (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT
);
CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY,
    times INTEGER,  -- e.g. 100, 500, 1000
    price REAL      -- e.g. 10.0, 40.0, 70.0
);
```

### API Pattern
```python
# Public API (user-facing page reads these)
@app.route('/api/announcement')
def get_announcement():
    row = conn.execute("SELECT title, content FROM announcements ORDER BY id DESC LIMIT 1").fetchone()
    return jsonify({"title": row["title"], "content": row["content"]} if row else {"title": "", "content": ""})

@app.route('/api/prices')
def get_prices():
    rows = conn.execute("SELECT times, price FROM prices ORDER BY times").fetchall()
    return jsonify({"prices": [{"times": r["times"], "price": r["price"]} for r in rows]})

# Admin API (management panel writes these)
@app.route('/admin/api/announcement', methods=['GET', 'POST'])
def admin_announcement():
    if request.method == "POST":
        d = request.json
        conn.execute("DELETE FROM announcements")
        conn.execute("INSERT INTO announcements(title, content) VALUES(?, ?)", (d["title"], d["content"]))
        conn.commit()
        return jsonify({"message": "公告已更新"})
```

### User-Facing Page Pattern
The user page should show:
1. Login/register forms
2. Dashboard with balance display
3. Announcement banner (fetched from /api/announcement)
4. Price list (fetched from /api/prices)
5. Recharge code input

Keep user page in `/user/` directory, separate from admin page in `/admin/`.
