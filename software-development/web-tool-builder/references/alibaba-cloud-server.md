# Alibaba Cloud ECS Server Environment

## Server Details
- **OS**: Alibaba Cloud Linux (kernel 5.10.134-19.3.2.al8.x86_64)
- **IP**: 8.162.25.142
- **User**: admin (home: /home/admin)

## Python Environment

The server has TWO Python installations:

### 1. System Python 3.6 (legacy)
```bash
/usr/bin/python3 → Python 3.6
pip3 install → installs to /usr/local/lib/python3.6/
```

### 2. uv-managed Python 3.11 (primary)
```bash
/home/admin/.local/bin/python3.11 → Python 3.11.15
```

**⚠️ IMPORTANT**: The Hermes Agent venv uses the uv-managed Python:
```bash
/home/admin/.hermes/hermes-agent/venv/bin/python → Python 3.11.15
```

### Installing Packages

```bash
# ✅ CORRECT — use uv for the venv Python
uv pip install flask werkzeug

# ✅ CORRECT — use venv's python -m pip
/home/admin/.hermes/hermes-agent/venv/bin/python -m pip install flask

# ❌ WRONG — installs to Python 3.6 site-packages
pip3 install flask

# ❌ WRONG — uv-managed Python rejects direct pip
/home/admin/.local/bin/python3.11 -m pip install flask
# Error: externally-managed-environment
```

### Running Apps
```bash
# Use the venv Python for running Flask apps
/home/admin/.hermes/hermes-agent/venv/bin/python app.py

# Or with terminal background=true
cd /opt/myapp && /home/admin/.hermes/hermes-agent/venv/bin/python app.py
```

## Pip Mirror (China)

Default PyPI is slow/unreliable from China. Use Aliyun mirror:
```bash
uv pip install flask -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
# or
sudo pip3 install flask -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

## Docker

Docker requires sudo:
```bash
sudo docker ps
sudo docker exec -it container_name command
```

## Port Allocation

Currently in use:
- 5244: AList / custom web tools
- 5700: QingLong panel
- 3001: Uptime Kuma
- 5230: Memos

## File Permissions

`/opt/` requires sudo for directory creation:
```bash
sudo mkdir -p /opt/myapp
sudo chown -R admin:admin /opt/myapp
```
