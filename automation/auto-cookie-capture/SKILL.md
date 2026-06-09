---
name: auto-cookie-capture
description: "自动获取网站/App Cookie 的技术方案：Playwright 模拟登录、requests 直接登录、mitmproxy 抓包。"
version: 1.0.0
author: Hermes
metadata:
  hermes:
    tags: [automation, cookie, login, scraping]
---

# 自动获取 Cookie 技能

## 适用场景
- 番茄小说自动签到（需登录 Cookie）
- 库街区/鸣潮 App 自动签到（需 Token）
- 其他需要登录态的自动化任务

## 方案一：Playwright 模拟登录（推荐，最可靠）

**原理**：启动真实浏览器，自动填写账号密码，获取登录后的 Cookie。

### 番茄小说示例

```python
import json
import asyncio
from playwright.async_api import async_playwright

async def get_fanqie_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 访问登录页
        await page.goto('https://fanqienovel.com')
        await page.click('text=登录')

        # 手机号登录
        await page.fill('input[placeholder="请输入手机号"]', 'YOUR_PHONE')
        await page.fill('input[placeholder="请输入验证码"]', 'YOUR_CODE')

        # 注意：验证码需要手动处理或接打码平台
        await page.click('button:has-text("登录")')

        # 等待登录完成
        await page.wait_for_url('**/library**', timeout=10000)

        # 获取所有 Cookie
        cookies = await context.cookies()

        # 保存到文件
        with open('/home/admin/.hermes/secrets/fanqie_cookies.json', 'w') as f:
            json.dump(cookies, f, indent=2)

        await browser.close()
        return cookies

# 运行
asyncio.run(get_fanqie_cookies())
```

### 提取 Cookie 字符串

```python
def cookies_to_header(cookies):
    return '; '.join(f"{c['name']}={c['value']}" for c in cookies)

cookie_str = cookies_to_header(cookies)
```

## 方案二：requests 模拟登录（轻量，适合简单接口）

**原理**：直接调用登录 API，获取返回的 Token/Cookie。

```python
import requests

def login_fanqie(phone, code):
    session = requests.Session()

    # 登录接口
    resp = session.post('https://fanqienovel.com/api/user/login', json={
        'phone': phone,
        'code': code,
        'type': 'phone'
    })

    if resp.status_code == 200:
        cookies = session.cookies.get_dict()
        return cookies
    return None
```

## 方案三：mitmproxy 抓包（适合 App，需手机配合）

**前提**：手机和电脑在同一局域网。

### 安装
```bash
pip install mitmproxy
```

### 启动代理
```bash
mitmdump --set block_global=false -p 8888 -w capture.flow
```

### 手机设置
1. 设置 → WiFi → 代理 → 手动
2. 服务器：电脑 IP，端口：8888
3. 浏览器访问 `mitm.it` 安装证书
4. 打开目标 App，操作一遍
5. 停止抓包，解析 flow 文件

### 解析 Cookie
```python
from mitmproxy.io import FlowReader

with open('capture.flow', 'rb') as f:
    for flow in FlowReader(f).stream():
        if 'api' in flow.request.pretty_url:
            print(flow.request.pretty_url)
            print(flow.request.headers.get('cookie'))
```

## 方案四：ADB + 手机（无需代理）

**原理**：通过 ADB 连接手机，用 `adb shell` 直接读取 App 数据。

```bash
# 连接手机（USB调试）
adb devices

# 查看 App 数据
adb shell run-as com.kurogame.xxx cat /data/data/com.kurogame.xxx/shared_prefs/*.xml

# 或用 logcat 抓取网络请求
adb logcat | grep -i "cookie\|token\|authorization"
```

## Cookie 存储规范

所有 Cookie 保存到 `~/.hermes/secrets/` 目录：
```
~/.hermes/secrets/
├── fanqie_cookies.json
├── kurogame_token.json
└── jieqicookie.json
```

## User Preferences

- **User cannot do manual proxy/capture** — operates via phone (JuiceSSH), no desktop tools
- **Prefer fully automated solutions** — Playwright/requests over manual mitmproxy
- **Keep instructions simple** — step-by-step, no jargon

## Notes

1. **验证码处理**：番茄小说有短信验证码，需手动输入或接打码平台
2. **Cookie 有效期**：大部分 Cookie 有 7-30 天有效期，需定期刷新
3. **反爬检测**：番茄反爬严格（secsdk+captcha），Playwright 方案有被检测风险
4. **安全存储**：Cookie 文件包含敏感信息，注意权限设置

## 快速使用

告诉我"获取番茄 Cookie"或"抓库街区 Token"，我会：
1. 选择合适方案
2. 执行获取流程
3. 保存到 secrets 目录
4. 更新签到脚本使用新 Cookie
