# Docker on Chinese Cloud Servers

## Problem
Docker Hub (`registry-1.docker.io`) is unreachable from many Chinese cloud servers (Alibaba Cloud ECS, Tencent Cloud CVM, etc.) even with public IPs. Standard mirror registries often fail too.

## Working Mirror Registry (tested 2026-06)

```json
{
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://docker.m.daocloud.io",
    "https://docker.nju.edu.cn"
  ]
}
```

Write to `/etc/docker/daemon.json`, then `systemctl daemon-reload && systemctl restart docker`.

## Failed Mirrors (do NOT use)
- `docker.mirrors.ustc.edu.cn` — connection timeout
- `hub-mirror.c.163.com` — connection timeout
- `mirror.ccs.tencentyun.com` — connection timeout
- `registry.cn-hangzhou.aliyuncs.com` — works for Alibaba's own images only, not a general Docker Hub mirror
- `dockerhub.icu` — connection timeout

## Docker Installation on Alibaba Cloud Linux 3

```bash
# Add repo (use Alibaba mirror, not docker.com which is also blocked)
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

# Install (exclude broken rootless-extras package)
yum install -y docker-ce docker-ce-cli containerd.io --exclude=docker-ce-rootless-extras

# Enable and start
systemctl start docker
systemctl enable docker
```

**Pitfall:** `docker-ce-rootless-extras` has a checksum mismatch on Alibaba Cloud Linux mirrors. Exclude it with `--exclude=docker-ce-rootless-extras`.

## QingLong Panel (青龙面板) Deployment

```bash
# Pull image (after configuring mirrors above)
docker pull whyour/qinglong:latest

# Run
docker run -dit \
  --name qinglong \
  --restart=always \
  -p 5700:5700 \
  -v /root/ql/data:/ql/data \
  whyour/qinglong:latest
```

### API Management

```bash
# Login and get token
TOKEN=$(curl -s -X POST http://localhost:5700/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"YOUR_USER","password":"YOUR_PASS"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# Add cron task
curl -s -X POST http://localhost:5700/api/crons \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Task Name","command":"task script.js","schedule":"30 8 * * *}'

# Add environment variable (array format)
curl -s -X POST http://localhost:5700/api/envs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"name":"VAR_NAME","value":"var_value","remarks":"description"}]'

# List tasks
curl -s http://localhost:5700/api/crons \
  -H "Authorization: Bearer $TOKEN"

# List env vars
curl -s http://localhost:5700/api/envs \
  -H "Authorization: Bearer $TOKEN"
```

### API Pitfalls
- `POST /api/envs` requires **array format** `[{...}]`, not single object `{...}`
- `POST /api/crons` does NOT accept `isDisabled` field — omit it
- Dependencies should be installed via the web UI ("依赖管理"), not CLI — pnpm store conflicts are common in containers
- Web UI default port: 5700

### Common Dependencies for QQ Scripts
- **Node.js:** axios, crypto-js, cheerio, js-yaml, got, request, tough-cookie, tslib
- **Python3:** requests, urllib3, pyaes, rsa
