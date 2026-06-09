---
name: reverse-engineering
description: 逆向工程工具链 — Ghidra, radare2, Frida, apktool, jadx, angr, pwntools
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [reverse-engineering, binary-analysis, decompilation, debugging, android, exploitation]
---

# 逆向工程工具链

## 核心工具一览

| 工具 | 用途 | 语言 |
|------|------|------|
| **Ghidra** | NSA开源反编译器，支持多架构 | Java |
| **radare2/rizin** | 命令行逆向框架 | C |
| **Frida** | 动态插桩，运行时hook | Python/JS |
| **apktool** | APK反编译/重打包 | Java |
| **jadx** | APK/DEX反编译为Java源码 | Java |
| **angr** | 符号执行/二进制分析框架 | Python |
| **pwntools** | CTF/exploit开发框架 | Python |
| **Capstone** | 多架构反汇编引擎 | C/Python |
| **Keystone** | 多架构汇编引擎 | C/Python |
| **Binwalk** | 固件分析/提取 | Python |
| **strings** | 提取可打印字符串 | 系统自带 |
| **file** | 文件类型识别 | 系统自带 |
| **objdump** | 目标文件反汇编 | 系统自带 |
| **readelf** | ELF文件分析 | 系统自带 |
| **strace** | 系统调用跟踪 | Linux |
| **ltrace** | 库函数调用跟踪 | Linux |

---

## 1. Ghidra — 反编译神器

### 安装
```bash
sudo apt install openjdk-21-jdk wget unzip
wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.1.2_build/ghidra_12.1.2_PUBLIC_20260605.zip
unzip ghidra_*.zip -d /opt/
/opt/ghidra_*/ghidraRun
# 无头模式
/opt/ghidra_*/support/analyzeHeadless /tmp/project MyProject -import /path/to/binary -postScript /path/to/script.java
# PyGhidra (Python无头模式)
/opt/ghidra_*/support/pyghidraRun
```

### 核心用法
```
1. File -> Import File -> 选择二进制
2. 自动分析(Analysis -> Auto Analyze)
3. 左侧Symbol Tree -> Functions查看函数列表
4. 双击函数进入反编译视图
5. Ctrl+E 打开脚本管理器
```

### GhidraScript 自动化(Java)
```java
// 找所有字符串引用
import ghidra.program.util.DefinedDataIterator;
for (var data : DefinedDataIterator.definedStrings(currentProgram)) {
    println(data.getAddress() + ": " + data.getDefaultValueRepresentation());
}
```

### 无头批量分析
```bash
/opt/ghidra_*/support/analyzeHeadless /tmp/ghidra_projects batch \
  -import /path/to/binary \
  -postScript FindStrings.java \
  -scriptPath /path/to/scripts \
  -deleteProject
```

---

## 2. radare2/rizin — 命令行逆向

### 安装
```bash
# radare2
git clone https://github.com/radareorg/radare2 && cd radare2 && sys/install.sh
# rizin
git clone https://github.com/rizinorg/rizin && cd rizin && meson build && ninja -C build && sudo ninja -C build install
```

### 常用命令
```bash
r2 -A ./binary           # 打开并自动分析
r2 -A -d ./binary        # 调试模式

aaa                      # 全面分析
afl                      # 列出所有函数
pdf @main                # 反汇编main
s sym.main               # 跳转到main
V                        # 可视化模式
VV                       # 图形可视化
iz                       # 列出字符串
axt @str.0x401000        # 交叉引用
db main                  # 设置断点
dc                       # 继续执行
pxr 64 @rsp              # 查看栈
dr                       # 查看寄存器
```

### r2pipe 自动化
```python
import r2pipe
r2 = r2pipe.open("./binary")
r2.cmd("aaa")
functions = r2.cmdj("aflj")
for func in functions:
    print(f"{func['offset']}: {func['name']}")
r2.quit()
```

---

## 3. Frida — 动态插桩

### 安装
```bash
pip install frida-tools frida
# Android: 下载frida-server推送到设备
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"
```

### 核心用法
```bash
frida-ps                          # 列出进程
frida-ps -U                       # USB设备(手机)
frida -U -n com.target.app -l hook.js   # 注入
frida -U -f com.target.app -l hook.js --no-pause  # spawn模式
```

### Hook Java方法(hook.js)
```javascript
Java.perform(function() {
    var LoginActivity = Java.use("com.target.app.LoginActivity");
    LoginActivity.checkPassword.implementation = function(password) {
        console.log("Password: " + password);
        var result = this.checkPassword(password);
        console.log("Result: " + result);
        return result;
    };
});
```

### Hook Native函数(hook.js)
```javascript
Interceptor.attach(Module.findExportByName("libnative.so", "encrypt"), {
    onEnter: function(args) {
        console.log("encrypt input: " + Memory.readUtf8String(args[0]));
    },
    onLeave: function(retval) {
        console.log("encrypt output: " + retval);
    }
});
```

### Python控制Frida
```python
import frida

device = frida.get_usb_device()
session = device.attach("com.target.app")

js_code = """
Java.perform(function() {
    var cls = Java.use("com.target.app.Crypto");
    cls.encrypt.overload("java.lang.String").implementation = function(input) {
        send({type: "plaintext", data: input});
        var result = this.encrypt(input);
        send({type: "ciphertext", data: result});
        return result;
    };
});
"""

script = session.create_script(js_code)
def on_message(message, data):
    print(f"[Frida] {message}")
script.on("message", on_message)
script.load()
input()
```

---

## 4. Android逆向 (apktool + jadx)

### apktool
```bash
wget https://github.com/iBotPeaches/Apktool/releases/latest/download/apktool.jar
sudo mv apktool.jar /usr/local/bin/

# 反编译
java -jar /usr/local/bin/apktool.jar d target.apk -o output_dir

# 重打包
java -jar /usr/local/bin/apktool.jar b output_dir -o modified.apk

# 签名
keytool -genkey -v -keystore my.keystore -alias my -keyalg RSA -keysize 2048 -validity 10000
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my.keystore modified.apk my
```

### jadx
```bash
wget https://github.com/skylot/jadx/releases/download/v1.5.5/jadx-1.5.5.zip
unzip jadx-*.zip -d /opt/jadx

# GUI
/opt/jadx/bin/jadx-gui target.apk

# 命令行
/opt/jadx/bin/jadx target.apk -o output_dir
grep -r "password\|api_key\|secret" output_dir/
```

### APK分析流程
```
1. jadx-gui打开APK -> 查看Java源码逻辑
2. apktool反编译 -> 查看smali、AndroidManifest.xml、资源
3. Frida动态hook -> 运行时抓取密钥/加密结果
4. 修改smali -> 重打包绕过检测
```

---

## 5. angr — 符号执行

### 安装
```bash
pip install angr
```

### 密码验证绕过
```python
import angr, claripy

proj = angr.Project("./crackme", auto_load_libs=False)
flag = claripy.BVS("flag", 32 * 8)
state = proj.factory.entry_state(stdin=flag)
simgr = proj.factory.simgr(state)
simgr.explore(find=0x401337)  # 成功地址

if simgr.found:
    found = simgr.found[0]
    print("Flag:", found.solver.eval(flag, cast_to=bytes))
```

---

## 6. pwntools — CTF/Exploit框架

### 安装
```bash
pip install pwntools
```

### 基本用法
```python
from pwn import *

r = remote("challenge.ctf.com", 1337)
r.recvuntil(b"Enter password: ")
r.sendline(b"admin")

# 自动找偏移
cyclic(100)
cyclic_find(0x6161616b)

# 构造payload
payload = b"A" * offset
payload += p64(0x401234)

# ret2libc
elf = ELF("./binary")
libc = ELF("./libc.so.6")
rop = ROP(elf)
rop.call(elf.plt["system"], [next(elf.search(b"/bin/sh"))])

# shellcode
context.arch = "amd64"
shellcode = asm(shellcraft.sh())

r.sendline(payload)
r.interactive()
```

---

## 7. 系统自带工具

```bash
strings binary | grep -i "password\|key\|secret\|flag"
strings -n 8 binary
strings -el binary           # 宽字符

file binary
objdump -d binary            # 反汇编
objdump -t binary            # 符号表
readelf -h binary            # ELF头
readelf -S binary            # 段表

strace ./binary              # 系统调用跟踪
strace -e trace=open,read ./binary
ltrace ./binary              # 库函数跟踪

# binwalk v3 (Rust重写!) — 推荐用cargo安装
# cargo install binwalk
# 或从源码: git clone https://github.com/ReFirmLabs/binwalk && cd binwalk && cargo build --release
binwalk firmware.bin         # 固件扫描
binwalk -e firmware.bin      # 提取嵌入文件
binwalk -E firmware.bin      # 熵分析
binwalk -Me firmware.bin     # 递归提取
```

### checksec
```bash
pip install checksec.py
checksec ./binary
# RELRO / Stack Canary / NX / PIE
```

---

## 8. CTF逆向常用流程

```
1. file binary -> 识别架构和类型
2. strings binary -> 快速找flag/密码/提示
3. checksec binary -> 检查保护
4. r2 -A binary -> 快速分析
5. ghidra -> 深度反编译理解逻辑
6. angr -> 符号执行自动求解
7. pwntools -> 写exploit打远程
```

---

## Pitfalls

1. **Ghidra需要JDK21+** — v12.x要求JDK21，低版本启动失败
2. **radare2命令多** — 先学 aaa + afl + pdf + iz 四个就够
3. **Frida需要root** — Android必须root或用模拟器
4. **apktool签名问题** — 重打包后必须重新签名
5. **angr路径爆炸** — 复杂程序会卡住，加约束限制路径
6. **pwntools架构设置** — 必须 context.arch = "amd64" 或 "i386"
7. **strace对静态链接无效** — ltrace看不到静态编译的库调用
8. **Frida版本匹配** — frida-tools和frida-server版本必须一致

---

## 9. 新增工具速查

### blutter — Flutter逆向
```bash
git clone https://github.com/worawit/blutter.git && cd blutter
sudo apt install python3-pyelftools python3-requests git cmake ninja-build build-essential pkg-config libicu-dev libcapstone-dev
# 从APK提取libapp.so和libflutter.so后:
python3 blutter.py /path/to/arm64-v8a/ /path/to/output/
```

### PINCE — Linux游戏逆向 (Cheat Engine替代)
```bash
git clone https://github.com/korcankaraokcu/PINCE.git && cd PINCE
sudo sh install_pince.sh
```

### ghidra-mcp — AI驱动的Ghidra逆向
```bash
# Ghidra MCP Server — 200+ MCP工具，让AI/LLM辅助二进制分析
# https://github.com/bethington/ghidra-mcp
# 安装: 按README安装Ghidra插件 + 无头服务器
```

### ida-pro-mcp — AI驱动的IDA Pro逆向
```bash
# IDA Pro + LLM桥接，通过MCP协议让AI直接操作IDA
# https://github.com/mrexodia/ida-pro-mcp
# 安装: 按README安装IDA插件
```
