---
name: docker-alibaba-cloud
description: "Docker deployment on Alibaba Cloud Linux — mirror config, common services, troubleshooting."
version: 1.0.0
author: agent
metadata:
  hermes:
    tags: [docker, alibaba-cloud, deployment, containers, devops]
---

# Docker on Alibaba Cloud Linux

Deploy and manage Docker containers on Alibaba Cloud ECS (Alinux 3 / CentOS 8 based).

## CRITICAL: Configure Mirrors FIRST (Step 0)

**BEFORE any `docker pull` or `docker run` with a new image, ALWAYS configure China mirrors.** Without mirrors, pulls from Docker Hub are extremely slow (often <50KB/s) or time out completely on Alibaba Cloud ECS. This is not optional — it is a prerequisite.

```bash
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://docker.m.daocloud.io",
    "https://docker.nju.edu.cn"
  ]
}
EOF
sudo systemctl daemon-reload && sudo systemctl restart docker
```

**Verify mirrors are active:**
```bash
sudo docker info | grep -A5 "Registry Mirrors"
```

**If not configured, you WILL hit:** commands hanging for minutes, timeouts, user frustration. Do this ONCE at server setup time.

## Docker Installation

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io --exclude=docker-ce-rootless-extras
sudo systemctl start docker && sudo systemctl enable docker
```

**Pitfall:** `docker-ce-rootless-extras` has checksum mismatch on Alibaba mirrors. Always use `--exclude=docker-ce-rootless-extras`.

## Working Mirror Sources

Docker Hub is often unreachable from Alibaba Cloud ECS. These mirrors work:

```json
{
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://docker.m.daocloud.io",
    "https://docker.nju.edu.cn"
  ]
}
```

**Failed mirrors** (as of 2026-06): `docker.mirrors.ustc.edu.cn`, `hub-mirror.c.163.com`, `mirror.ccs.tencentyun.com`, `registry.cn-hangzhou.aliyuncs.com` (only for private repos).

**⚠️ CRITICAL:** 配置镜像源后必须 `sudo systemctl daemon-reload && sudo systemctl restart docker` 才生效。不配镜像源直接pull，一个100MB镜像可能要10分钟+。

Apply: write to `/etc/docker/daemon.json`, then `sudo systemctl daemon-reload && sudo systemctl restart docker`.

## QingLong Panel (青龙面板)

```bash
sudo docker pull whyour/qinglong:latest
sudo docker run -dit --name qinglong --restart=always \
  -p 5700:5700 -v /root/ql/data:/ql/data whyour/qinglong:latest
```

### API Usage

Login to get token:
```bash
TOKEN=$(curl -s -X POST http://localhost:5700/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"USER","password":"PASS"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")
```

Add cron job:
```bash
curl -s -X POST http://localhost:5700/api/crons \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Task Name","command":"task script.js","schedule":"30 8 * * *"}'
```

### Dependencies

Install via Web UI (依赖管理) — the API for dependency install has validation issues.
- Node.js: axios, crypto-js, cheerio, js-yaml
- Python3: requests, urllib3

### Pitfalls

- New install needs web UI initialization (set username/password)
- `pnpm` store location conflicts after container restart — use web UI for dependency management
- Port 5700 must be open in Alibaba Cloud security group AND in local firewalld

## Firewalld (Port Management)

Alibaba Cloud Linux 3 uses `firewalld` by default (not raw iptables). Opening a port requires TWO steps:

**Step 1: Local firewall**
```bash
sudo firewall-cmd --add-port=PORT/tcp --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports  # verify
```

**Step 2: Alibaba Cloud security group**
Go to ECS console → Security Group → Add inbound rule → TCP/PORT/0.0.0.0/0

**Pitfall:** Docker's port mapping (`-p 5700:5700`) bypasses firewalld for the mapped port. But if you run a non-Docker service on a custom port, firewalld WILL block it unless explicitly opened.

## Critical: Configure Docker Mirrors First

**Docker Hub is extremely slow from Alibaba Cloud ECS.** Always configure mirrors BEFORE pulling any images. Failure to do so causes timeouts and user frustration.

```bash
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://docker.m.daocloud.io",
    "https://docker.nju.edu.cn"
  ]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

**Pitfall:** Always configure mirrors as the VERY FIRST step before any `docker pull`. Even one pull without mirrors can timeout after 2+ minutes and frustrate the user.

**Pitfall:** Use `background=true` for long-running `docker pull` operations. Do NOT block the user waiting for image downloads.

- `iptables -L` shows `policy ACCEPT` but firewalld still blocks ports. Use `firewall-cmd` commands, not raw iptables.
- **挂载宿主机根目录到容器不要加:ro** — `:ro`是只读，用户无法写入。需要写入时去掉`:ro`。
- **Docker容器内SQLite WAL模式** — 直接在宿主机修改容器内的sqlite数据库会失败（WAL锁定），需要停止容器后再修改，或使用应用自身的API。
- **AList等应用密码存储** — 密码可能存储在WAL文件中，宿主机sqlite3查询显示为空但认证正常工作。不要尝试直接修改数据库，用应用API。

**Pitfall:** ALWAYS check if security group ports are open BEFORE deploying a new service. If the user says "I'll open the ports later", DO NOT deploy — wait for confirmation. Deploying a service that can't be accessed wastes everyone's time and causes frustration.

**Pitfall:** When deploying multiple services, pull ALL images in background first, then run containers. Do NOT pull one-by-one in foreground — each pull can take 2+ minutes on Alibaba Cloud.

**Pitfall:** For large images (>100MB), use `terminal(background=True)` or run `docker pull` in a separate background process. Foreground pulls block the conversation and cause timeouts/user frustration. Better: pull in background, then `docker run` after.

**Pitfall:** When user says "等会我放行端口" (I'll open ports later), STOP and wait. Do NOT continue deploying. The user will tell you when ports are open. Deploying before ports are open wastes time.

## Deploying Multiple Services

When deploying 2+ Docker services in sequence:
1. Configure mirrors (once, Step 0)
2. Pull ALL images in parallel using background tasks
3. Run all containers after pulls complete
4. Open all ports at once (local firewall + remind user about security group)
5. Report all access URLs in one message

Do NOT deploy one-by-one with foreground pulls — it's slow and frustrating.

**User preference: Quick, direct answers.** When user asks "能不能?" (can you?), answer YES/NO first, then explain. Don't start with long explanations.

## Self-Hosted Services Quick Reference

### AList — File Sharing / Cloud Storage

See `references/alist-api.md` for full API reference.

**Deployment:**
```bash
sudo docker pull xhofe/alist:latest
sudo docker run -d --restart=always --name alist \
  -p 5244:5244 \
  -v /opt/alist/data:/opt/alist/data \
  -v /:/host \
  -e PUID=0 -e PGID=0 -e UMASK=022 \
  xhofe/alist:latest
```

**First-time setup (API):**
```bash
# Get initial password
INIT_PASS=$(sudo docker logs alist 2>&1 | grep -oP 'password is: \K\S+')
TOKEN=$(curl -s http://localhost:5244/api/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"$INIT_PASS\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# Change username and password
curl -s http://localhost:5244/api/admin/user/update -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"id":2,"username":"NEW_USER","password":"NEW_PASS","role":[2],"disabled":false,"permission":65535,"base_path":"/","sso_id":""}'

# Configure storage (mount host filesystem)
curl -s http://localhost:5244/api/admin/storage/update -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"id":1,"mount_path":"/","order":0,"driver":"Local","cache_expiration":30,"status":"work","addition":"{\"root_folder_path\":\"/host\",\"thumbnail\":false,\"show_hidden\":true,\"mkdir_perm\":\"777\",\"recycle_bin_path\":\"delete permanently\"}"}'

# Enable guest upload (permission: view+download+upload+mkdir = 1+2+4+8 = 15)
curl -s http://localhost:5244/api/admin/user/update -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"id":1,"username":"guest","password":"","role":[1],"disabled":false,"permission":15,"base_path":"/","sso_id":""}'
```

**Key pitfalls:**
- `-v /:/host:ro` makes filesystem READ-ONLY — remove `:ro` for upload capability
- Guest user (id=1) has permission=0 by default — must enable manually
- Admin user is id=2, not id=1
- Role must be array `[2]` not number `2`
- API `/api/me/update-password` returns HTML (wrong endpoint) — use `/api/admin/user/update` instead

**API file operations:**
```bash
# Upload file
curl -s http://localhost:5244/api/fs/put -X PUT \
  -H "Authorization: $TOKEN" \
  -H "File-Path: /path/to/file.txt" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @local_file.txt

# List directory
curl -s http://localhost:5244/api/fs/list -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"path":"/","password":"","page":1,"per_page":50}'

# Create directory
curl -s http://localhost:5244/api/fs/mkdir -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"path":"/new_folder"}'
```

### Uptime Kuma — Monitoring
```bash
sudo docker pull louislam/uptime-kuma:1
sudo docker run -d --restart=always --name uptime-kuma \
  -p 3001:3001 -v uptime-kuma:/app/data louislam/uptime-kuma:1
```

### Memos — Note Taking
```bash
sudo docker pull neosmemo/memos:stable
sudo docker run -d --restart=always --name memos \
  -p 5230:5230 -v memos:/var/opt/memos neosmemo/memos:stable
```

### Vaultwarden — Password Manager
```bash
sudo docker pull vaultwarden/server:latest
sudo docker run -d --restart=always --name vaultwarden \
  -p 8080:80 -v vw-data:/data/ vaultwarden/server:latest
```
