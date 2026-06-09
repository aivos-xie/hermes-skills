---
name: security-toolkit
description: 安全测试总览 — 逆向工程、密码爆破、Web安全三大方向工具链
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [security, penetration-testing, red-team, toolkit]
    related_skills: [reverse-engineering, password-cracking, web-security, network-pentest, wireless-security, cryptography-attacks, malware-analysis, digital-forensics, osint, evasion-techniques, ai-reverse-engineering, mobile-security, bug-bounty, cloud-security, active-directory, godmode, obliteratus]
---

# 安全测试工具链总览

## 三大方向

| 方向 | Skill | 核心工具 |
|------|-------|---------|
| 逆向工程 | `reverse-engineering` | Ghidra, radare2, Frida, apktool, jadx, angr, pwntools |
| 密码爆破 | `password-cracking` | hashcat, John, Hydra, CeWL, crunch |
| Web安全 | `web-security` | sqlmap, Nmap, Nikto, XSStrike, ffuf, nuclei, Metasploit |

## 快速选型

### 我要逆向一个二进制
```
1. file binary → 识别类型
2. strings binary → 快速搜字符串
3. r2 -A binary → 快速分析
4. ghidra → 深度反编译
5. angr → 符号执行求解
```

### 我要破解密码
```
1. hashid → 识别hash类型
2. hashcat -m <mode> -a 0 hash.txt rockyou.txt → 字典攻击
3. hashcat -m <mode> -a 0 -r rules/best64.rule hash.txt rockyou.txt → 规则
4. hashcat -m <mode> -a 3 hash.txt ?d?d?d?d?d?d → 掩码暴力
```

### 我要渗透测试Web应用
```
1. nmap -sV -sC target → 端口扫描
2. whatweb target → 指纹识别
3. ffuf -u target/FUZZ -w common.txt → 目录扫描
4. nuclei -u target → 漏洞扫描
5. sqlmap -u "target/?id=1" → SQL注入
```

## 安装快速参考

```bash
# 逆向
sudo apt install binwalk strace ltrace
pip install frida-tools pwntools angr capstone keystone
git clone https://github.com/radareorg/radare2 && cd radare2 && sys/install.sh

# 爆破
sudo apt install hashcat john hydra nmap nikto
pip install hashid name-that-hash

# Web
pip install sqlmap wafw00f
git clone https://github.com/s0md3v/XSStrike.git
git clone https://github.com/commixproject/commix.git
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/projectdiscovery/ffuf/v2/cmd/ffuf@latest
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

## Skill 列表(16个)

| Skill | 方向 | 核心工具 | 关键更新 |
|-------|------|---------|---------|
| reverse-engineering | 逆向 | Ghidra 12.1.2, radare2 6.1.6, Frida 17.11, binwalk 3.1(Rust) | JDK21, blutter, ghidra-mcp |
| password-cracking | 爆破 | hashcat 7.1.2, John, Hydra 9.7 | KeePass4/SM3模式, BruteSpray |
| web-security | Web | sqlmap v1.10, nuclei v3.8.0, ffuf, ZAP v2.17 | katana, dalfox, Fenjing, dnsReaper |
| network-pentest | 内网 | CME, Impacket, Chisel, ligolo-ng, BloodHound | Evil-WinRM, AD CS |
| wireless-security | 无线 | Aircrack-ng, Wifite2, bettercap, Proxmark3 | PMKID, BLE, SDR |
| cryptography-attacks | 密码学 | SageMath, RsaCtfTool, PadBuster | RSA多攻击, AES Padding Oracle |
| malware-analysis | 恶意软件 | YARA, Volatility, Cuckoo, PEframe | 脱壳, 反调试绕过 |
| digital-forensics | 取证 | Autopsy, Volatility 3, plaso, Chainsaw | 内存取证, 云/容器取证 |
| osint | 情报 | Sherlock, holehe, Shodan, theHarvester | Google Dorking, 社交媒体 |
| evasion-techniques | 免杀 | Sliver, Havoc, ScareCrow, Donut | AMSI绕过, 域前置, DNS隧道 |
| ai-reverse-engineering | AI逆向 | ghidra-mcp, ida-pro-mcp, LLM4Decompile, blutter | Flutter/Godot/Unity RE |
| mobile-security | 移动 | MobSF, Frida, Objection, Magisk | SSL pinning绕过, APK重打包 |
| bug-bounty | 漏洞猎人 | subfinder→httpx→katana→nuclei pipeline | 自动化recon脚本 |
| cloud-security | 云 | Prowler, Trivy, Pacu, Stratus Red Team | AWS/Azure/GCP/K8s |
| active-directory | 域渗透 | BloodHound, Certipy, bloodyAD, DonPAPI | ESC1-8, DCSync, DPAPI |
| security-toolkit | 总览 | 本文件 | 快速选型指南 |

## 快速选型

### 逆向二进制
`file` → `strings` → `r2 -A` → `ghidra` → `angr` → `pwntools`

### 破解密码
`hashid` → `hashcat -m <mode> -a 0 hash.txt rockyou.txt` → `hashcat -r rules/best64.rule` → `hashcat -a 3 ?d?d?d?d?d?d`

### 渗透Web
`nmap` → `whatweb` → `ffuf` → `nuclei` → `sqlmap` → `XSStrike` → `Commix`

### 内网渗透
`CME枚举` → `BloodHound分析` → `Responder捕获hash` → `Pass-the-Hash横向` → `DCSync导出域hash`

### 安装快速参考
```bash
# 核心工具
sudo apt install nmap nikto hashcat john hydra binwalk strace ltrace
pip install frida-tools pwntools angr capstone impacket crackmapexec
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/projectdiscovery/ffuf/v2/cmd/ffuf@latest
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
```

## 法律声明

所有工具仅用于授权的安全测试。未经授权的渗透测试是违法的。
