# mitmproxy 搭建详情

## 安装

Alibaba Cloud Linux上PyPI直连超时，必须用阿里云镜像：

```bash
uv venv /tmp/mitm-env --python python3.11
uv pip install --python /tmp/mitm-env/bin/python mitmproxy \
  -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

## CA证书

首次运行mitmdump会自动生成CA证书到 `~/.mitmproxy/`：
- `mitmproxy-ca-cert.cer` — Android安装用
- `mitmproxy-ca-cert.pem` — Linux/iOS用

证书复制到网盘方便手机下载：
```bash
cp ~/.mitmproxy/mitmproxy-ca-cert.cer /opt/aivos-disk/storage/
```

Android安装路径: 设置 → 安全 → 加密与凭据 → 安装证书 → CA证书
⚠️ 部分手机需先设置锁屏密码

## 启动命令

```bash
# 先停掉占用5701端口的进程
fuser -k 5701/tcp 2>/dev/null

# 启动mitmproxy（带捕获脚本）
/tmp/mitm-env/bin/mitmdump -p 5701 \
  --set upstream_cert=false \
  -s /tmp/kuro_capture.py \
  --set block_global=false \
  -q 2>&1
```

## 关键注意事项

1. **抓到Token后必须关掉手机代理**，否则影响正常上网
2. mitmproxy的`-q`参数减少日志噪音
3. `block_global=false`允许外部连接（默认只允许localhost）
4. `upstream_cert=false`跳过上游证书验证，避免APP证书pinning问题
5. Token一般7-30天过期，过期需重新抓取

## 故障排查

**mitmproxy无响应/请求超时：**
- 症状：curl通过代理请求超时，手机APP也超时
- 原因：mitmproxy运行一段时间后可能变得无响应（连接堆积）
- 解决：kill重启 `fuser -k 5701/tcp && /tmp/mitm-env/bin/mitmdump ...`
- 诊断：先用 `curl -x http://localhost:5701 http://httpbin.org/ip` 测试本地代理
- 调试：去掉`-q`参数查看mitmproxy日志输出

**手机连不上代理：**
- 检查防火墙: `sudo firewall-cmd --list-ports` 确认5701已放行
- 检查阿里云安全组是否开放5701
- 检查mitmproxy是否绑定了0.0.0.0（`--set block_global=false`）

**CA证书安装失败：**
- Android需要先设置锁屏密码才能安装CA证书
- 部分Android版本路径: 设置→安全→信任的凭据→从存储设备安装
