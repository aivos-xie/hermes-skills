---
name: kurobbs-signin
description: 库街区(Kurobbs)自动签到 — Token获取与签到流程
category: productivity
---

# 库街区自动签到

## 概述
库街区是库洛游戏(Kuro Games)的社区APP，签到需APP端Token。
- API域名: `api.kurobbs.com`
- 签到接口需要`KURO_TOKEN`环境变量

## Token获取方案

### 方案1: mitmproxy MITM拦截（推荐 ✅ 已验证）

库街区**网页版不支持登录**，只能APP登录。反向代理方案不可行（SPA资源加载问题+无登录入口）。
正确方案是用 **mitmproxy** 做HTTPS中间人代理，拦截APP的登录请求。

**原理**: 手机WiFi代理指向服务器mitmproxy → APP的HTTPS流量经过代理 → mitmproxy解密HTTPS → 拦截`sdkLogin`响应 → 提取Token存入青龙。

**服务器端搭建:**
```bash
# 安装mitmproxy（PyPI超时，用阿里云镜像）
uv venv /tmp/mitm-env --python python3.11
uv pip install --python /tmp/mitm-env/bin/python mitmproxy \
  -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 首次运行生成CA证书
timeout 3 /tmp/mitm-env/bin/mitmdump -p 5701 --set upstream_cert=false
# CA证书生成在 ~/.mitmproxy/

# 启动（带捕获脚本）
/tmp/mitm-env/bin/mitmdump -p 5701 \
  --set upstream_cert=false \
  -s /tmp/kuro_capture.py \
  --set block_global=false
```

**捕获脚本** `scripts/kuro_capture.py`（本skill自带）: 监听`api.kurobbs.com`的`sdkLogin`/`login`响应，code=200时提取`data.token`，自动存入青龙`KURO_TOKEN`。部署时复制到`/tmp/kuro_capture.py`使用。

**手机端操作（3步）:**

1. **安装CA证书**（只需一次）
   - 从网盘下载 `mitmproxy-ca-cert.cer` (`http://服务器IP:5244`)
   - Android: 设置 → 安全 → 加密与凭据 → 安装证书 → CA证书 → 选择.cer文件
   - ⚠️ 部分手机需要先设置锁屏密码才能安装CA证书

2. **设置WiFi代理**
   - WiFi设置 → 修改当前网络 → 高级选项 → 代理手动
   - 主机名: `服务器IP`, 端口: `5701`

3. **打开库街区APP登录**
   - 登录成功 → Token自动保存到青龙
   - 页面会自动跳转到绿色"Token获取成功"页面
   - ⚠️ 抓到Token后**立即关掉手机代理**，否则影响正常上网

### 方案2: ProxyPin/HttpCanary手动抓包
- 手机安装ProxyPin（网盘有APK）或HttpCanary
- 打开APP登录 → 找到`api.kurobbs.com/user/sdkLogin`请求
- 响应中`data.token`即为KURO_TOKEN
- 手动复制Token → 告诉我存入青龙

### 方案3: 模拟登录（不可行）
- 发送验证码API(`/user/sendSms`)需要**内部访问令牌**（APP内置）
- `sdkLogin`接口也需要设备信息+验证码，无法从外部调用
- 结论: 不可自动化，需走方案1或2

### ⚠️ 已验证的失败方案

**反向代理网页版**（不可行）:
- kurobbs.com是SPA，静态资源在`web-static.kurobbs.com`和`prod-alicdn-community.kurobbs.com`
- 即使代理了HTML+CDN域名，网页版**没有登录入口**，只能APP登录
- 反向代理方案从原理上不可行

## API参考
```
POST https://api.kurobbs.com/user/sdkLogin
  - 需要APP端请求，含设备信息、验证码等
  - 返回: {"code":200, "data":{"token":"eyJ..."}}

POST https://api.kurobbs.com/user/sendSms
  - 需要内部访问令牌(header中)
  - 返回: {"code":220,"msg":"访问令牌不能为空"} ← 无内部令牌时
```

## Token有效期
- 一般7-30天，过期后青龙任务会失败
- 过期需重新走Token获取流程

## 青龙面板配置
- 环境变量名: `KURO_TOKEN`
- 值: JWT格式的token (以`eyJ`开头)
