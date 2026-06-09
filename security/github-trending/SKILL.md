---
name: github-trending
description: GitHub热门项目 — AI Agent框架、自托管工具、开发者工具 (2026年6月)
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, trending, self-hosted, ai-agents, devtools, productivity]
---

# GitHub 热门项目速查 (2026年6月)

## 🏆 星数排行 TOP 20

| 排名 | 项目 | 星数 | 类别 | 简介 |
|------|------|------|------|------|
| 1 | n8n | 191K | 自动化 | 自托管Zapier，400+集成，AI工作流 |
| 2 | Ollama | 174K | AI | 本地运行LLM，一键部署 |
| 3 | Open WebUI | 141K | AI | ChatGPT式前端，支持100+后端 |
| 4 | LangChain | 139K | AI框架 | Agent工程平台 |
| 5 | Claude Code | 131K | AI编码 | Anthropic终端编码Agent |
| 6 | Immich | 103K | 照片 | 自托管Google Photos替代 |
| 7 | Browser Use | 98K | AI工具 | 让AI操控浏览器 |
| 8 | OpenAI Codex | 90K | AI编码 | OpenAI终端编码Agent |
| 9 | Uptime Kuma | 88K | 监控 | 美观的自托管监控 |
| 10 | Stirling-PDF | 80K | PDF | 自托管PDF工具箱 |
| 11 | OpenHands | 76K | AI编码 | AI软件开发Agent |
| 12 | AppFlowy | 72K | 笔记 | 开源Notion替代 |
| 13 | DeerFlow | 71K | AI研究 | 字节跳动超级Agent |
| 14 | Traefik | 64K | 反向代理 | 云原生反向代理 |
| 15 | Vaultwarden | 62K | 密码管理 | 轻量Bitwarden服务端 |
| 16 | Memos | 61K | 笔记 | 轻量自托管笔记 |
| 17 | AutoGen | 59K | AI框架 | 微软多Agent框架 |
| 18 | Pi-hole | 59K | DNS | 网络广告拦截 |
| 19 | CrewAI | 53K | AI框架 | 角色扮演Agent编排 |
| 20 | Jellyfin | 53K | 媒体 | 开源媒体服务器 |

---

## 🤖 AI Agent 框架

### 终端编码Agent (2025年爆发)
```bash
# Claude Code ⭐131K
npm install -g @anthropic-ai/claude-code
claude

# OpenAI Codex ⭐90K
npm install -g @openai/codex
codex "explain this codebase"

# OpenHands ⭐76K
docker run -it --pull=always -p 3000:3000 \
  -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.29-nikolaik \
  -v /var/run/docker.sock:/var/run/docker.sock \
  docker.all-hands.dev/all-hands-ai/openhands:0.29
```

### Agent框架
```bash
# LangChain ⭐139K
pip install langchain langchain-openai

# OpenAI Agents SDK ⭐27K (2025新)
pip install openai-agents

# CrewAI ⭐53K
pip install crewai

# AutoGen ⭐59K (微软)
pip install autogen

# VoltAgent ⭐9.5K (TypeScript)
npm create voltagent@latest
```

### MCP 生态 (2025爆发)
```bash
# Playwright MCP ⭐33.6K
npx @playwright/mcp@latest

# GitHub MCP Server ⭐30.5K
docker run -e GITHUB_PERSONAL_ACCESS_TOKEN=<token> ghcr.io/github/github-mcp-server
```

### 其他AI工具
```bash
# Browser Use ⭐98K — AI操控浏览器
pip install browser-use

# Composio ⭐28.7K — 1000+工具集成
pip install composio

# E2B ⭐12.5K — AI安全沙箱
pip install e2b

# DeerFlow ⭐71K — 字节跳动超级Agent
git clone https://github.com/bytedance/deer-flow.git
```

---

## 🏠 自托管工具

### 监控
```bash
# Uptime Kuma ⭐88K
docker run -d --restart=always -p 3001:3001 \
  -v uptime-kuma:/app/data --name uptime-kuma louislam/uptime-kuma:1

# Homepage ⭐31K
docker run -d -p 3000:3000 \
  -v /path/to/config:/app/config \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  ghcr.io/gethomepage/homepage:latest

# Portainer ⭐38K
docker run -d -p 9443:9443 --name portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data portainer/portainer-ce:latest
```

### AI
```bash
# Open WebUI ⭐141K
docker run -d -p 3000:8080 -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main

# Ollama ⭐174K
docker run -d -v ollama:/root/.ollama -p 11434:11434 \
  --name ollama ollama/ollama
```

### 照片
```bash
# Immich ⭐103K — Google Photos替代
# 需要docker-compose: https://immich.app/docs/install/docker-compose
```

### 笔记
```bash
# Memos ⭐61K — 微日记
docker run -d --name memos -p 5230:5230 \
  -v /path/to/memos:/var/opt/memos neosmemo/memos:stable

# AppFlowy ⭐72K — Notion替代
docker run -d -p 8080:80 \
  -v /path/to/data:/data appflowyinc/appflowy-web:latest

# SiYuan ⭐44K — 思源笔记
docker run -d -p 6806:6806 \
  -v /path/to/data:/siyuan/workspace b3log/siyuan:latest
```

### 密码管理
```bash
# Vaultwarden ⭐62K
docker run -d --name vaultwarden \
  -v /vw-data/:/data/ -p 80:80 vaultwarden/server:latest

# Authelia ⭐28K — SSO/MFA
docker run -d -p 9091:9091 \
  -v /path/to/config:/config authelia/authelia:latest
```

### 文件/媒体
```bash
# Filebrowser ⭐35K
docker run -d -p 8080:80 \
  -v /your/data:/srv filebrowser/filebrowser

# Stirling-PDF ⭐80K
docker run -d -p 8080:8080 frooodle/s-pdf:latest

# Jellyfin ⭐53K
docker run -d -p 8096:8096 \
  -v /path/to/config:/config \
  -v /path/to/media:/media jellyfin/jellyfin:latest

# Nextcloud ⭐36K
docker run -d -p 8080:80 -v nextcloud:/var/www/html nextcloud:latest
```

### 自动化
```bash
# n8n ⭐192K
docker run -d -p 5678:5678 -v n8n_data:/home/node/.n8n \
  -e GENERIC_TIMEZONE="Asia/Shanghai" n8nio/n8n

# Activepieces ⭐23K
docker run -d -p 8080:80 \
  -v activepieces:/root/.activepieces activepieces/activepieces:latest
```

### DNS/广告拦截
```bash
# AdGuard Home ⭐35K
docker run -d -p 53:53/tcp -p 53:53/udp -p 3000:3000 \
  -v /path/to/work:/opt/adguardhome/work \
  -v /path/to/conf:/opt/adguardhome/conf adguard/adguardhome

# Pi-hole ⭐59K
docker run -d -p 53:53/tcp -p 53:53/udp -p 80:80 \
  -v /path/to/etc-pihole:/etc/pihole pihole/pihole:latest
```

### 反向代理
```bash
# Nginx Proxy Manager ⭐33K
docker run -d -p 80:80 -p 443:443 -p 81:81 \
  -v /path/to/data:/data \
  -v /path/to/letsencrypt:/etc/letsencrypt \
  jc21/nginx-proxy-manager:latest

# Traefik ⭐64K
docker run -d -p 80:80 -p 443:443 \
  -v /var/run/docker.sock:/var/run/docker.sock traefik:v3.0
```

### 其他
```bash
# Maybe Finance ⭐54K — 个人财务
docker run -d -p 3000:3000 \
  -v /path/to/data:/rails/storage ghcr.io/maybe-finance/maybe:latest
```

---

## 📊 2026年趋势

1. **终端编码Agent爆发** — Claude Code、OpenAI Codex、OpenHands
2. **MCP协议成为标准** — Playwright MCP、GitHub MCP Server
3. **自托管AI需求暴涨** — Ollama、Open WebUI
4. **Agent框架竞争激烈** — LangChain vs OpenAI Agents vs CrewAI vs AutoGen
5. **n8n成为自动化之王** — 192K星，AI原生工作流
6. **Immich成为照片管理首选** — 103K星，Google Photos替代

---

## Pitfalls

1. **Docker镜像拉取可能很慢** — 国内需要配置镜像源
2. **Ollama需要GPU** — CPU也能跑但很慢
3. **n8n需要足够内存** — 复杂工作流吃内存
4. **Immich需要多容器** — 不是单docker run能搞定的
5. **Vaultwarden不是官方Bitwarden** — 功能有差异但够用
6. **Pi-hole可能影响正常DNS** — 配置不当会屏蔽正常网站
7. **Traefik学习曲线陡** — 比Nginx Proxy Manager复杂
