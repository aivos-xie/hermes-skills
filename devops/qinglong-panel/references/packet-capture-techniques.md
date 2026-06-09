# 抓包技术详解

## 方案对比

| 方案 | 难度 | 需要 | 适用场景 |
|------|------|------|----------|
| mitmproxy | ⭐⭐⭐ | 电脑+手机同WiFi | 通用 App 抓包 |
| Fiddler | ⭐⭐ | Windows 电脑 | Windows 用户 |
| Charles | ⭐⭐ | Mac/Windows | Mac 用户 |
| ADB | ⭐⭐ | USB 数据线 | 无需代理 |
| Playwright | ⭐⭐ | 服务器 | 网页端登录 |

## mitmproxy 详解

### 安装
```bash
pip install mitmproxy
```

### 启动代理
```bash
# 终端交互模式
mitmproxy --set block_global=false -p 8888

# 后台运行+保存
mitmdump --set block_global=false -p 8888 -w capture.flow
```

### 手机配置
1. 手机和电脑连接同一 WiFi
2. 手机设置 → WiFi → 代理 → 手动
3. 服务器：电脑 IP（`ifconfig` 查看），端口：8888
4. 手机浏览器访问 `mitm.it`，下载安装证书
5. 打开目标 App，操作一遍
6. 停止抓包

### 解析 Cookie
```python
from mitmproxy.io import FlowReader

with open('capture.flow', 'rb') as f:
    for flow in FlowReader(f).stream():
        url = flow.request.pretty_url
        if 'api' in url or 'signin' in url:
            print(f"URL: {url}")
            print(f"Cookie: {flow.request.headers.get('cookie')}")
            print(f"Token: {flow.request.headers.get('authorization')}")
            print("---")
```

## ADB 抓包（无需代理）

```bash
# 连接手机（需开启 USB 调试）
adb devices

# 查看 App 数据
adb shell run-as com.package.name cat /data/data/com.package.name/shared_prefs/*.xml

# 抓取网络请求日志
adb logcat | grep -iE "cookie|token|authorization|set-cookie"

# 导出 App 数据
adb pull /data/data/com.package.name/ ./app_data/
```

## Playwright 自动登录

```python
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    page.goto('https://example.com/login')
    page.fill('input[name="username"]', 'user')
    page.fill('input[name="password"]', 'pass')
    page.click('button[type="submit"]')
    page.wait_for_url('**/dashboard**')
    
    cookies = context.cookies()
    with open('cookies.json', 'w') as f:
        json.dump(cookies, f, indent=2)
    
    browser.close()
```

## 常见 App 包名

| App | 包名 |
|-----|------|
| 库街区 | com.kurogame.kjq |
| 鸣潮 | com.kurogame.gplay |
| 番茄小说 | com.dragon.read |
| 京东 | com.jingdong.app.mall |
