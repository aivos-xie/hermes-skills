# Remote Hermes Sub-Agent Deployment

Full worked example: deploying a Hermes sub-agent on a remote Alibaba Cloud ECS and controlling it from the local agent via SSH + tmux.

## Environment

- Local: 8.162.25.142 (Alinux 3, 2-core 1.8GB)
- Remote: 47.96.236.144 (Alinux 4, 2-core 2GB)
- Model: mimo-v2.5-pro (Xiaomi MiMo)
- **Auth: SSH key-based via alias** (preferred, see below)

## Auth Methods

### Method 1: SSH Key + Config Alias (current, preferred)

```bash
# ~/.ssh/config
Host hz-server
    HostName 47.96.236.144
    User root
    IdentityFile ~/.ssh/hermes_key
    StrictHostKeyChecking no

# Usage
ssh hz-server 'command here'
```

### Method 2: sshpass + password (legacy)

```bash
sshpass -p "$PASS" ssh root@47.96.236.144 'command here'
```

Key-based is preferred — no password exposure in command history or logs.

## Installation Script

```bash
REMOTE="47.96.236.144"

# Install system deps
ssh hz-server "yum install -y git tmux && pip3 install pipx"

# Clone Hermes (shallow)
ssh hz-server "cd /opt && git clone --depth 1 https://github.com/NousResearch/hermes-agent.git"

# Create venv + install
ssh hz-server "cd /opt/hermes-agent && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip -q && pip install -e . -q"
```

## Configuration

```bash
ssh hz-server 'python3 -c "
import os
os.makedirs(\"/root/.hermes\", exist_ok=True)
with open(\"/root/.hermes/.env\", \"w\") as f:
    f.write(\"XIAOMI_API_KEY=your_key_here\n\")
with open(\"/root/.hermes/config.yaml\", \"w\") as f:
    f.write(\"\"\"model:
  default: mimo-v2.5-pro
  provider: xiaomi
  base_url: https://token-plan-cn.xiaomimimo.com/v1
agent:
  max_turns: 50
terminal:
  timeout: 120
display:
  tool_progress: false
  show_cost: false\"\"\")
print(\"Config written\")
"'
```

## Launch in tmux

```bash
# Create tmux session
ssh hz-server "tmux new-session -d -s hermes-agent -x 120 -y 40"

# Start hermes
ssh hz-server "tmux send-keys -t hermes-agent 'cd /opt/hermes-agent && source venv/bin/activate && export XIAOMI_API_KEY=\$(grep XIAOMI_API_KEY /root/.hermes/.env | cut -d= -f2) && hermes chat --yolo -Q' Enter"

# Wait for initialization (8-10 seconds)
sleep 10

# Verify
ssh hz-server "tmux capture-pane -t hermes-agent -p | tail -10"
```

## Control Commands

```bash
# Send a message
ssh hz-server "tmux send-keys -t hermes-agent 'your message' Enter"

# Read output
sleep 10
ssh hz-server "tmux capture-pane -t hermes-agent -p -S -30 | tail -20"

# Check if running
ssh hz-server "tmux has-session -t hermes-agent 2>/dev/null && echo 'running' || echo 'stopped'"
```

## Pitfalls Encountered

1. **`hermes chat -q '中文'` fails** — argparse interprets CJK characters as a subcommand. Use `hermes -q '中文'` or pipe input.

2. **SSH output redaction** — SSH may redact strings that look like API keys. Write .env files using `python3 -c "..."` on the remote side.

3. **systemd Python path** — `/usr/bin/python3` on Alibaba Cloud doesn't have pip-installed packages. Use the venv Python: `/opt/hermes-agent/venv/bin/python3`.

4. **systemd + .env file** — `EnvironmentFile=` may not work if the .env uses `export` or has comments. Prefer inline `Environment=` directives.

5. **SQLite schema migration** — When upgrading a FastAPI backend that adds new columns, run `ALTER TABLE ... ADD COLUMN` before restarting.

6. **Firewall vs Security Group** — `firewalld` port opening is separate from Alibaba Cloud security group rules. Both must be configured.

## Control Script Template

Save as `~/hz-agent.sh`:

```bash
#!/bin/bash
SESSION="hermes-agent"
case "$1" in
  send)  ssh hz-server "tmux send-keys -t $SESSION '$2' Enter" ;;
  read)  ssh hz-server "tmux capture-pane -t $SESSION -p -S -${2:-30}" ;;
  status) ssh hz-server "tmux has-session -t $SESSION 2>/dev/null && echo 'running' || echo 'stopped'" ;;
  restart)
    ssh hz-server "tmux kill-session -t $SESSION 2>/dev/null; sleep 1"
    ssh hz-server "tmux new-session -d -s $SESSION -x 120 -y 40; sleep 1"
    ssh hz-server "tmux send-keys -t $SESSION 'cd /opt/hermes-agent && source venv/bin/activate && hermes chat --yolo -Q' Enter"
    sleep 8; ssh hz-server "tmux capture-pane -t $SESSION -p | tail -10"
    ;;
  *) echo "Usage: $0 {send|read|status|restart} [message|lines]" ;;
esac
```
