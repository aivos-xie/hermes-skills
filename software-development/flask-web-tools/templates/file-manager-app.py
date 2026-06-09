#!/usr/bin/env python3
"""
aivos 的网盘 - 秘钥登录版
简洁的文件管理器，支持上传/下载/重命名/删除/移动
"""

import os
import shutil
import mimetypes
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

from flask import (
    Flask, request, jsonify, send_file,
    render_template, redirect, url_for,
    session
)

# 配置
app = Flask(__name__)
app.secret_key = 'CHANGE-ME-to-fixed-secret'  # 必须固定，不能每次重启变化
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# 秘钥
SECRET_KEY = '699613'

# 存储路径
STORAGE_ROOT = Path('/opt/myapp/storage')
STORAGE_ROOT.mkdir(exist_ok=True)

SESSION_EXPIRY_HOURS = 72


def safe_filename(name):
    """安全文件名：支持中文，防止路径穿越"""
    name = name.replace("\\", "/").split("/")[-1]
    name = name.replace("\x00", "")
    name = name.replace("..", "")
    name = name.strip(". ")
    return name if name else ""


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'authenticated' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': '未登录'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def get_safe_path(path):
    if not path:
        path = '/'
    path = path.strip('/')
    if not path:
        return STORAGE_ROOT
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
        return STORAGE_ROOT


def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def get_file_info(file_path, relative_path):
    stat = file_path.stat()
    return {
        'name': file_path.name,
        'path': str(relative_path),
        'is_dir': file_path.is_dir(),
        'size': stat.st_size if file_path.is_file() else 0,
        'size_formatted': format_size(stat.st_size) if file_path.is_file() else '-',
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        'type': mimetypes.guess_type(file_path.name)[0] if file_path.is_file() else 'folder'
    }


# ==================== 路由 ====================

@app.route('/')
def index():
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        key = request.form.get('key', '').strip()
        if key == SECRET_KEY:
            session['authenticated'] = True
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=SESSION_EXPIRY_HOURS)
            return redirect(url_for('index'))
        return render_template('login.html', error='秘钥错误')
    if 'authenticated' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/files')
@login_required
def list_files():
    path = request.args.get('path', '/')
    target_dir = get_safe_path(path)
    if not target_dir.exists() or not target_dir.is_dir():
        return jsonify({'error': '目录不存在'}), 404
    files = []
    try:
        for item in sorted(target_dir.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            if item.name.startswith('.'):
                continue
            relative_path = item.relative_to(STORAGE_ROOT)
            files.append(get_file_info(item, relative_path))
    except PermissionError:
        return jsonify({'error': '权限不足'}), 403
    return jsonify({'path': path, 'files': files, 'total': len(files)})

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    target_path = request.form.get('path', '/')
    target_dir = get_safe_path(target_path)
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = safe_filename(file.filename)
    if not filename:
        filename = 'unnamed_file'
    file_path = target_dir / filename
    counter = 1
    original_name = filename
    while file_path.exists():
        name, ext = os.path.splitext(original_name)
        filename = f"{name}_{counter}{ext}"
        file_path = target_dir / filename
        counter += 1
    file.save(str(file_path))
    relative_path = file_path.relative_to(STORAGE_ROOT)
    return jsonify({'success': True, 'message': f'文件 {filename} 上传成功', 'file': get_file_info(file_path, relative_path)})

@app.route('/api/download')
@login_required
def download_file():
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': '未指定文件'}), 400
    target_file = get_safe_path(file_path)
    if not target_file.exists() or not target_file.is_file():
        return jsonify({'error': '文件不存在'}), 404
    return send_file(str(target_file), as_attachment=True, download_name=target_file.name)

@app.route('/api/mkdir', methods=['POST'])
@login_required
def create_folder():
    data = request.get_json()
    path = data.get('path', '/')
    name = data.get('name', '')
    if not name:
        return jsonify({'error': '文件夹名为空'}), 400
    name = safe_filename(name)
    if not name:
        return jsonify({'error': '文件夹名无效'}), 400
    target_dir = get_safe_path(path)
    new_folder = target_dir / name
    if new_folder.exists():
        return jsonify({'error': '文件夹已存在'}), 409
    try:
        new_folder.mkdir(parents=True, exist_ok=True)
        relative_path = new_folder.relative_to(STORAGE_ROOT)
        return jsonify({'success': True, 'message': f'文件夹 {name} 创建成功', 'folder': get_file_info(new_folder, relative_path)})
    except Exception as e:
        return jsonify({'error': f'创建失败: {str(e)}'}), 500

@app.route('/api/rename', methods=['POST'])
@login_required
def rename_item():
    data = request.get_json()
    old_path = data.get('path', '')
    new_name = data.get('new_name', '')
    if not old_path or not new_name:
        return jsonify({'error': '参数不完整'}), 400
    target = get_safe_path(old_path)
    if not target.exists():
        return jsonify({'error': '文件或文件夹不存在'}), 404
    new_name = safe_filename(new_name)
    if not new_name:
        return jsonify({'error': '名称无效'}), 400
    new_path = target.parent / new_name
    if new_path.exists():
        return jsonify({'error': '目标名称已存在'}), 409
    try:
        target.rename(new_path)
        relative_path = new_path.relative_to(STORAGE_ROOT)
        return jsonify({'success': True, 'message': '重命名成功', 'item': get_file_info(new_path, relative_path)})
    except Exception as e:
        return jsonify({'error': f'重命名失败: {str(e)}'}), 500

@app.route('/api/delete', methods=['POST'])
@login_required
def delete_item():
    data = request.get_json()
    path = data.get('path', '')
    if not path:
        return jsonify({'error': '未指定路径'}), 400
    target = get_safe_path(path)
    if not target.exists():
        return jsonify({'error': '文件或文件夹不存在'}), 404
    try:
        if target.is_file():
            target.unlink()
            return jsonify({'success': True, 'message': '文件已删除'})
        elif target.is_dir():
            shutil.rmtree(str(target))
            return jsonify({'success': True, 'message': '文件夹已删除'})
    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500

@app.route('/api/storage-info')
@login_required
def storage_info():
    total, used, free = shutil.disk_usage(str(STORAGE_ROOT))
    return jsonify({'total': format_size(total), 'used': format_size(used), 'free': format_size(free)})

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': '接口不存在'}), 404
    return render_template('404.html'), 404

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': '文件太大，最大支持500MB'}), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5244, debug=False)
