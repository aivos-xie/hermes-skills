---
name: flask-webapp-deployment
description: Deploy Flask web applications with nginx reverse proxy, systemd services, SQLite, and remote management APIs. Use when deploying Python web apps, creating admin panels, setting up reverse proxies, or building management APIs.
triggers:
  - deploy flask app
  - nginx reverse proxy
  - create admin panel
  - web application deployment
  - systemd service
  - remote command api
  - sqlite database
---

# Flask Web Application Deployment

Complete guide for deploying Flask applications with production-ready configuration.

## Architecture Overview

```
Client → Nginx (port 80/443) → Flask (port 8080) → SQLite
```

## Step 1: Flask Application Structure

### Basic App Template

```python
from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__, static_folder='static')
DB = '/opt/myapp/data.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/data', methods=['GET', 'POST'])
def api_data():
    if request.method == 'GET':
        conn = get_db()
        items = [dict(r) for r in conn.execute("SELECT * FROM users").fetchall()]
        conn.close()
        return jsonify({'items': items})
    else:
        data = request.json
        conn = get_db()
        conn.execute("INSERT INTO users(username) VALUES(?)", (data['username'],))
        conn.commit()
        conn.close()
        return jsonify({'message': 'created'})

# Admin panel
@app.route('/admin')
def admin_page():
    return send_from_directory('admin', 'index.html')

@app.route('/admin/<path:filename>')
def admin_static(filename):
    return send_from_directory('admin', filename)

# Static files
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory('/opt/myapp/files', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Admin Panel HTML Template

```html
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin Panel</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#f0f2f5;min-height:100vh}
.login{max-width:360px;margin:100px auto;padding:30px;background:#fff;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,.08)}
.header{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:16px 20px;display:flex;justify-content:space-between;align-items:center}
.tabs{display:flex;background:#fff;border-bottom:1px solid #eee;overflow-x:auto}
.tab{padding:14px 18px;cursor:pointer;white-space:nowrap;font-size:14px;color:#666;border-bottom:2px solid transparent}
.tab.active{color:#667eea;border-bottom-color:#667eea;font-weight:600}
.content{padding:16px;max-width:800px;margin:0 auto}
.card{background:#fff;border-radius:16px;padding:20px;margin-bottom:16px;box-shadow:0 2px 12px rgba(0,0,0,.04)}
input,button{padding:10px 14px;border:1px solid #ddd;border-radius:8px;font-size:14px}
button{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;cursor:pointer}
</style>
</head>
<body>
<div class="login" id="loginBox">
<h2>🔐 Admin</h2>
<input type="password" id="pwd" placeholder="Password" onkeypress="if(event.key==='Enter')login()">
<button onclick="login()">Login</button>
</div>
<div id="dash" style="display:none">
<div class="header">
<h2>⚡ Dashboard</h2>
<button onclick="localStorage.removeItem('token');location.reload()">Logout</button>
</div>
<div class="tabs">
<div class="tab active" onclick="tab('stats',this)">📊 Stats</div>
<div class="tab" onclick="tab('data',this)">📋 Data</div>
</div>
<div class="content">
<div id="p-stats"><div id="sg"></div></div>
<div id="p-data" style="display:none"><div class="card"><div id="dl"></div></div></div>
</div>
</div>
<script>
const B='/admin/api';
if(localStorage.getItem('token')==='admin')show();
function login(){if(document.getElementById('pwd').value==='admin'){localStorage.setItem('token','admin');show()}else alert('Wrong password')}
function show(){document.getElementById('loginBox').style.display='none';document.getElementById('dash').style.display='block';loadStats()}
function tab(n,el){document.querySelectorAll('[id^="p-"]').forEach(e=>e.style.display='none');document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));document.getElementById('p-'+n).style.display='block';el.classList.add('active')}
function api(p,m='GET',b=null){const o={method:m,headers:{'Content-Type':'application/json'}};if(b)o.body=JSON.stringify(b);return fetch(B+p,o).then(r=>r.json())}
function loadStats(){api('/stats').then(d=>{document.getElementById('sg').innerHTML=JSON.stringify(d)})}
</script>
</body>
</html>
```

## Step 2: Nginx Reverse Proxy

### Configuration File

```nginx
# /etc/nginx/conf.d/myapp.conf
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }
}
```

### Apply Configuration

```bash
# Test configuration
sudo nginx -t

# Reload nginx
sudo nginx -s reload
```

## Step 3: Systemd Service

### Service File

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Flask Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/python3 /opt/myapp/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Commands

```bash
# Create service file
sudo tee /etc/systemd/system/myapp.service > /dev/null << 'EOF'
[Unit]
Description=My Flask Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/python3 /opt/myapp/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload and start
sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl start myapp

# Check status
sudo systemctl status myapp
```

## Step 4: Remote Command Execution API

### Implementation

```python
import subprocess

@app.route('/api/exec', methods=['POST'])
def api_exec():
    data = request.json
    token = data.get('token', '')
    if token != 'your-secret-token':
        return jsonify({'error': 'unauthorized'}), 401
    cmd = data.get('cmd', '')
    try:
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(timeout=120)
        return jsonify({
            'stdout': stdout.decode('utf-8', errors='replace'),
            'stderr': stderr.decode('utf-8', errors='replace'),
            'code': proc.returncode
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Usage

```bash
curl -X POST http://server/api/exec \
  -H "Content-Type: application/json" \
  -d '{"token":"your-secret-token","cmd":"ls -la"}'
```

## Step 5: User Authentication System

### Database Schema

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    balance INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recharge_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    times INTEGER DEFAULT 100,
    used_by TEXT,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API Endpoints

```python
@app.route('/api/register', methods=['POST'])
def register():
    d = request.json
    u, p = d.get('username','').strip(), d.get('password','').strip()
    if not u or not p:
        return jsonify({'error':'Username and password required'}), 400
    conn = get_db()
    if conn.execute("SELECT 1 FROM users WHERE username=?",(u,)).fetchone():
        conn.close()
        return jsonify({'error':'Username exists'}), 400
    conn.execute("INSERT INTO users(username,password) VALUES(?,?)",(u,p))
    conn.commit()
    conn.close()
    return jsonify({'message':'Registered','username':u})

@app.route('/api/login', methods=['POST'])
def login():
    d = request.json
    u, p = d.get('username','').strip(), d.get('password','').strip()
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p)).fetchone()
    conn.close()
    if not row:
        return jsonify({'error':'Invalid credentials'}), 401
    return jsonify({'message':'Logged in','username':u,'balance':row['balance']})

@app.route('/api/recharge', methods=['POST'])
def recharge():
    d = request.json
    u = d.get('username','').strip()
    code = d.get('code','').strip().upper()
    conn = get_db()
    rc = conn.execute("SELECT * FROM recharge_codes WHERE code=? AND used_by IS NULL",(code,)).fetchone()
    if not rc:
        conn.close()
        return jsonify({'error':'Invalid code'}), 400
    conn.execute("UPDATE users SET balance=balance+? WHERE username=?",(rc['times'],u))
    conn.execute("UPDATE recharge_codes SET used_by=?,used_at=datetime('now') WHERE code=?",(u,code))
    conn.commit()
    bal = conn.execute("SELECT balance FROM users WHERE username=?",(u,)).fetchone()['balance']
    conn.close()
    return jsonify({'message':'Recharged','added':rc['times'],'balance':bal})
```

## Step 6: Email Verification (SMTP)

When you need to send verification codes or notification emails:

```python
import smtplib
from email.mime.text import MIMEText
import random, string
from datetime import datetime, timedelta

# SMTP配置（QQ邮箱示例）
SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 465
SMTP_USER = 'QQ号@qq.com'
SMTP_PASS = '授权码'  # NOT QQ password! Get from mail.qq.com → 设置 → POP3/SMTP

def send_email(to_addr, subject, body):
    try:
        smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        smtp.login(SMTP_USER, SMTP_PASS)
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = to_addr
        smtp.sendmail(SMTP_USER, [to_addr], msg.as_string())
        smtp.quit()
        return True
    except Exception as e:
        print(f'发送邮件失败: {e}')
        return False

# Verification code endpoint
@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json.get('email', '').strip()
    code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.now() + timedelta(minutes=10)
    
    conn.execute("INSERT INTO password_resets(email, code, expires_at) VALUES(?, ?, ?)",
                 (email, code, expires_at.isoformat()))
    conn.commit()
    
    email_body = f'【应用名】验证码：{code}，10分钟有效。'
    if send_email(email, '验证码', email_body):
        return jsonify({'message': '验证码已发送到您的邮箱'})
    else:
        return jsonify({'error': '邮件发送失败'}), 500
```

**Important**: Never return the verification code in the API response (was common in testing, breaks security in production).

**Other SMTP servers**: 163邮箱 (`smtp.163.com:465`), Gmail (`smtp.gmail.com:587` TLS).

## Step 7: Tampermonkey Userscript

### Basic Template

```javascript
// ==UserScript==
// @name         My App Helper
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Auto-fill and helper for my app
// @match        *://example.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_setValue
// @grant        GM_getValue
// @connect      your-server.com
// ==/UserScript==

(function() {
    'use strict';

    const API_BASE = 'http://your-server.com';
    let username = GM_getValue('username', '');

    // Create UI
    function createUI() {
        const panel = document.createElement('div');
        panel.style.cssText = `
            position: fixed; top: 10px; right: 10px; z-index: 99999;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 16px; border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3); font-size: 14px;
            min-width: 280px; font-family: -apple-system, sans-serif;
        `;
        
        if (username) {
            panel.innerHTML = `
                <div style="font-weight:bold;font-size:16px;margin-bottom:12px">⚡ My App</div>
                <div>👤 ${username}</div>
                <button onclick="myapp.logout()" style="margin-top:8px;padding:8px 12px;background:rgba(255,255,255,0.2);border:none;color:white;border-radius:6px;cursor:pointer">Logout</button>
            `;
        } else {
            panel.innerHTML = `
                <div style="font-weight:bold;font-size:16px;margin-bottom:12px">⚡ My App</div>
                <input id="loginUser" placeholder="Username" style="width:100%;padding:8px;margin-bottom:8px;border:1px solid rgba(255,255,255,0.3);border-radius:6px;background:rgba(255,255,255,0.1);color:white">
                <input id="loginPass" type="password" placeholder="Password" style="width:100%;padding:8px;margin-bottom:8px;border:1px solid rgba(255,255,255,0.3);border-radius:6px;background:rgba(255,255,255,0.1);color:white">
                <button onclick="myapp.login()" style="width:100%;padding:8px;background:white;color:#667eea;border:none;border-radius:6px;cursor:pointer;font-weight:bold">Login</button>
            `;
        }
        
        document.body.appendChild(panel);
    }

    // API request
    function api(path, data, callback) {
        GM_xmlhttpRequest({
            method: 'POST',
            url: API_BASE + path,
            headers: { 'Content-Type': 'application/json' },
            data: JSON.stringify(data),
            onload: function(res) {
                callback(null, JSON.parse(res.responseText));
            },
            onerror: function(err) {
                callback(err, null);
            }
        });
    }

    window.myapp = {
        login: function() {
            const u = document.getElementById('loginUser').value.trim();
            const p = document.getElementById('loginPass').value.trim();
            api('/api/login', { username: u, password: p }, function(err, data) {
                if (data && data.message) {
                    username = u;
                    GM_setValue('username', u);
                    location.reload();
                } else {
                    alert(data ? data.error : 'Login failed');
                }
            });
        },
        logout: function() {
            GM_setValue('username', '');
            location.reload();
        }
    };

    createUI();
})();
```

## Step 8: Multi-Server Control via SSH Key Forwarding

When you need to control multiple servers from one API endpoint:

### Setup SSH Keys
```bash
# On the controller server
ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519 -N "" -q

# Add public key to target server
echo "$(cat /root/.ssh/id_ed25519.pub)" >> /root/.ssh/authorized_keys

# Configure SSH aliases
cat >> /root/.ssh/config << 'EOF'
Host hz-server
    HostName TARGET_IP
    User root
    IdentityFile /root/.ssh/id_ed25519
    StrictHostKeyChecking no
EOF
chmod 600 /root/.ssh/config
```

### Execute Remote Commands via API
```bash
# Control local server
curl -X POST http://server/api/exec \
  -H "Content-Type: application/json" \
  -d '{"token":"your-token","cmd":"hostname"}'

# Control remote server via SSH
curl -X POST http://server/api/exec \
  -H "Content-Type: application/json" \
  -d '{"token":"your-token","cmd":"ssh hz-server \"hostname && uptime\""}'
```

### Security: Restrict API Port to Specific IPs
In Alibaba Cloud security group, create rule:
- Protocol: Custom TCP
- Port: 9090/9090 (or your API port)
- Authorization object: YOUR_IP/32
- This ensures only your IP can access the management API

## Step 9: User-Facing Frontend (Separate from Admin)

When you need both an admin panel AND a user-facing site:

```python
# Admin panel (management)
@app.route('/admin')
def admin_page():
    return send_from_directory('admin', 'index.html')

# User-facing page (registration, purchase, etc.)
@app.route('/user')  # or '/' for the main page
def user_page():
    return send_from_directory('user', 'index.html')
```

Keep them in separate directories (`admin/` and `user/`) with separate HTML files.

## Step 9: Announcement & Price Management

For SaaS-style apps with announcements and pricing:

```python
# Database tables
conn.execute('''CREATE TABLE IF NOT EXISTS announcements (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT
)''')
conn.execute('''CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY,
    times INTEGER,
    price REAL
)''')

# Public API (for user-facing page)
@app.route('/api/announcement')
def get_announcement():
    conn = get_db()
    row = conn.execute("SELECT title, content FROM announcements ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    if row:
        return jsonify({"title": row["title"], "content": row["content"]})
    return jsonify({"title": "", "content": ""})

# Admin API (for management)
@app.route('/admin/api/announcement', methods=['GET', 'POST'])
def admin_announcement():
    conn = get_db()
    if request.method == "POST":
        d = request.json
        conn.execute("DELETE FROM announcements")
        conn.execute("INSERT INTO announcements(title, content) VALUES(?, ?)", (d["title"], d["content"]))
        conn.commit(); conn.close()
        return jsonify({"message": "公告已更新"})
    else:
        row = conn.execute("SELECT title, content FROM announcements ORDER BY id DESC LIMIT 1").fetchone()
        conn.close()
        return jsonify({"title": row["title"], "content": row["content"]} if row else {"title": "", "content": ""})
```

## Common Pitfalls

### 1. Port Already in Use
```bash
# Check what's using the port
sudo ss -tlnp | grep :8080

# If process is owned by root and kill fails
sudo kill -9 $(fuser 8080/tcp 2>/dev/null)

# fuser may be unreliable on some systems — use ps + grep as fallback
ps aux | grep "python3 app.py" | grep -v grep
sudo kill -9 <PID>
```

### 2. Nginx Configuration Conflicts
```bash
# Check for conflicting server names
sudo nginx -t 2>&1 | grep conflicting

# Remove default configuration
sudo rm /etc/nginx/conf.d/default.conf
```

### 3. SQLite Database Locked
```bash
# Check for locks
fuser /opt/myapp/data.db

# Use WAL mode for better concurrency
PRAGMA journal_mode=WAL;
```

### ⚠️ Pitfall: Flask Route Ordering (CRITICAL)

Routes must be defined at module level, NOT inside `if __name__ == '__main__':`. The `if` block only runs when executed directly, not when imported by systemd/gunicorn. Always put all `@app.route` decorators before the `if` block.

**Symptoms**: Routes return 404 even though they exist in the file. No error in logs. Flask starts normally.

**Detection**: `grep -n "@app.route" app.py` — if any route appears AFTER `if __name__`, it's broken.

**Fix**: Move all routes before `if __name__`. When appending routes to an existing file, always insert BEFORE the `if __name__` block, not after.

**Common mistake**: Using `cat >> app.py << 'EOF'` to add new routes — this appends AFTER `if __name__`. Instead, use `sed -i '/if __name__/i \新路由代码' app.py` or rewrite the file.

### Pitfall: Duplicate Route Definitions

When patching app.py multiple times, duplicate `@app.route('/path')` definitions cause silent failures. Always check with:
```bash
grep -c "@app.route('/user')" app.py  # Should be 1
```

### 🔴 Pitfall: File Corruption When Patching Python

When using find-and-replace on Python files (patch tool, sed, etc.), replacements that span function boundaries can corrupt the file. Common scenario: replacing a function CALL that sits adjacent to a function DEFINITION destroys the colon, indentation, or body.

**Example of corruption**:
```python
# Original:
def init_db():
    conn = get_db()
    ...
    
init_db()  # ← replacing this line with SMTP config

# Corrupted result:
def init_db()    # ← lost the colon AND the body!
# SMTP config...
    conn = get_db()  # ← now indented inside send_email
```

**Prevention**: For complex multi-line changes, rewrite the entire file rather than surgical replacements. Always verify syntax after any patch:
```bash
python3 -c "import py_compile; py_compile.compile('app.py', doraise=True)"
```

**Recovery**: If corrupted, either restore from backup (`cp app.py.bak app.py`) or rewrite the file completely.

### Pitfall: File Download Route

When serving userscripts or static files through Flask, add explicit routes with correct MIME types:
```python
@app.route('/chaoxing.user.js')
def download_script():
    return send_from_directory('/opt/app', 'chaoxing.user.js', mimetype='application/javascript')
```
Do NOT rely on nginx to serve these — Flask's `send_from_directory` is more reliable when the file is in the app directory.

### 5. Systemd Service Won't Start
```bash
# Check logs
sudo journalctl -u myapp -f

# Check permissions
ls -la /opt/myapp/app.py
```

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Set strong API tokens
- [ ] Validate all user inputs
- [ ] Use parameterized queries (prevent SQL injection)
- [ ] Set appropriate CORS headers
- [ ] Rate limit API endpoints
- [ ] Use environment variables for secrets
- [ ] Regular backups of SQLite database

## Quick Deploy Script

```bash
#!/bin/bash
# Quick deploy script for Flask app

APP_DIR="/opt/myapp"
APP_NAME="myapp"

# Create directory
mkdir -p $APP_DIR

# Copy files
cp app.py $APP_DIR/
cp -r admin $APP_DIR/

# Create systemd service
sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null << EOF
[Unit]
Description=My Flask Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/python3 $APP_DIR/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Create nginx config
sudo tee /etc/nginx/conf.d/$APP_NAME.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Start services
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl start $APP_NAME
sudo nginx -t && sudo nginx -s reload

echo "✅ Deployed! Access at http://your-server/admin"
```
