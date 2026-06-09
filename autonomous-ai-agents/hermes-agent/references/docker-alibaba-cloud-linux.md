# Docker Installation on Alibaba Cloud Linux 3

## Problem
Standard Docker CE installation from `download.docker.io` fails due to SSL connection errors (blocked). The `docker-ce-rootless-extras` package has checksum mismatches on Alibaba mirrors.

## Working Solution

```bash
# 1. Add Alibaba mirror repo
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

# 2. Install with broken package excluded
yum install -y docker-ce docker-ce-cli containerd.io --exclude=docker-ce-rootless-extras

# 3. Start Docker
systemctl start docker
systemctl enable docker
```

## Pitfalls
- **do NOT use** `https://download.docker.com/linux/centos/docker-ce.repo` — SSL blocked
- **do NOT include** `docker-ce-rootless-extras` — checksum mismatch on Alibaba mirrors
- After install, configure Chinese mirror registries before pulling images (see `docker-china-cloud.md`)
