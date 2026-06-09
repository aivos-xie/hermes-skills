---
name: multi-server-management
description: "Manage multiple remote servers from Hermes via SSH — deploy services, configure firewalls, transfer files, run commands across servers"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [ssh, remote, servers, devops, deployment, multi-host]
---

# Multi-Server Management

Manage multiple remote servers from the Hermes host via SSH. Covers connection, command execution, file transfer, service deployment, and firewall configuration.

## When to Use

- Deploying services to remote servers
- Running commands on servers other than the current host
- Transferring files between servers
- Managing systemd services remotely
- Configuring firewalls and security groups

## Prerequisites

```bash
# Install sshpass for password-based SSH
dnf install -y sshpass    # RHEL/Alibaba Cloud Linux
apt install -y sshpass    # Debian/Ubuntu

# For key-based auth, ensure key is in ~/.ssh/
```

## Core Patterns

### Run command on remote server

```bash
sshpass -p 'PASSWORD' ssh -o StrictHostKeyChecking=no root@REMOTE_IP "command"
```

### Transfer file to remote server

```bash
sshpass -p 'PASSWORD' scp -o StrictHostKeyChecking=no /local/file root@REMOTE_IP:/remote/path
```

### Transfer file from remote server

```bash
sshpass -p 'PASSWORD' scp -o StrictHostKeyChecking=no root@REMOTE_IP:/remote/file /local/path
```

### Check connectivity

```bash
ping -c 2 -W 3 REMOTE_IP
sshpass -p 'PASSWORD' ssh -o ConnectTimeout=5 root@REMOTE_IP "hostname"
```

## Service Deployment Template

```bash
# 1. Upload code
sshpass -p 'PASS' scp -r ./project root@SERVER:/opt/project

# 2. Install dependencies
sshpass -p 'PASS' ssh root@SERVER "pip3 install -r /opt/project/requirements.txt"

# 3. Create systemd service
sshpass -p 'PASS' ssh root@SERVER "cat > /etc/systemd/system/myservice.service << 'EOF'
[Unit]
Description=My Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/project
ExecStart=/usr/bin/python3 /opt/project/app.py
Restart=always
RestartSec=5
EnvironmentFile=-/opt/project/.env

[Install]
WantedBy=multi-user.target
EOF"

# 4. Enable and start
sshpass -p 'PASS' ssh root@SERVER "
systemctl daemon-reload
systemctl enable myservice
systemctl start myservice
systemctl status myservice --no-pager
"
```

## Firewall Configuration

### Alibaba Cloud Linux (firewalld)

```bash
# Check status
firewall-cmd --state

# Open port
firewall-cmd --permanent --add-port=8080/tcp
firewall-cmd --reload

# List open ports
firewall-cmd --list-ports
```

### Important: Security Groups

Alibaba Cloud ECS requires BOTH:
1. OS-level firewall (firewalld/iptables) — open port
2. Cloud security group — add inbound rule for the port

Security group must be configured via Alibaba Cloud console/API. The OS firewall alone is not enough.

## Deploying Hermes Sub-Agent on Remote Server

Use tmux to run a persistent Hermes agent on a remote server that you can control via SSH.

```bash
# 1. Clone Hermes on remote server
sshpass -p 'PASS' ssh root@SERVER "cd /opt && git clone --depth 1 https://github.com/NousResearch/hermes-agent.git"

# 2. Create venv and install
sshpass -p 'PASS' ssh root@SERVER "cd /opt/hermes-agent && python3 -m venv venv && source venv/bin/activate && pip install -e . -q"

# 3. Configure (copy API key from existing .env)
sshpass -p 'PASS' ssh root@SERVER "python3 -c \"
with open('/opt/existing/.env') as f:
    for line in f:
        if 'API_KEY' in line:
            key = line.strip().split('=',1)[1]
            with open('/root/.hermes/.env', 'w') as out:
                out.write(f'XIAOMI_API_KEY={key}\n')
\""

# 4. Create config.yaml
sshpass -p 'PASS' ssh root@SERVER "cat > /root/.hermes/config.yaml << 'EOF'
model:
  default: mimo-v2.5-pro
  provider: xiaomi
  base_url: https://token-plan-cn.xiaomimimo.com/v1
agent:
  max_turns: 50
EOF"

# 5. Start in tmux
sshpass -p 'PASS' ssh root@SERVER "
tmux new-session -d -s hermes-agent -x 120 -y 40
tmux send-keys -t hermes-agent 'cd /opt/hermes-agent && source venv/bin/activate && export XIAOMI_API_KEY=\$(grep XIAOMI_API_KEY /root/.hermes/.env | cut -d= -f2) && hermes chat --yolo' Enter
"

# 6. Send commands to remote agent
sshpass -p 'PASS' ssh root@SERVER "tmux send-keys -t hermes-agent '你的消息' Enter"

# 7. Read output
sshpass -p 'PASS' ssh root@SERVER "tmux capture-pane -t hermes-agent -p -S -30"
```

### Control Script Template

```bash
#!/bin/bash
# hz-agent.sh - 控制远程Hermes子Agent
SERVER="IP"; PASS="PASS"; SESSION="hermes-agent"
case "$1" in
    send) sshpass -p "$PASS" ssh root@$SERVER "tmux send-keys -t $SESSION '$2' Enter" ;;
    read) sshpass -p "$PASS" ssh root@$SERVER "tmux capture-pane -t $SESSION -p -S -${2:-30}" ;;
    status) sshpass -p "$PASS" ssh root@$SERVER "tmux has-session -t $SESSION 2>/dev/null && echo '运行中' || echo '未运行'" ;;
    restart) # kill + restart tmux + hermes ;;
esac
```

## Remote Command API (When SSH Fails)

Two approaches: standalone API on new port, or embed in existing web app (preferred — no new port needed).

### Permanent SSH Key Connection (Preferred for persistent access)

When you need permanent, passwordless SSH access between servers:

```bash
# 1. Generate key on the controlling server
ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519 -N "" -q

# 2. Add public key to target server (run on target)
echo "ssh-ed25519 AAAA... root@hostname" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys

# 3. Configure SSH alias on controlling server
cat >> /root/.ssh/config << 'EOF'
Host hz-server
    HostName TARGET_IP
    User root
    IdentityFile /root/.ssh/id_ed25519
    StrictHostKeyChecking no
EOF
chmod 600 /root/.ssh/config

# 4. Test: ssh hz-server "hostname"
```

**Why this over sshpass**: Permanent, no password in scripts, works with tmux/agent forwarding, survives restarts.

**Chaining through an API**: If the controlling server only has API access (not SSH), deploy the key via the API:
```bash
curl -X POST http://CONTROL_SERVER/api/exec -H "Content-Type: application/json" \
  -d '{"token":"xxx","cmd":"ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519 -N \"\" -q && cat /root/.ssh/id_ed25519.pub"}'
# Then add returned pubkey to target's authorized_keys
# Then test: curl ... -d '{"cmd":"ssh hz-server \"hostname\""}'
```

### Approach A: Embed in Existing Web App (Preferred)

Add `/api/exec` endpoint to the app already running on the target server. No new port, no security group changes needed.

```python
import subprocess

@app.route('/api/exec', methods=['POST'])
def api_exec():
    data = request.json
    if data.get('token') != 'hermes2024':
        return jsonify({'error': 'unauthorized'}), 401
    try:
        proc = subprocess.Popen(data.get('cmd',''), shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(timeout=120)
        return jsonify({
            'stdout': stdout.decode('utf-8', errors='replace'),
            'stderr': stderr.decode('utf-8', errors='replace'),
            'code': proc.returncode
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Why Popen instead of subprocess.run**: `capture_output` and `text` params require Python 3.7+. Use `Popen` + `communicate()` for broader compatibility.

**Usage from Hermes**: `curl -X POST http://SERVER/api/exec -H "Content-Type: application/json" -d '{"token":"hermes2024","cmd":"hostname"}'`

### Approach B: Standalone API on New Port

Use when the target server has no existing web app. Requires port to be opened in security group.

```bash
cat > /opt/hermes-api.py << 'EOF'
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)
TOKEN = "hermes2024"  # Change this!

@app.route('/exec', methods=['POST'])
def exec_cmd():
    if request.headers.get('Authorization') != f'Bearer {TOKEN}':
        return jsonify({'error': 'unauthorized'}), 401
    cmd = request.json.get('cmd', '')
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        return jsonify({'stdout': result.stdout, 'stderr': result.stderr, 'code': result.returncode})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
EOF

pip3 install flask -q
nohup python3 /opt/hermes-api.py > /opt/hermes-api.log 2>&1 &
```

### Step 2: Security group configuration

Only allow Hermes host IP to access the API port:

| Setting | Value |
|---------|-------|
| Authorization | Allow |
| Protocol | Custom TCP |
| Port | 9090/9090 |
| Source | HERMES_HOST_IP/32 |
| Description | Hermes Agent API |

Get Hermes host IP: `curl -s ifconfig.me`

### Step 3: Execute commands via API

```bash
curl -s -X POST http://REMOTE_IP:9090/exec \
  -H "Authorization: Bearer hermes2024" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"echo hello && hostname"}'
```

### Step 4: Use from Hermes

```python
import requests

API_URL = "http://REMOTE_IP:9090/exec"
TOKEN = "hermes2024"

def remote_exec(cmd):
    resp = requests.post(API_URL, 
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        json={"cmd": cmd}, timeout=120)
    return resp.json()

# Example
result = remote_exec("systemctl status chaoxing")
print(result['stdout'])
```

### Security Notes

- Always whitelist only the Hermes host IP, never open to 0.0.0.0/0
- Use a strong random token (not "hermes2024" in production)
- Consider adding IP allowlist in the Flask app itself as defense-in-depth
- Shut down the API when not needed: `pkill -f hermes-api.py`

## Templates

- `templates/hermes-remote-api.py` — Ready-to-deploy Flask API for remote command execution when SSH fails.

## Pitfalls

1. **Alibaba Cloud ECS password auth disabled by default**: New ECS instances may have `PasswordAuthentication no` in sshd_config. SSH connection will fail with "Permission denied" even with correct password. **Fix**: User must connect via Workbench (console web terminal) and run `sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config && systemctl restart sshd`. Always test SSH connectivity BEFORE planning deployment.
2. **Security group vs firewall**: Both must allow the port. If curl times out from outside but works locally, it's the security group.
3. **sshpass not installed**: Always check and install first.
4. **StrictHostKeyChecking**: Always use `-o StrictHostKeyChecking=no` for automated scripts.
5. **ConnectTimeout**: Set 5-10s to avoid hanging on unreachable hosts.
6. **Mobile user provides server info via screenshots**: User operates on phone (JuiceSSH). Server credentials may come as screenshot text. Extract IP/user/pass carefully from image content.
5. **systemd reload**: Always `daemon-reload` after editing service files.
6. **Append vs overwrite**: When adding to config files remotely, use `>>` not `>` to avoid overwriting.
7. **Python module path**: Alibaba Cloud Linux uses `pip3`/`python3`, not `pip`/`python`.
8. **systemd + Python venv**: If Python packages are installed in a virtualenv, `ExecStart` MUST use the venv Python path (e.g., `/home/admin/.hermes/hermes-agent/venv/bin/python3`), NOT `/usr/bin/python3`. Otherwise systemd reports `ModuleNotFoundError`. Check with `journalctl -u service-name -n 30`.
9. **systemd env var masking**: systemd automatically masks environment variable values containing `TOKEN`, `PASSWORD`, `SECRET`, `KEY` etc. in `systemctl show` output (displays `***`). The actual value IS correct in the running process — this is just display masking for security. Don't chase "wrong values" based on `systemctl show`; check the `.env` file directly.
10. **Deploy static files with FastAPI**: No need for Nginx to serve admin pages or scripts. Use `HTMLResponse` for HTML and `FileResponse` for JS/CSS. Keeps everything on one port.
11. **nginx reverse proxy for port mapping**: When a port (e.g. 8080) isn't in the security group and you can't modify it, use nginx to proxy from an already-open port (e.g. 80). Config: `proxy_pass http://127.0.0.1:8080;` with `server_name _;`. Multiple `server_name _` warnings are harmless.
12. **Embedded API vs standalone**: Prefer embedding `/api/exec` in an existing web app (no new port needed) over deploying a standalone API on a new port (requires security group changes).
13. **SSH key re-establishment after server cleanup**: When a server is reimaged/cleaned, all authorized_keys are lost. Use `sshpass` to re-copy the key: `sshpass -p 'NEW_PASS' ssh-copy-id -o StrictHostKeyChecking=no -i ~/.ssh/hermes_key root@SERVER`. Also update `known_hosts` if the host key changed: `ssh-keygen -R SERVER_IP`.

## Multi-Server Command Execution

```bash
# Define servers
SERVERS=("server1:pass1" "server2:pass2")

for entry in "${SERVERS[@]}"; do
    IFS=':' read -r ip pass <<< "$entry"
    echo "=== $ip ==="
    sshpass -p "$pass" ssh -o StrictHostKeyChecking=no root@$ip "uptime"
done
```
