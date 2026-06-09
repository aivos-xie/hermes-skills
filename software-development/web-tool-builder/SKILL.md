---
name: web-tool-builder
description: Build and deploy self-contained web applications on Linux servers — Flask/Node tools with auth, file management, dashboards. Includes templates, deployment patterns, and Python environment pitfalls.
triggers:
  - user asks to build a web tool dashboard or file manager
  - user wants to replace an existing heavy service with a custom lightweight one
  - deploying Flask or Python web apps on Linux servers
---

# Web Tool Builder

Build self-contained web applications from scratch, typically replacing heavier services (AList, Nextcloud, etc.) with purpose-built tools.

## Architecture Pattern

```
/opt/<tool-name>/
├── app.py              # Main application (Flask/Express)
├── requirements.txt    # Python deps (pin compatible versions)
├── Dockerfile          # Optional containerization
├── docker-compose.yml  # Optional compose config
├── storage/            # Data directory (bind-mounted if Docker)
└── templates/          # HTML templates (Jinja2/Handlebars)
    ├── base.html       # Shared layout (optional)
    ├── index.html       # Main page
    ├── login.html       # Auth page
    └── 404.html         # Error page
```

## Step-by-Step Build Flow

### 1. Create project structure
```bash
sudo mkdir -p /opt/<tool-name>/{templates,static/{css,js},storage}
sudo chown -R $USER:$USER /opt/<tool-name>
```

### 2. Backend (Flask) — minimal viable API
Key patterns for a file manager / tool:
- `login_required` decorator checking session
- `get_safe_path()` to prevent path traversal (resolve + relative_to check)
- RESTful JSON API under `/api/*`
- HTML pages served from `/templates/`
- Session-based auth with `flask.session`

**Always include these security measures:**
- `safe_filename()` (custom, NOT werkzeug's `secure_filename`) for all user-supplied filenames — see Chinese filename section
- Path traversal protection: resolve path, verify it's under STORAGE_ROOT
- Session expiry (set `app.permanent_session_lifetime`)
- Password hashing (SHA256 minimum, bcrypt preferred)

### 3. Frontend — single-page with JS fetch
- Use vanilla JS (no framework needed for simple tools)
- Drag-and-drop upload via `FormData` + `fetch`
- Modal dialogs for create/rename operations
- Responsive CSS Grid layout
- Notification system (toast-style)

### 4. Deployment

**Option A: Direct run (simplest)**
```bash
nohup python3 app.py > app.log 2>&1 &
```

**Option B: systemd service (recommended for production)**
```ini
[Unit]
Description=<Tool Name>
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/opt/<tool-name>
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Option C: Docker**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5244
CMD ["python", "app.py"]
```

## Python Environment Pitfalls

⚠️ **CRITICAL: Check Python version BEFORE writing code**

```bash
python3 --version
which python3
```

Common gotchas on older servers:
- System Python may be 3.6 while user has 3.11 via uv/pyenv
- `pip install` may go to wrong site-packages
- Virtual environments may lack pip (`python -m pip` works better)
- uv-managed Pythons reject `pip install` — use `uv pip install` instead
- Always install deps to the SAME Python that will run the app

**Safe install pattern:**
```bash
# If using uv-managed Python
uv pip install flask werkzeug

# If using system Python with pip
sudo pip3 install flask werkzeug -i https://mirrors.aliyun.com/pypi/simple/

# If using venv
/path/to/venv/bin/python -m pip install flask werkzeug
```

## Flask Secret Key — CRITICAL

⚠️ **PITFALL: Never use `secrets.token_hex(32)` for `app.secret_key`**

Random secret keys generated at startup invalidate ALL existing session cookies on restart. Users get logged out every time the app restarts, and may see "password wrong" errors because their session is gone.

```python
# ❌ WRONG — new key on every restart, kills all sessions
app.secret_key = secrets.token_hex(32)

# ✅ CORRECT — static key, sessions persist across restarts
app.secret_key = 'your-app-name-secret-key-YYYY-MM-DD'
```

For production, use an environment variable:
```python
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-static-key')
```

## Flask Version Compatibility

For older Python (3.6-3.8), use:
```
flask>=2.0.0,<3.0
werkzeug>=2.0.0,<3.0
```

For Python 3.9+, latest versions work fine.

## Feature Checklist (File Manager)

When building a file manager, ensure these features:
- [ ] Login with hashed passwords or secret key
- [ ] Chinese filename support (`safe_filename` not `secure_filename`)
- [ ] File listing with size/date/type
- [ ] File upload (multipart form, progress indication)
- [ ] File download (send_file with as_attachment)
- [ ] File preview/viewer (images, video, audio, PDF, text, code)
- [ ] Create folder
- [ ] Rename (file and folder)
- [ ] Delete (with confirmation dialog)
- [ ] Move/organize files (directory tree picker)
- [ ] Breadcrumb navigation
- [ ] Storage space info
- [ ] Drag-and-drop upload zone
- [ ] File type icons
- [ ] Responsive design
- [ ] Mobile long-press context menu

## Chinese User Preferences

- UI text in Chinese
- **NEVER use `secure_filename()`** — it strips ALL Chinese/CJK characters, returning empty strings
  - Use custom `safe_filename()` instead (see `flask-web-tools` skill for full implementation)
- Aliyun pip mirror: `https://mirrors.aliyun.com/pypi/simple/`
- Default port: 5244 (or user-specified)
- File viewer/preview: add `/api/preview` endpoint for inline viewing (see `flask-web-tools` skill)

## References

- `references/alist-troubleshooting.md` — AList permission and storage fixes
- `templates/flask-file-manager.py` — Complete starter template