---
name: self-hosted-services
description: 自托管服务部署 — AList网盘、Uptime Kuma监控、Memos笔记等轻量Docker服务
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [self-hosted, docker, alist, uptime-kuma, memos, file-sharing, monitoring]
---

# 自托管服务部署

## 部署前必做：Docker镜像源

**在中国大陆服务器上，必须先配置镜像源再拉取镜像，否则极慢。**

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

**Pitfall:** 不配镜像源直接pull，一个100MB的镜像可能要10分钟+。

---

## AList — 文件管理/网盘

### 部署
```bash
sudo docker run -d \
  --restart=always \
  --name alist \
  -p 5244:5244 \
  -v /opt/alist/data:/opt/alist/data \
  xhofe/alist:latest
```

### 获取初始密码
```bash
sudo docker logs alist 2>&1 | grep -i "password"
```

### 停止/管理Docker容器

⚠️ **AList用 `--restart=always` 部署，`kill`进程无效，Docker会自动重启。**

```bash
sudo docker stop alist      # 停止
sudo docker start alist     # 启动
sudo docker restart alist   # 重启
```

**Pitfall:** `ps aux | grep alist` 能看到进程，但 `sudo kill -9 <pid>` 会被Docker立刻重启。必须用 `docker stop`。

### 与自定义网盘共存

当前服务器同时有AList(Docker)和自定义Flask网盘"aivos的网盘"，**都用端口5244**，互斥运行：
- AList: `sudo docker start/stop alist`
- Flask网盘: `cd /opt/aivos-disk && /home/admin/.hermes/hermes-agent/venv/bin/python app.py`（background模式启动）
- Flask网盘秘钥: 699613，存储: `/opt/aivos-disk/storage/`

切换时先停一个再启另一个。

### 修改用户名和密码（通过API）
```bash
# 1. 用初始密码登录获取token
TOKEN=$(curl -s http://localhost:5244/api/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"初始密码"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# 2. 修改用户名和密码
# 注意：role必须是数组 [2]，不是数字 2
curl -s http://localhost:5244/api/admin/user/update -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"id":2,"username":"新用户名","password":"新密码","role":[2],"disabled":false,"permission":65535,"base_path":"/","sso_id":""}'
```

### 添加本地存储（根目录）

⚠️ **重要**：存储路径必须在Docker挂载点 `/opt/alist/data` 内，否则会报 "storage not found" 错误。

```bash
# 创建存储目录（必须在Docker挂载点内）
sudo mkdir -p /opt/alist/data/storage
sudo chmod 777 /opt/alist/data/storage

TOKEN=...
curl -s http://localhost:5244/api/admin/storage/create -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{
    "mount_path": "/",
    "order": 0,
    "driver": "Local",
    "cache_expiration": 30,
    "status": "work",
    "addition": "{\"root_folder_path\":\"/opt/alist/data/storage\",\"thumbnail\":false,\"show_hidden\":true,\"mkdir_perm\":\"777\",\"recycle_bin_path\":\"delete permanently\"}"
  }'
```

### 禁用访客/匿名访问
```bash
# 禁用guest用户
curl -s http://localhost:5244/api/admin/user/update -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"id":1,"username":"guest","password":"","role":[1],"disabled":true,"permission":0,"base_path":"/","sso_id":""}'
```

### 测试匿名访问是否被拒
```bash
curl -s "http://localhost:5244/api/fs/list" -X POST \
  -H "Content-Type: application/json" \
  -d '{"path":"/","password":"","page":1,"per_page":5}'
# 应返回 {"code":401,"message":"Guest user is disabled, login please"}
```

### 修复存储路径问题

如果更新用户后文件消失，检查并修复存储配置：

```bash
# 检查当前存储配置
sqlite3 /opt/alist/data/data.db "SELECT id, addition FROM x_storages;"

# 如果root_folder_path错误，更新它
sqlite3 /opt/alist/data/data.db "UPDATE x_storages SET addition='{\"root_folder_path\":\"/opt/alist/data/storage\",\"thumbnail\":false,\"thumb_cache_folder\":\"\",\"show_hidden\":true,\"mkdir_perm\":\"777\",\"recycle_bin_path\":\"delete permanently\"}' WHERE id=1;"

# 重启容器
sudo docker restart alist
```

---

## Pitfalls

1. **Docker镜像源必须先配** — 在中国大陆不配镜像源pull极慢
2. **挂载宿主机根目录不要加:ro** — `:ro`是只读，用户无法上传/创建文件夹
3. **AList密码在数据库中显示为空** — AList使用WAL模式，密码存储在WAL文件中，直接sqlite3查询看不到，但认证正常工作
4. **API更新用户role必须是数组** — `"role":[2]` 不是 `"role":2`，否则报错
5. **alist admin set在Docker中不接受管道输入** — 用API改密码更可靠
6. **网页上传按钮需要进入文件夹后才出现** — 不是在主页直接上传
7. **修改数据库需要停止容器** — WAL模式下运行时sqlite3写入会失败
8. **AList v3 API路径** — `/api/auth/login`(登录), `/api/admin/user/update`(更新用户), `/api/admin/storage/create`(创建存储), `/api/fs/list`(列出文件)
9. **⚠️ 存储路径必须在Docker挂载点内** — Docker只挂载 `/opt/alist/data`，所以存储路径必须是 `/opt/alist/data/storage`，不能是 `/opt/alist/storage`。否则报 "storage not found" 错误
10. **更新用户后存储可能丢失** — 通过API更新用户信息后，要验证存储配置是否正常。如果文件消失，检查 `x_storages` 表的 `root_folder_path` 是否正确
11. **`--restart=always` 容器不能靠kill停止** — 必须用 `docker stop`，直接kill进程会被Docker立刻重启。排查端口占用时先 `docker ps` 看容器
