---
name: github-pages-deploy
version: 1.0.0
description: Deploy static sites to GitHub Pages via API — create repo, push, enable Pages, all from CLI
tags: [github, pages, deploy, static-site, ci-cd, api]
triggers:
  - deploy to github pages
  - github pages setup
  - 部署GitHub Pages
  - 静态网站部署
  - 开源网站
---

# GitHub Pages 部署

## 前置条件
- GitHub账号 + Personal Access Token（repo权限）
- Token存在 `~/.hermes/.env` 的 `GITHUB_TOKEN=` 行

## 完整流程

### 1. 创建仓库（API方式，无需gh CLI）

```bash
TOKEN=$(python3 -c "
for line in open('$HOME/.hermes/.env'):
    if line.startswith('GITHUB_TOKEN='):
        print(line.split('=',1)[1].strip().strip('\"').strip(\"'\"))
        break
")

curl -s -X POST https://api.github.com/user/repos \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"repo-name","description":"描述","public":true}'
```

### 2. 推送代码

```bash
cd /path/to/project
git init
git add -A
git commit -m "init"
git branch -m master main
git remote add origin "https://USERNAME:${TOKEN}@github.com/USERNAME/repo-name.git"
git push -u origin main
```

### 3. 开启 GitHub Pages

```bash
curl -s -X POST "https://api.github.com/repos/USERNAME/repo-name/pages" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source":{"branch":"main","path":"/"}}'
```

网站地址：`https://USERNAME.github.io/repo-name/`

### 4. 后续更新

```bash
git add -A && git commit -m "update" && git push origin main
```

GitHub Actions自动重新部署（如果有 `.github/workflows/deploy.yml`）。

## Pitfalls

- **push rejected "repository rule violations"** — 大文件或敏感内容被GitHub拦截。删除大文件（.tar.gz, .zip, 图片）后重试
- **Pages未生效** — 需要几分钟，首次可能等5-10分钟
- **Token权限** — 需要 `repo` scope，fine-grained token需要 `Pages: Read and write` 权限
- **API返回空** — curl输出为空通常是Token格式问题，用python3读取.env而不是grep
- **gh CLI未安装** — 阿里云网络慢装不上，直接用curl调GitHub API即可

## 国内访问注意事项

- GitHub Pages国内访问偶尔不稳定
- 如果用户主要在国内，考虑用阿里云服务器托管，GitHub做备份
- Cloudflare Pages国内更不稳定，不推荐
