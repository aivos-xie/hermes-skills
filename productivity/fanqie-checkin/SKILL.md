---
name: fanqie-checkin
description: "番茄小说自动签到：网页端API签到获取金币奖励"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [fanqie, novel, checkin, automation, 番茄小说, 签到]
---

# 番茄小说自动签到

通过网页端API实现番茄小说每日自动签到，获取金币奖励。

## When to Use

- 每日自动签到番茄小说获取金币
- 配合定时任务(cron)实现无人值守

## 快速开始

### 1. 获取Cookie

**方式一：浏览器获取（推荐）**

1. 打开浏览器访问 https://fanqienovel.com/
2. 使用手机号/今日头条账号登录
3. 按F12打开开发者工具
4. 点击 Application → Cookies → fanqienovel.com
5. 复制以下关键字段：
   - `sessionid`
   - `novel_web_id`
   - `ttwid`

**方式二：使用Playwright自动获取**

```bash
pip install playwright
playwright install chromium
python get_cookie.py
```

### 2. 配置Cookie

编辑 `~/.hermes/scripts/fanqie_checkin.py`，填入你的Cookie：

```python
COOKIES = {
    "sessionid": "你的sessionid",
    "novel_web_id": "你的novel_web_id",
    "ttwid": "你的ttwid",
}
```

### 3. 运行签到

```bash
python ~/.hermes/scripts/fanqie_checkin.py
```

### 4. 设置定时任务

在青龙面板中添加任务，或使用系统cron：

```bash
# 每天早上8点签到
0 8 * * * python3 ~/.hermes/scripts/fanqie_checkin.py
```

## API接口

详细API文档见 [references/fanqie-api.md](references/fanqie-api.md)

### 签到接口

| 项目 | 详情 |
|------|------|
| **URL** | `https://fanqienovel.com/api/reader/sign_in` |
| **请求方式** | `POST` |
| **认证方式** | Cookie |
| **Content-Type** | `application/json` |

### 查询签到状态

| 项目 | 详情 |
|------|------|
| **URL** | `https://fanqienovel.com/api/reader/sign_in/query` |
| **请求方式** | `GET` |
| **认证方式** | Cookie |

### 请求Headers

```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Referer: https://fanqienovel.com/
Cookie: sessionid=xxx; novel_web_id=xxx; ttwid=xxx
```

## 实现代码

### Python实现

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""番茄小说自动签到"""

import requests
import json
from datetime import datetime

# 配置Cookie - 请替换为你的实际Cookie
COOKIES = {
    "sessionid": "YOUR_SESSION_ID",
    "novel_web_id": "YOUR_NOVEL_WEB_ID",
    "ttwid": "YOUR_TTWID",
}

SIGN_URL = "https://fanqienovel.com/api/reader/sign_in"
QUERY_URL = "https://fanqienovel.com/api/reader/sign_in/query"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://fanqienovel.com/",
    "Content-Type": "application/json",
}

def query_sign_status():
    """查询签到状态"""
    session = requests.Session()
    session.cookies.update(COOKIES)
    session.headers.update(HEADERS)
    
    try:
        resp = session.get(QUERY_URL)
        data = resp.json()
        print(f"📋 签到状态查询: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return None

def sign_in():
    """执行签到"""
    session = requests.Session()
    session.cookies.update(COOKIES)
    session.headers.update(HEADERS)
    
    try:
        resp = session.post(SIGN_URL)
        data = resp.json()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if data.get("code") == 0:
            reward = data.get("data", {}).get("reward", 0)
            print(f"✅ [{now}] 签到成功！获得 {reward} 金币")
        else:
            msg = data.get("message", "未知错误")
            print(f"⚠️ [{now}] 签到结果: {msg}")
        
        return data
    except Exception as e:
        print(f"❌ [{now}] 签到失败: {e}")
        return None

if __name__ == "__main__":
    print("🍅 番茄小说自动签到")
    print("=" * 40)
    
    # 先查询状态
    query_sign_status()
    
    # 执行签到
    sign_in()
```

### Node.js实现

```javascript
const axios = require('axios');

const COOKIES = {
    sessionid: 'YOUR_SESSION_ID',
    novel_web_id: 'YOUR_NOVEL_WEB_ID',
    ttwid: 'YOUR_TTWID',
};

const cookieStr = Object.entries(COOKIES)
    .map(([k, v]) => `${k}=${v}`)
    .join('; ');

const headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://fanqienovel.com/',
    'Cookie': cookieStr,
    'Content-Type': 'application/json',
};

async function signIn() {
    try {
        const resp = await axios.post('https://fanqienovel.com/api/reader/sign_in', {}, { headers });
        const data = resp.data;
        
        if (data.code === 0) {
            console.log(`✅ 签到成功！获得 ${data.data?.reward || 0} 金币`);
        } else {
            console.log(`⚠️ 签到结果: ${data.message}`);
        }
    } catch (e) {
        console.log(`❌ 签到失败: ${e.message}`);
    }
}

signIn();
```

## 青龙面板配置

### 环境变量

在青龙面板中添加环境变量：

| 变量名 | 值 |
|--------|-----|
| `FANQIE_SESSION_ID` | 你的sessionid |
| `FANQIE_NOVEL_WEB_ID` | 你的novel_web_id |
| `FANQIE_TTWID` | 你的ttwid |

### 定时任务

```bash
# 每天早上8:30签到
30 8 * * * python3 /ql/scripts/fanqie_checkin.py
```

## ⚠️ CRITICAL: Cookie类型不通用

**网页端Cookie和APP端Cookie是两套完全不同的体系，不能混用。**

| 类型 | 来源 | 关键字段 | 适用接口 |
|------|------|---------|---------|
| 网页端Cookie | 浏览器登录 fanqienovel.com | `sessionid`, `novel_web_id`, `ttwid` | 网页端API (`fanqienovel.com/api/...`) |
| APP端Cookie | 手机APP抓包 | `install_id`, `passport_csrf_token` | APP端API (`fqnovel.com/reading/...`) |

**实测结果 (2026-06):**
- 浏览器导出的Cookie（`passport_auth_status`, `passport_mfa_token`等）发送到网页端API返回 `"请先登录"`，说明不是真正的登录态
- 浏览器Cookie中**没有** `sessionid` 和 `ttwid` — 这两个才是网页端真正的登录凭证
- 现有脚本 `~/fanqie_checkin.py` 使用APP端API，需要 `install_id`（只能通过抓包获取）

**网页端签到可行性未验证** — 网页端 `/api/reader/sign_in` 返回403（WAF拦截），可能需要额外的反爬token。

**推荐方案：用APP端API + HttpCanary抓包获取 `install_id`**

## 注意事项

1. **Cookie有效期**：APP端Cookie有效期约1-2个月，过期需重新抓包
2. **频率限制**：每日签到一次即可，不要频繁请求
3. **接口变动**：字节系API可能更新，需关注接口变化
4. **风控检测**：保持User-Agent一致性，避免异常请求频率
5. **多账号**：如需多账号签到，用 `&` 分隔多个Cookie

## Cookie获取脚本

### 使用Playwright获取Cookie

```python
#!/usr/bin/env python3
"""获取番茄小说Cookie"""

from playwright.sync_api import sync_playwright
import json

def get_cookies():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://fanqienovel.com/")
        
        print("请在浏览器中登录番茄小说...")
        print("登录完成后按回车继续...")
        input()
        
        cookies = context.cookies()
        
        cookie_dict = {}
        for cookie in cookies:
            if cookie['name'] in ['sessionid', 'novel_web_id', 'ttwid']:
                cookie_dict[cookie['name']] = cookie['value']
        
        print(f"\n获取到的Cookie:")
        print(json.dumps(cookie_dict, indent=2))
        
        browser.close()
        return cookie_dict

if __name__ == "__main__":
    cookies = get_cookies()
```

## 故障排除

### 签到失败：code != 0

- 检查Cookie是否过期
- 确认是否已经签到过（重复签到会返回已签到提示）
- 检查网络连接

### Cookie获取失败

- 确保使用最新版本的浏览器
- 尝试清除浏览器缓存后重新登录
- 检查网络代理设置

### 接口返回403

- Cookie可能已失效，重新获取
- 检查User-Agent是否正确

## 相关链接

- 番茄小说官网: https://fanqienovel.com/
- 字节跳动开放平台: https://open.douyin.com/

## 法律声明

本脚本仅供学习研究使用，请遵守番茄小说的用户协议和使用条款。自动签到属于个人使用范畴，请勿用于商业用途或恶意刷取奖励。