---
name: self-hosted-apps
description: Deploy self-hosted applications via Docker — AList, monitoring, notes, dashboards. Covers deployment, configuration, API integration, and China-specific Docker mirror setup.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [self-hosted, docker, alist, monitoring, uptime-kuma, memos, deployment]
---

# Self-Hosted Application Deployment

## When to Use

- User asks to set up a file server, cloud storage, monitoring, dashboard, or note-taking app
- Deploying web applications on the server
- Need API access to manage files or services programmatically

## Pre-Deployment Checklist

1. **Docker mirrors MUST be configured first** — see `docker-alibaba-cloud` skill
2. Check available resources: `free -h && df -h /`
3. Check existing containers: `sudo docker ps`
4. Plan port allocation — avoid conflicts

## Deployment Pattern

```bash
# 1. Pull image (use background=true for large images)
sudo docker pull image:tag

# 2. Run container
sudo docker run -d --restart=always \
  --name appname \
  -p PORT:PORT \
  -v /path/to/data:/data \
  image:tag

# 3. Open firewall
sudo firewall-cmd --add-port=PORT/tcp --permanent
sudo firewall-cmd --reload

# 4. Get initial credentials
sudo docker logs appname 2>&1 | grep -i "password\|密码"

# 5. Remind user to open Alibaba Cloud security group port
```

## AList — File Server / Cloud Storage

Lightweight self-hosted file manager with API access. Perfect for file sharing between user and agent.

### Deploy
```bash
sudo docker run -d --restart=always --name alist \
  -p 5244:5244 \
  -v /opt/alist/data:/opt/alist/data \
  -v /:/host:ro \
  -e PUID=0 -e PGID=0 -e UMASK=022 \
  xhofe/alist:latest
```

### Initial Setup
```bash
# Get initial password
sudo docker logs alist 2>&1 | grep -i "password"

# Login and get token
TOKEN=$(curl -s http://localhost:5244/api/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"INITIAL_PASSWORD"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")
```

### Change Username/Password via API
```bash
# IMPORTANT: role must be array [2] for admin, not integer 2
curl -s http://localhost:5244/api/admin/user/update -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"id":2,"username":"newuser","password":"newpass","role":[2],"disabled":false,"permission":65535,"base_path":"/","sso_id":""}'
```

**Pitfall:** AList API `role` field MUST be array `[2]`, not integer `2`. Error: "decode slice: expect [ or n, but found 2"

**Pitfall:** User ID may be 2, not 1. Always check `/api/me` first to get the actual user ID.

**Pitfall:** `/api/me/update-password` returns HTML page (not JSON) in some AList versions. Use `/api/admin/user/update` instead.

### Configure Storage
```bash
# Update storage to point to host root
curl -s http://localhost:5244/api/admin/storage/update -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{
    "id": 1,
    "mount_path": "/",
    "order": 0,
    "driver": "Local",
    "cache_expiration": 30,
    "status": "work",
    "addition": "{\"root_folder_path\":\"/host\",\"thumbnail\":false,\"use_ffmpeg\":false,\"thumb_cache_folder\":\"\",\"thumb_concurrency\":\"\",\"thumb_pixel\":\"\",\"video_thumb_pos\":\"20%\",\"show_hidden\":true,\"mkdir_perm\":\"777\",\"recycle_bin_path\":\"delete permanently\"}"
  }'
```

**Pitfall:** If mounting host root `/`, use `-v /:/host:ro` in Docker and set `root_folder_path` to `/host`. Container's own `/` is the container filesystem, not the host.

**Pitfall:** To add a storage, use `update` on existing ID, not `create` — UNIQUE constraint on `mount_path` prevents duplicates.

### File Operations API
```bash
# List files
curl -s "http://localhost:5244/api/fs/list" -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"path":"/some/path","password":"","page":1,"per_page":50}'

# Upload file
curl -T localfile.txt "http://localhost:5244/dav/remote/path/file.txt" \
  -H "Authorization: $TOKEN"

# Create folder
curl -s http://localhost:5244/api/fs/mkdir -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"path":"/some/new/folder"}'
```

## Uptime Kuma — Monitoring

```bash
sudo docker run -d --restart=always --name uptime-kuma \
  -p 3001:3001 -v uptime-kuma:/app/data louislam/uptime-kuma:1
```

## Memos — Note-Taking

```bash
sudo docker run -d --restart=always --name memos \
  -p 5230:5230 -v memos:/var/opt/memos neosmemo/memos:stable
```

## Pitfalls

1. **Always configure Docker mirrors first** — without mirrors, pulls timeout in China
2. **Use background=true for docker pull** — don't block the conversation
3. **AList role is array not int** — `[2]` not `2`
4. **AList user ID may not be 1** — check `/api/me` first
5. **Host root mount needs `/host` mapping** — `-v /:/host:ro` + `root_folder_path: /host`
6. **Alibaba Cloud security group** — remind user to open ports after deployment
7. **Don't over-deploy on small servers** — 2 cores 1.8GB RAM can handle 3-4 lightweight apps max
8. **AList Docker auto-restarts** — `xhofe/alist:latest` container has a restart policy. If you replace AList with a custom app (e.g. Flask disk on port 5244), `kill` won't work — the Docker daemon restarts it. Must use `sudo docker stop alist` (or `sudo docker rm -f alist`) to permanently free the port. Check with `sudo docker ps | grep alist` before starting a replacement service.
