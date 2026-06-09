---
name: flask-web-tools
description: Build and deploy lightweight Flask web tools (file managers, dashboards, admin panels) on Linux servers. Covers Chinese/i18n filenames, mobile touch UX, simple auth, and Docker-free deployment.
triggers:
  - user asks to build a web UI, file manager, admin panel, or dashboard
  - user asks to deploy a Python web app on a server
  - user mentions 文件管理, 网盘, file manager, or web tool
  - user needs a simple internal tool with a web interface
---

# Flask Web Tools

Build lightweight, single-file Flask web tools for server deployment. No heavy frameworks — Flask + inline HTML templates + vanilla JS.

## Project Structure

```
/opt/<app-name>/
├── app.py              # Flask backend (all routes)
├── templates/
│   ├── login.html      # Auth page
│   ├── index.html      # Main app page
│   └── 404.html        # Error page
├── storage/            # User data (if file manager)
└── requirements.txt    # flask, werkzeug
```

## Step-by-Step

1. **Create project directory** under `/opt/<app-name>/`
2. **Write `app.py`** with all routes in one file (no blueprints for simple tools)
3. **Write HTML templates** with inline CSS/JS (no build step, no npm)
4. **Install deps**: `uv pip install flask werkzeug` or use system pip with `-i https://mirrors.aliyun.com/pypi/simple/`
5. **Run as background process**: `terminal(background=true)` with the venv python
6. **Test all endpoints** with curl before telling user it's ready

## Authentication Patterns

### Secret Key Login (simplest)
```python
SECRET_KEY = '699613'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        key = request.form.get('key', '').strip()
        if key == SECRET_KEY:
            session['authenticated'] = True
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=72)
            return redirect(url_for('index'))
        return render_template('login.html', error='秘钥错误')
    return render_template('login.html')
```

### Username/Password with Hash
```python
import hashlib
USERS = {'admin': {'password_hash': hashlib.sha256('password'.encode()).hexdigest()}}

def verify_password(password, password_hash):
    return hashlib.sha256(password.encode()).hexdigest() == password_hash
```

### Login Decorator
```python
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'authenticated' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': '未登录'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated
```

## Critical Pitfalls

### Pitfall: `secure_filename` strips Chinese/CJK characters
`werkzeug.utils.secure_filename` removes ALL non-ASCII characters. Chinese filenames become empty strings.

**Fix — custom safe_filename:**
```python
def safe_filename(name):
    """安全文件名：支持中文，防止路径穿越"""
    name = name.replace("\\", "/").split("/")[-1]
    name = name.replace("\x00", "")
    name = name.replace("..", "")
    name = name.strip(". ")
    if not name:
        return ""
    return name
```
Use this instead of `secure_filename` for all user-provided filenames.

### Pitfall: Hover-only buttons invisible on mobile
CSS `opacity: 0` with `:hover { opacity: 1 }` makes buttons invisible on touch devices (no hover state).

**Two solutions:**
1. **Always visible**: Remove opacity rules entirely, buttons always shown
2. **Long-press action sheet** (better UX): Add touch event handlers for mobile context menu

### Pitfall: AJAX login forms can fail silently
Complex `fetch()`-based login can fail due to CORS, content-type mismatch, or JS errors. For simple tools, **use plain HTML form POST** — it's more reliable and works without JavaScript.

```html
<form method="POST" action="/login">
    <input type="text" name="key" required>
    <button type="submit">登录</button>
</form>
```

### Pitfall: Flask secret_key changes on restart
Using `secrets.token_hex(32)` generates a new key each restart, invalidating all session cookies. Use a **fixed secret key** for tools that need persistent sessions.

### Pitfall: Python version mismatch on pip install
On systems with multiple Python versions, `pip3 install` may install to the wrong Python. Use the specific python binary:
```bash
/home/admin/.hermes/hermes-agent/venv/bin/python -m pip install flask
# or
uv pip install flask  # if using uv-managed venv
```

## Mobile Long-Press Context Menu

For file managers and list-based UIs, add touch-based long-press:

```javascript
let pressTimer = null;
let actionFile = null;

function pressStart(e, idx) {
    pressEnd(e);
    pressTimer = setTimeout(() => {
        const f = window._files[idx];
        showActionSheet(f);
        if (navigator.vibrate) navigator.vibrate(50); // haptic feedback
    }, 500); // 500ms threshold
}

function pressEnd(e) {
    if (pressTimer) { clearTimeout(pressTimer); pressTimer = null; }
}
```

Attach to rows: `ontouchstart`, `ontouchend`, `ontouchmove`, `ontouchcancel`, `onmousedown`, `onmouseup`, `onmouseleave`.

Action sheet CSS: fixed bottom sheet with slide-up animation, `position: fixed; bottom: 0`.

## CSS Patterns

### Responsive file list (hide columns on mobile)
```css
@media (max-width: 700px) {
    .list-head, .row { grid-template-columns: 1fr 80px; }
    .ftime, .fops { display: none; }  /* hide time + ops columns */
}
```

### Modal overlay
```css
.modal-bg { position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,.4); display: none; z-index: 100; }
.modal-bg.show { display: flex; align-items: center; justify-content: center; }
```

### Toast notification
```css
.toast { position: fixed; top: 20px; right: 20px; transform: translateX(120%);
         transition: transform .3s; z-index: 200; }
.toast.show { transform: translateX(0); }
```

## Path Traversal Prevention

Always validate file paths to prevent `../../../etc/passwd` attacks:

```python
def get_safe_path(path):
    path = path.strip('/')
    parts = []
    for part in path.split('/'):
        if part in ('', '.'): continue
        if part == '..':
            if parts: parts.pop()
            continue
        parts.append(part)
    safe_path = STORAGE_ROOT.joinpath(*parts)
    try:
        safe_path.resolve().relative_to(STORAGE_ROOT.resolve())
        return safe_path
    except ValueError:
        return STORAGE_ROOT  # fallback to root if path escapes
```

## File Viewer / Preview

Add inline file viewing so users can click a file and see it without downloading.

### Backend: `/api/preview` endpoint

```python
@app.route('/api/preview')
@login_required
def preview_file():
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': '未指定文件'}), 400
    target_file = get_safe_path(file_path)
    if not target_file.exists() or not target_file.is_file():
        return jsonify({'error': '文件不存在'}), 404
    mime_type = mimetypes.guess_type(target_file.name)[0] or 'application/octet-stream'
    # Text files: force UTF-8
    text_exts = {'.txt','.md','.json','.xml','.html','.htm','.css','.js','.py','.sh',
                 '.yaml','.yml','.toml','.ini','.cfg','.conf','.log','.csv','.sql',
                 '.java','.c','.cpp','.h','.go','.rs','.rb','.php','.swift','.kt',
                 '.lua','.env','.properties','.vue','.jsx','.tsx','.ts','.svelte'}
    ext = os.path.splitext(target_file.name)[1].lower()
    if ext in text_exts or mime_type.startswith('text/'):
        mime_type = 'text/plain; charset=utf-8'
    return send_file(str(target_file), mimetype=mime_type)
```

⚠️ **PITFALL: This route MUST be placed BEFORE `if __name__ == '__main__':`.**
Flask ignores routes defined after the main block. If you append with `cat >>`, the route won't register.

### Frontend: viewer modal

Types and their rendering:
| Type | Detection | HTML |
|------|-----------|------|
| Image | `type.startsWith('image/')` | `<img src="/api/preview?path=...">` |
| Video | `type.startsWith('video/')` | `<video controls autoplay><source ...>` |
| Audio | `type.startsWith('audio/')` | `<audio controls autoplay><source ...>` |
| PDF | `ext === 'pdf'` | `<iframe src="/api/preview?path=...">` |
| Text/Code | ext in text_exts list | `fetch(url).then(r => r.text())` → `<pre>` |
| Office | doc/xls/ppt/odt | `<iframe src="https://view.officeapps.live.com/op/embed.aspx?src=...">` |
| Other | fallback | Download prompt |

Viewer CSS: full-screen dark overlay (z-index: 200), top bar with filename + close + download buttons, body centered with scrollable content.

**Office preview caveat**: Microsoft's online viewer requires the file URL to be publicly accessible. Works on public servers, won't work on localhost/LAN.

## Critical Pitfall: Flask Route Placement

⚠️ **Routes defined AFTER `if __name__ == '__main__':` are NOT registered.**

When appending routes (e.g., `cat >> app.py`), always insert BEFORE the main block:
```python
# ✅ Correct order
@app.route('/api/new-endpoint')
def new_func(): ...

if __name__ == '__main__':
    app.run(...)

# ❌ WRONG — route never registers
if __name__ == '__main__':
    app.run(...)

@app.route('/api/new-endpoint')  # ← ignored!
def new_func(): ...
```

Fix: split file, move routes above `if __name__`, or rewrite the whole file.

## Serving Public Static Files (No Auth Required)

For admin panels, userscripts, or test pages that should be accessible without login:

```python
# Public routes — BEFORE login_required routes
@app.route('/admin.html')
def serve_admin():
    return send_file(str(STORAGE_ROOT / 'admin.html'))

@app.route('/chaoxing.user.js')
def serve_userscript():
    return send_file(str(STORAGE_ROOT / 'chaoxing.user.js'), mimetype='application/javascript')

@app.route('/test-video.html')
def serve_test():
    return send_file(str(STORAGE_ROOT / 'test-video.html'))
```

**Use case**: Self-contained tools where the admin UI and API client scripts are served from the same Flask app. Users access `http://server/admin.html` directly without logging into the file manager.

## Deployment Checklist

1. [ ] Fixed secret_key (not random per restart)
2. [ ] Chinese filename support (custom `safe_filename`)
3. [ ] Path traversal prevention
4. [ ] Mobile responsive (or long-press menu)
5. [ ] Upload size limit: `app.config['MAX_CONTENT_LENGTH']`
6. [ ] File preview/viewer endpoint
7. [ ] Background process with `terminal(background=true)`
8. [ ] Test all CRUD operations with curl before announcing
9. [ ] All routes placed BEFORE `if __name__ == '__main__':`
