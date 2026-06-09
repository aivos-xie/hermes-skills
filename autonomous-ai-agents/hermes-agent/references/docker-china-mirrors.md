# Docker Installation in China (Alibaba Cloud ECS)

## Working Registry Mirrors (tested 2026-06)

Most Docker Hub mirrors in China are dead or unreliable. These actually worked:

```json
{
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://docker.m.daocloud.io",
    "https://docker.nju.edu.cn"
  ]
}
```

## Setup Steps

```bash
# 1. Install Docker from Alibaba mirror
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io --exclude=docker-ce-rootless-extras

# 2. Configure working mirrors
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://docker.m.daocloud.io",
    "https://docker.nju.edu.cn"
  ]
}
EOF

# 3. Restart and verify
sudo systemctl daemon-reload
sudo systemctl start docker
sudo systemctl enable docker
```

## Pitfalls

- `docker-ce-rootless-extras` often has checksum mismatch on Alibaba Cloud — exclude it
- `registry.cn-hangzhou.aliyuncs.com` only works for images explicitly pushed there, NOT as a general Docker Hub mirror
- `docker.mirrors.ustc.edu.cn` and `hub-mirror.c.163.com` are often unreliable
- `ghcr.io` (GitHub Container Registry) also often timeout from China

## QingLong Panel (青龙面板)

```bash
# Pull and run
sudo docker pull whyour/qinglong:latest
sudo docker run -dit \
  --name qinglong \
  --restart=always \
  -p 5700:5700 \
  -v /root/ql/data:/ql/data \
  whyour/qinglong:latest

# Check logs for setup info
sudo docker logs qinglong 2>&1 | tail -20
```

### API Access

Default login after setup:
```bash
# Login and get token
TOKEN=$(curl -s -X POST http://localhost:5700/api/user/login \
    -H "Content-Type: application/json" \
    -d '{"username":"YOUR_USER","password":"YOUR_PASS"}' | \
    python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# List tasks
curl -s http://localhost:5700/api/crons -H "Authorization: Bearer $TOKEN"

# Add environment variable (format is ARRAY)
curl -s -X POST http://localhost:5700/api/envs \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '[{"name":"VAR_NAME","value":"VAR_VALUE","remarks":"description"}]'

# Add cron task
curl -s -X POST http://localhost:5700/api/crons \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name":"Task Name","command":"task script.js","schedule":"30 8 * * *"}'
```

### Pitfalls

- API `/api/envs` expects **array format** `[{}]`, not plain object `{}`
- API `/api/crons` expects plain object `{}`
- Node.js deps need to be installed via the web UI (dependency management page) — pnpm/npm in container has store conflicts
- Scripts must be downloaded to `/ql/data/scripts/` before running
- Environment variables from the panel are NOT automatically injected into container env — scripts need to read them via the panel API or use `require` patterns
