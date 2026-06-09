---
name: custom-file-manager
description: Build custom web-based file managers with Flask — upload, download, rename, move, delete, mkdir. Supports Chinese filenames, secret-key auth, drag-and-drop upload. Use when the user wants a self-hosted file server, web disk, or lightweight AList/Nextcloud replacement.
triggers:
  - file manager
  - web disk
  - web file server
  - 网盘
  - file sharing server
  - self-hosted file server
  - AList replacement
  - upload download server
---

# Custom File Manager

Build a self-hosted web file manager using Python Flask. Designed for Chinese-speaking users who want a simple, clean alternative to AList/Nextcloud.

## Architecture

```
/opt/<project>/
├── app.py              # Flask backend (all-in-one)
├── requirements.txt    # flask>=2.0.0, werkzeug>=2.0.0
├── storage/            # File storage root
└── templates/
    ├── login.html      # Minimal login page
    ├── index.html      # Main file manager UI
    └── 404.html        # Error page
```

## Authentication: Secret Key Pattern

User prefers **single secret key** over username/password for simplicity.

```python
SECRET_KEY = '699613'  # User-configured

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

Login page: single centered input box + submit button. Show error on wrong key. Keep it minimal.

## Critical Pitfall: Chinese Filenames

**`werkzeug.utils.secure_filename` strips ALL non-ASCII characters.** For Chinese users this is a showstopper — Chinese folder/file names become empty strings.

### ❌ Broken
```python
from werkzeug.utils import secure_filename
secure_filename('测试文件夹')  # returns ''
```

### ✅ Fix: Custom `safe_filename`
```python
def safe_filename(name):
    """安全文件名：支持中文，防止路径穿越"""
    name = name.replace("\\", "/").split("/")[-1]  # no path traversal
    name = name.replace("\x00", "")                 # no null bytes
    name = name.replace("..", "")                   # no parent ref
    name = name.strip(". ")                         # no hidden/special
    if not name:
        return ""
    return name
```

Replace ALL `secure_filename()` calls with `safe_filename()` — applies to upload, mkdir, rename.

## Security: Path Traversal Prevention

```python
def get_safe_path(path):
    """Resolve user path to safe absolute path under STORAGE_ROOT"""
    if not path:
        path = '/'
    path = path.strip('/')
    parts = []
    for part in path.split('/'):
        if part in ('', '.'):
            continue
        if part == '..':
            if parts:
                parts.pop()
            continue
        parts.append(part)
    safe_path = STORAGE_ROOT.joinpath(*parts)
    try:
        safe_path.resolve().relative_to(STORAGE_ROOT.resolve())
        return safe_path
    except ValueError:
        return STORAGE_ROOT  # fallback to root
```

## Required API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/files?path=/` | List directory contents |
| POST | `/api/upload` | Upload file (multipart, field: `file` + `path`) |
| GET | `/api/download?path=/file` | Download file |
| GET | `/api/preview?path=/file` | Preview file inline (images, video, audio, PDF, text) |
| POST | `/api/mkdir` | Create folder `{path, name}` |
| POST | `/api/rename` | Rename `{path, new_name}` |
| POST | `/api/delete` | Delete `{path}` |
| GET | `/api/storage-info` | Disk usage stats |

## Frontend Design

- **Single-page app** with vanilla JS (no frameworks)
- **Modals** for: mkdir, upload, rename, move
- **Drag-and-drop** upload zone
- **Breadcrumb** navigation
- **Per-row action buttons** (download, rename, move, delete) that appear on hover
- **Toast notifications** for success/error
- **Responsive**: hide columns on mobile, stack toolbar vertically

### Move/Organize Files

The "整理文件" (organize files) feature is implemented as a **directory tree picker** modal:
1. Load root dirs via `/api/files?path=/`
2. Show clickable folder list with current selection highlighted
3. Double-click to expand into subdirectory
4. Confirm moves via `/api/rename` (rename changes the path prefix)

## Deployment

```bash
# Install deps
pip install flask werkzeug -i https://mirrors.aliyun.com/pypi/simple/

# Run
python app.py  # host=0.0.0.0, port=5244

# Or background
nohup python app.py > app.log 2>&1 &
```

Use `app.secret_key = '<fixed-key>'` (not `secrets.token_hex()`) so sessions survive restarts.

## Pitfall: AList Docker Port Conflict

If replacing AList with this custom app on the same port (5244), AList's Docker container will keep restarting and抢占端口. `kill` won't help — Docker daemon restarts it.

```bash
# Stop AList Docker container permanently
sudo docker stop alist
# Or remove it entirely
sudo docker rm -f alist

# Verify port is free
netstat -tlnp | grep 5244
```

Check `sudo docker ps | grep alist` before starting the Flask app.

## File Type Icons

Map MIME types to emoji for the file list:
- 📁 folder, 🖼️ image, 🎥 video, 🎵 audio
- 📕 pdf, 📝 word/doc, 📊 excel, 📈 ppt
- 📦 archive (zip/rar/7z), 📄 default

## File Viewer / Preview

Click a file name to open it inline in a full-screen viewer modal:
- **Images**: `<img>` tag, max-width/height 100%
- **Video**: `<video controls autoplay>` with `<source>`
- **Audio**: `<audio controls autoplay>` with `<source>`
- **PDF**: `<iframe>` with preview endpoint as src
- **Text/Code**: `fetch()` the preview URL, display in `<pre>` with dark theme
- **Office (doc/xls/ppt)**: Microsoft online viewer iframe (requires public URL)
- **Unsupported**: Show file icon + download button

Backend: `/api/preview` endpoint that serves files with correct MIME type (inline, not attachment). Force `text/plain; charset=utf-8` for text/code file extensions.

⚠️ **Route must be placed BEFORE `if __name__ == '__main__':`** — Flask ignores routes after the main block.

## Public Routes (Bypassing Auth)

Some files need to be accessible without login (admin panels, user scripts, public assets). Add routes **before** the authenticated routes:

```python
# Public pages — no @login_required
@app.route('/admin.html')
def serve_admin():
    return send_file(str(STORAGE_ROOT / 'admin.html'))

@app.route('/chaoxing.user.js')
def serve_userscript():
    return send_file(str(STORAGE_ROOT / 'chaoxing.user.js'), mimetype='application/javascript')

# All other routes remain behind @login_required
@app.route('/')
def index():
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')
```

**Use case**: Hosting admin panels and tampermonkey scripts on the same Flask server as the file manager — one domain, one port, no extra Nginx. The file manager stays locked down, but specific files are publicly accessible.