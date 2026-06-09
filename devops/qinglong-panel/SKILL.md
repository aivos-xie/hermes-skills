---
name: qinglong-panel
description: "青龙面板完全指南：部署、脚本编写、API使用、抓包、自动化签到。"
version: 2.0.0
author: Hermes
metadata:
  hermes:
    tags: [automation, qinglong, cron, scripts, checkin, packet-capture]
---

# 青龙面板完全指南

## 一、简介

青龙面板（QingLong Panel）是一个支持 Python3、JavaScript、Shell、Typescript 的定时任务管理平台。

- **GitHub**: https://github.com/whyour/qinglong
- **文档**: https://qinglong.online
- **Stars**: 19.6k
- **支持语言**: Python3, JavaScript, Shell, TypeScript

## 二、功能特性

- ✅ 多脚本语言支持（Python/JS/Shell/TS）
- ✅ 在线管理脚本、环境变量、配置文件
- ✅ 在线查看任务日志
- ✅ 秒级任务设置
- ✅ 系统级通知
- ✅ 暗黑模式
- ✅ 手机端操作
- ✅ 内置 API（JavaScript 全局变量 `QLAPI`）

## 三、部署方式

### 3.1 Docker 部署（推荐）

```bash
# Alpine 镜像（默认）
docker pull whyour/qinglong:latest

# Debian 镜像（需要 Alpine 不支持的依赖时使用）
docker pull whyour/qinglong:debian

# 运行容器
docker run -d \
  -v /path/to/ql/data:/ql/data \
  -p 5700:5700 \
  --name qinglong \
  whyour/qinglong:latest

# 非 root 用户运行（必须用 debian 镜像）
docker run -d \
  -v /path/to/ql/data:/ql/data \
  -p 5700:5700 \
  --user qinglong \
  --name qinglong \
  whyour/qinglong:debian
```

### 3.2 Docker Compose 部署

```yaml
version: '3'
services:
  qinglong:
    image: whyour/qinglong:latest
    container_name: qinglong
    restart: unless-stopped
    ports:
      - "5700:5700"
    volumes:
      - ./data:/ql/data
    environment:
      - QlPort=5700
```

### 3.3 宝塔面板部署

1. 安装宝塔面板
2. 安装 Docker 管理器
3. 搜索 `whyour/qinglong` 镜像
4. 创建容器，映射端口 5700

### 3.4 1Panel 部署

1. 安装 1Panel
2. 应用商店搜索「青龙」
3. 一键部署

### 3.5 npm 部署

```bash
# 需要先安装 node/npm/python3/pip3/pnpm
npm i @whyour/qinglong
```

## 四、目录结构

```
/ql/data/
├── config/           # 配置文件
│   ├── config.sh     # 主配置
│   ├── auth.json     # 认证信息
│   └── extra.sh      # 额外配置
├── db/               # 数据库
├── log/              # 日志
├── repo/             # 脚本仓库
├── scripts/          # 自定义脚本
├── store/            # 存储
└── raw/              # 原始脚本
```

## 五、脚本编写规范

### 5.1 JavaScript 脚本模板

```javascript
/**
 * 脚本名称: 示例签到脚本
 * 脚本作者: YourName
 * 更新日期: 2026-06-09
 * 使用方法: 在环境变量中添加 Cookie
 * 依赖: axios
 */

const axios = require('axios');

// 从环境变量获取 Cookie
const COOKIE = process.env.COOKIE_NAME;

if (!COOKIE) {
    console.log('请先添加环境变量 COOKIE_NAME');
    process.exit(1);
}

// 通用请求头
const headers = {
    'Cookie': COOKIE,
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36'
};

// 签到函数
async function signIn() {
    try {
        const response = await axios.post('https://api.example.com/signin', {}, {
            headers: headers
        });

        if (response.data.code === 0) {
            console.log(`签到成功！获得 ${response.data.points} 积分`);
        } else {
            console.log(`签到失败: ${response.data.message}`);
        }
    } catch (error) {
        console.log(`请求出错: ${error.message}`);
    }
}

// 执行签到
signIn();
```

### 5.2 Python 脚本模板

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本名称: 示例签到脚本
脚本作者: YourName
更新日期: 2026-06-09
使用方法: 在环境变量中添加 Cookie
依赖: requests
"""

import os
import sys
import requests
import time
import random

# 从环境变量获取 Cookie
COOKIE = os.environ.get('COOKIE_NAME')

if not COOKIE:
    print('请先添加环境变量 COOKIE_NAME')
    sys.exit(1)

# 通用请求头
headers = {
    'Cookie': COOKIE,
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36'
}

def sign_in():
    """签到函数"""
    try:
        response = requests.post(
            'https://api.example.com/signin',
            headers=headers,
            timeout=30
        )

        data = response.json()

        if data['code'] == 0:
            print(f"签到成功！获得 {data['points']} 积分")
        else:
            print(f"签到失败: {data['message']}")

    except Exception as e:
        print(f"请求出错: {str(e)}")

if __name__ == '__main__':
    sign_in()
```

### 5.3 Shell 脚本模板

```bash
#!/bin/bash
# 脚本名称: 示例签到脚本
# 脚本作者: YourName
# 更新日期: 2026-06-09
# 使用方法: 在环境变量中添加 Token

# 从环境变量获取 Token
TOKEN="${COOKIE_NAME}"

if [ -z "$TOKEN" ]; then
    echo "请先添加环境变量 COOKIE_NAME"
    exit 1
fi

# 签到函数
sign_in() {
    response=$(curl -s -X POST \
        -H "Cookie: $TOKEN" \
        -H "User-Agent: Mozilla/5.0 (Linux; Android 12)" \
        "https://api.example.com/signin")

    code=$(echo $response | jq -r '.code')

    if [ "$code" = "0" ]; then
        points=$(echo $response | jq -r '.points')
        echo "签到成功！获得 $points 积分"
    else
        message=$(echo $response | jq -r '.message')
        echo "签到失败: $message"
    fi
}

# 执行签到
sign_in
```

## 六、内置 API（QLAPI）

青龙面板提供 JavaScript 全局变量 `QLAPI`，可在脚本中直接调用。

### 6.1 环境变量管理

```javascript
// 获取环境变量列表
const envs = await QLAPI.getEnvs({ searchValue: 'keyword' });

// 创建环境变量
await QLAPI.createEnv({
    envs: [
        { name: 'VAR_NAME', value: 'var_value' }
    ]
});

// 更新环境变量
await QLAPI.updateEnv({
    env: { id: 1, name: 'VAR_NAME', value: 'new_value' }
});

// 删除环境变量
await QLAPI.deleteEnvs({ ids: [1, 2, 3] });

// 禁用环境变量
await QLAPI.disableEnvs({ ids: [1, 2, 3] });

// 启用环境变量
await QLAPI.enableEnvs({ ids: [1, 2, 3] });

// 移动环境变量位置
await QLAPI.moveEnv({ id: 1, fromIndex: 0, toIndex: 1 });
```

### 6.2 通知管理

```javascript
// 发送通知
await QLAPI.sendNotify('标题', '内容');
```

## 七、定时任务语法

青龙面板支持标准 cron 表达式：

```
┌───────────── 秒 (0-59)
│ ┌───────────── 分 (0-59)
│ │ ┌───────────── 时 (0-23)
│ │ │ ┌───────────── 日 (1-31)
│ │ │ │ ┌───────────── 月 (1-12)
│ │ │ │ │ ┌───────────── 周 (0-7, 0和7都是周日)
│ │ │ │ │ │
* * * * * *
```

### 常用示例

```
0 0 0 * * *        # 每天 0 点执行
0 30 8 * * *       # 每天 8:30 执行
0 0 */2 * * *      # 每 2 小时执行
0 0 0 * * 1        # 每周一 0 点执行
0 0 0 1 * *        # 每月 1 号 0 点执行
*/5 * * * * *      # 每 5 秒执行
0 0 9-18 * * 1-5   # 工作日 9-18 点每小时执行
```

## 八、环境变量管理

### 8.1 环境变量格式

```
变量名=变量值
```

### 8.2 多账号支持

用 `&` 分隔多个值：

```
COOKIE_NAME=cookie1&cookie2&cookie3
```

### 8.3 常用环境变量

| 变量名 | 说明 |
|--------|------|
| `JD_COOKIE` | 京东 Cookie |
| `PT_KEY` | 京东 PT_KEY |
| `PT_PIN` | 京东 PT_PIN |
| `TG_BOT_TOKEN` | Telegram Bot Token |
| `TG_USER_ID` | Telegram 用户 ID |
| `PUSH_KEY` | Server酱 SendKey |
| `BARK_PUSH` | Bark 推送地址 |

## 九、通知配置

### 9.1 支持的通知方式

- Telegram Bot
- 钉钉机器人
- 企业微信机器人
- Server酱
- Bark
- PushPlus
- iGot

### 9.2 配置方法

在「配置文件」中添加：

```bash
# Telegram 通知
export TG_BOT_TOKEN="your_bot_token"
export TG_USER_ID="your_user_id"

# 钉钉通知
export DD_BOT_TOKEN="your_bot_token"
export DD_BOT_SECRET="your_bot_secret"

# 企业微信通知
export QYWX_KEY="your_key"

# Server酱通知
export PUSH_KEY="your_sendkey"
```

## 十、常用脚本仓库

### 10.1 京东类

```bash
# 拉取仓库
ql repo https://github.com/user/repo.git "jd_|jx_" "" "scripts"

# 参数说明
# 第1个参数: 仓库地址
# 第2个参数: 包含的脚本文件名（用 | 分隔）
# 第3个参数: 排除的脚本文件名
# 第4个参数: 脚本目录
```

### 10.2 签到类

```bash
# 拉取签到脚本
ql repo https://github.com/user/checkin.git "checkin|sign" "" "src"
```

## 十一、常见问题

### 11.1 脚本依赖安装

```bash
# Node.js 依赖
npm install axios crypto-js

# Python 依赖
pip install requests
```

### 11.2 脚本不执行

1. 检查 cron 表达式是否正确
2. 检查环境变量是否配置
3. 查看日志排查错误
4. 检查脚本权限

### 11.3 通知不生效

1. 检查通知环境变量是否正确
2. 手动测试通知功能
3. 查看通知日志

## 十二、高级功能

### 12.1 脚本依赖管理

在「依赖管理」中添加：

- Node.js: `axios`, `crypto-js`, `got`
- Python: `requests`, `pycryptodome`

### 12.2 配置文件编辑

在「配置文件」中编辑 `config.sh`：

```bash
# 设置代理
export ProxyUrl="http://proxy:port"

# 设置超时
export MaxTimeout=30000

# 设置通知方式
export NotifyMode="all"  # all=所有通知, go=只用GOTR, ...
```

### 12.3 日志管理

- 日志路径: `/ql/data/log/`
- 自动清理: 在配置中设置日志保留天数

## 十三、抓包技术

### 13.1 mitmproxy 抓包

```bash
# 安装
pip install mitmproxy

# 启动代理
mitmdump --set block_global=false -p 8888 -w capture.flow

# 手机设置代理
# 设置 → WiFi → 代理 → 手动
# 服务器：电脑 IP，端口：8888

# 安装证书
# 手机浏览器访问 http://mitm.it

# 解析 Cookie
python3 -c "
from mitmproxy.io import FlowReader
with open('capture.flow', 'rb') as f:
    for flow in FlowReader(f).stream():
        if 'api' in flow.request.pretty_url:
            print(flow.request.headers.get('cookie'))
"
```

### 13.2 Fiddler 抓包

1. 下载安装 Fiddler
2. 配置 HTTPS 解密
3. 设置手机代理
4. 安装 Fiddler 证书
5. 操作 App，抓取请求

### 13.3 Charles 抓包

1. 下载安装 Charles
2. 代理设置 → SSL 代理
3. 添加需要抓取的域名
4. 手机设置代理
5. 安装 Charles 证书

### 13.4 ADB 抓包（无需代理）

```bash
# 连接手机
adb devices

# 查看 App 数据
adb shell run-as com.xxx.app cat /data/data/com.xxx.app/shared_prefs/*.xml

# 抓取网络请求
adb logcat | grep -i "cookie\|token\|authorization"
```

## 十四、最佳实践

1. **脚本命名规范**: `项目名_功能_作者.js`
2. **环境变量命名**: 大写+下划线，如 `JD_COOKIE`
3. **错误处理**: 必须有 try-catch 和错误提示
4. **通知集成**: 成功/失败都发送通知
5. **定时任务**: 避免整点执行，分散压力

## 十五、参考资源

- [官方文档](https://qinglong.online)
- [GitHub 仓库](https://github.com/whyour/qinglong)
- [Telegram 频道](https://t.me/jiao_long)
- [演示站点](http://demo.qinglong.online:4433/)
- `references/packet-capture-techniques.md` — 抓包技术详解（mitmproxy/Fiddler/Charles/ADB/Playwright）
