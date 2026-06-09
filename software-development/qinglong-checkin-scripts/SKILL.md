---
name: qinglong-checkin-scripts
description: "青龙面板签到脚本开发 — 逆向APP API、多账号、通知推送、售卖打包"
version: 1.0.0
author: aivos
metadata:
  hermes:
    tags: [qinglong, checkin, automation, scripts, monetization]
---

# 青龙面板签到脚本开发

## 概述

为青龙面板编写自动签到脚本，支持多平台APP的每日签到、金币领取、阅读时长上报等功能。脚本可打包售卖变现。

## 开发流程

### 1. API逆向（抓包）

签到脚本的核心是找到APP的签到API接口。

**抓包工具：**
- **ProxyPin** ⭐13K — 全平台开源免费，最推荐（Android/iOS/Windows/Mac）
  - GitHub: https://github.com/wanghongenpin/proxypin
  - 服务器已有APK: /opt/aivos-disk/storage/ProxyPin.apk (v1.2.8)
- **PCAPdroid** ⭐4K — Android免Root网络监控+抓包
  - GitHub: https://github.com/emanuele-f/PCAPdroid
- **HttpCanary** — Android免root，老牌工具
- **Reqable** ⭐6K — 跨平台HTTP调试，类似Charles
  - GitHub: https://github.com/reqable/reqable-app
- **mitmproxy** ⭐43K — 命令行，脚本化，适合自动化

**抓包步骤：**
1. 启动抓包工具
2. 打开目标APP，手动执行签到
3. 找到签到请求（通常包含 sign/checkin/daily 等关键词）
4. 记录：URL、请求方法、Headers、Cookie、Body
5. 分析参数哪些是固定的、哪些是动态的

**常见签到API模式：**
- `POST /api/sign/in` — 简单签到
- `POST /api/mission/sign_in` — 任务式签到
- `POST /api/v1/user_sign` — 用户签到（番茄小说）
- `GET /api/checkin` — GET方式签到

### 2. Cookie/Token获取

**环境变量命名规范：**
```
平台名_COOKIE     — 主要认证信息
平台名_TOKEN      — Bearer token
平台名_DEVICE_ID  — 设备标识
```

**多账号分隔符：** `&` （与号）

**青龙面板设置：**
```
环境变量 -> 新建
名称: FQ_COOKIE
值: install_id=xxx;passport_csrf_token=xxx
```

### 3. 脚本结构模板

```python
#!/usr/bin/env python3
"""
平台名自动签到脚本
环境变量: XX_COOKIE (必填), XX_NOTIFY (可选)
"""

import os, sys, json, time, random, requests
from datetime import datetime

# ========== 配置 ==========
API_BASE = "https://api.example.com"
COOKIES = os.environ.get("XX_COOKIE", "")
HEADERS = {"User-Agent": "APP_NAME/version (Android)"}

# ========== 核心逻辑 ==========
class Checkin:
    def __init__(self, cookie):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.cookie = cookie

    def sign_in(self):
        """签到"""
        resp = self.session.post(f"{API_BASE}/sign/in",
            cookies=self._parse_cookie(self.cookie))
        return resp.json()

    def run(self):
        """执行流程"""
        result = self.sign_in()
        return result

# ========== 多账号 ==========
def get_accounts():
    cookies = COOKIES
    if not cookies:
        print("❌ 未设置环境变量")
        sys.exit(1)
    return [c.strip() for c in cookies.split("&") if c.strip()]

# ========== 主入口 ==========
if __name__ == "__main__":
    accounts = get_accounts()
    for i, cookie in enumerate(accounts):
        checker = Checkin(cookie)
        checker.run()
```

### 4. 通知推送

**支持的通知方式：**
- Server酱: `https://sctapi.ftqq.com/{key}.send`
- Telegram: `https://api.telegram.org/bot{token}/sendMessage`
- 企业微信机器人: Webhook URL
- Pushplus: `http://www.pushplus.plus/send`
- 钉钉机器人: Webhook URL

**环境变量：**
```
XX_NOTIFY=tg / server / wx / pushplus / dingtalk
TG_BOT_TOKEN=xxx
TG_CHAT_ID=xxx
XX_SERVER_KEY=xxx
```

### 5. 反检测技巧

1. **分段上报** — 阅读时长分成3-6次上报，模拟真实行为
2. **随机延迟** — 每次请求间隔1-5秒随机
3. **真实UA** — 使用APP的真实User-Agent，不要用浏览器UA
4. **设备指纹** — 保持device_id一致，不要每次随机生成
5. **IP要求** — 住宅IP安全，VPS IP可能被风控
6. **频率控制** — 每天执行1-2次，不要过于频繁

### 6. 打包售卖

**文件结构：**
```
番茄小说签到脚本v2.0/
├── fanqie_checkin.py      # 主脚本
├── README.txt              # 使用教程
├── Cookie获取教程.docx     # 抓包教程
└── 常见问题FAQ.txt         # 售后文档
```

**定价建议：**
- 单个脚本: 9.9元
- 3个打包: 29.9元
- 全套(10+): 49.9元
- 附带教程+售后: 加价到99元

**销售渠道：**
- 闲鱼（搜索"青龙面板脚本"参考同行）
- 淘宝（虚拟商品店）
- QQ群（青龙面板交流群）
- 微信朋友圈

**售卖话术要点：**
- "一键部署，自动运行"
- "支持多账号"
- "附带详细教程"
- "永久更新"

## API参考

- `references/fanqie-api.md` — 番茄小说APP API详情（域名、接口、参数、Cookie获取）

## 已完成的脚本

| 脚本 | 路径 | 状态 |
|------|------|------|
| 番茄小说签到 | ~/fanqie_checkin.py | ✅ 完成(需APP Cookie) |
| 库街区/鸣潮签到 | 青龙面板脚本 | 🔄 Token获取服务就绪(端口5701) |

## Token获取服务（库街区）

库街区签到需要APP Token，但网页版不支持登录（只能APP登录），且GeeTest验证码阻止服务端自动获取。

**正确方案: mitmproxy MITM代理** — 用mitmproxy做HTTPS中间人代理，拦截APP登录请求，自动提取Token存入青龙。

⚠️ **已验证失败的方案**: 反向代理kurobbs.com网页版 → SPA资源加载问题 + 网页版无登录入口，从原理上不可行。

**mitmproxy搭建:**
```bash
# 安装（阿里云PyPI超时，用镜像）
uv venv /tmp/mitm-env --python python3.11
uv pip install --python /tmp/mitm-env/bin/python mitmproxy \
  -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 启动
/tmp/mitm-env/bin/mitmdump -p 5701 --set upstream_cert=false -s /tmp/kuro_capture.py --set block_global=false
```

**手机操作:** 安装CA证书(.cer) → WiFi代理设为服务器IP:5701 → 打开库街区APP登录 → Token自动保存。

详细实现见 `kurobbs-signin` skill。

## 热门需求排行

| 平台 | 需求 | 难度 | 状态 |
|------|------|------|------|
| 京东(京豆) | ★★★★★ | 中 | 待开发 |
| 淘宝 | ★★★★ | 中 | 待开发 |
| 哔哩哔哩 | ★★★★ | 低 | 待开发 |
| 饿了么 | ★★★★ | 中 | 待开发 |
| 美团 | ★★★★ | 中 | 待开发 |
| 网易云音乐 | ★★★★ | 低 | 待开发 |
| 微博 | ★★★ | 低 | 待开发 |
| 知乎 | ★★★ | 低 | 待开发 |
| 拼多多 | ★★★ | 中 | 待开发 |

## 注意事项

- 签到API可能随时变更，需要定期维护
- Cookie会过期，脚本需提示用户重新获取
- 部分平台会封号，脚本需控制频率
- 售卖时注明"仅供学习交流"

## GitHub下载镜像（中国大陆）

从GitHub下载Release资产时，直连速度慢。使用镜像加速：

| 镜像站 | 状态 | 格式 |
|--------|------|------|
| `gh-proxy.com` | ✅ 可用（阿里云测试通过） | `https://gh-proxy.com/https://github.com/...` |
| `mirror.ghproxy.com` | ❌ 超时（2026-06阿里云不可用） | 已失效 |
| `ghfast.top` | 待测 | `https://ghfast.top/https://github.com/...` |

示例：
```bash
curl -L -o ProxyPin.apk "https://gh-proxy.com/https://github.com/wanghongenpin/proxypin/releases/download/v1.2.8/proxypin-android.apk"
```
