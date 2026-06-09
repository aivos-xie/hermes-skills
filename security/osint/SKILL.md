---
name: osint
description: 开源情报收集 — 社工、人肉搜索、域名/IP/邮箱情报、社交媒体
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [osint, social-engineering, reconnaissance, people-search, domain-intel]
---

# OSINT开源情报工具链

## 核心工具

| 工具 | 用途 |
|------|------|
| **Maltego** | 关系图谱分析 |
| **Recon-ng** | 信息收集框架 |
| **theHarvester** | 邮箱/域名/IP收集 |
| **Shodan** | 设备/服务搜索引擎 |
| **Censys** | 互联网设备搜索 |
| **SpiderFoot** | 自动化OSINT |
| **Sherlock** | 社交媒体用户名搜索 |
| **holehe** | 邮箱关联账户查询 |
| **Photon** | 网站爬取 |
| **Wayback Machine** | 历史网页快照 |
| **WHOIS** | 域名注册信息 |
| **DNSrecon** | DNS枚举 |
| **Amass** | 子域名枚举 |
| **Metagoofil** | 文档元数据提取 |
| **Creepy** | 地理位置情报 |
| **tinfoleak** | Twitter情报 |

---

## 1. 域名/IP情报

### WHOIS查询
```bash
whois target.com
whois 192.168.1.1

# 提取关键信息
whois target.com | grep -E 'Registrar|Name Server|Creation Date|Registrant'
```

### DNS枚举
```bash
# 基本查询
dig target.com ANY
dig target.com A
dig target.com MX
dig target.com TXT
dig target.com NS
dig target.com CNAME

# 反向DNS
dig -x 192.168.1.1

# 区域传送(如果允许)
dig @ns1.target.com target.com AXFR

# 子域名爆破
dnsrecon -d target.com -t brt
dnsrecon -d target.com -t std

# subfinder
subfinder -d target.com -silent

# amass
amass enum -d target.com
amass enum -d target.com -passive
```

### Shodan搜索
```bash
pip install shodan

# 设置API key
export SHODAN_API_KEY="your_key"

# 搜索
shodan search "org:Target port:80"
shodan search "product:apache country:CN"
shodan search "http.title:login"
shodan search "ssl:target.com"

# 主机信息
shodan host 192.168.1.1

# 命令行
shodan init YOUR_API_KEY
shodan scan submit 192.168.1.0/24
shodan stats --facets country,port vuln:ms17-010
```

### Censys搜索
```bash
pip install censys

# 搜索证书
censys search "parsed.subject.common_name: target.com"

# 搜索主机
censys search "services.port=443 AND location.country=China"

# 查看特定主机
censys view 192.168.1.1
```

---

## 2. 人肉搜索

### Sherlock — 社交媒体搜索
```bash
git clone https://github.com/sherlock-project/sherlock.git
cd sherlock && pip install -r requirements.txt

# 搜索用户名
python sherlock.py username123

# 搜索多个用户名
python sherlock.py user1 user2 user3

# 输出到文件
python sherlock.py username123 -o output.txt

# 指定站点
python sherlock.py username123 --site twitter,instagram,github
```

### holehe — 邮箱关联账户
```bash
pip install holehe

holehe email@example.com
# 输出: 该邮箱注册了哪些网站
```

### 邮箱情报
```bash
# theHarvester
theHarvester -d target.com -b google,bing,linkedin

# hunter.io (API)
curl "https://api.hunter.io/v2/domain-search?domain=target.com&api_key=YOUR_KEY"

# 验证邮箱
smtp-verify email@target.com

# 查找泄露密码
# HaveIBeenPwned API
curl "https://haveibeenpwned.com/api/v3/breachedaccount/email@example.com" \
  -H "hibp-api-key: YOUR_KEY"
```

### 电话号码情报
```bash
# phonenumbers (Python)
pip install phonenumbers
python3 -c "
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
number = phonenumbers.parse('+8613800138000')
print(geocoder.description_for_number(number, 'zh'))
print(carrier.name_for_number(number, 'zh'))
print(timezone.time_zones_for_number(number))
"
```

---

## 3. 社交媒体情报

### Twitter/X情报
```bash
# tinfoleak
pip install tinfoleak

# sn0int (框架)
# 收集推文、关注者、地理位置
```

### LinkedIn情报
```bash
# linkedin2username
git clone https://github.com/initstring/linkedin2username.git
python linkedin2username.py -c "Company Name"

# linkedin-scraper
pip install linkedin-scraper
```

### GitHub情报
```bash
# 搜索泄露的密钥
# GitHub Dorking
"target.com" password
"target.com" api_key
org:target secret
org:target password

# gitleaks
pip install gitleaks
gitleaks detect -s /path/to/repo
```

---

## 4. 文档情报

### Metagoofil — 文档元数据
```bash
git clone https://github.com/laramies/metagoofil.git
python metagoofil.py -d target.com -t pdf,docx -l 100 -o output -f results.html
```

### 批量文档分析
```bash
# 下载目标网站的PDF/DOC文件
wget -r -A pdf,doc,docx https://target.com/

# 提取元数据
exiftool -r /downloaded/documents/

# 关键信息
# - 作者名称
# - 公司名称
# - 软件版本
# - 创建时间
# - 文件路径(可能泄露内部结构)
```

---

## 5. 图片情报

### 图片搜索
```bash
# Google反向图片搜索
# https://images.google.com → 上传图片

# TinEye
# https://tineye.com

# Yandex图片搜索
# https://yandex.com/images/
```

### 地理位置
```bash
# 从图片EXIF提取GPS
exiftool -GPSLatitude -GPSLongitude image.jpg

# 转换为十进制坐标
python3 -c "
lat = 39 + 54/60 + 26.4/3600  # 39°54'26.4"N
lon = 116 + 23/60 + 29.88/3600  # 116°23'29.88"E
print(f'{lat}, {lon}')
"

# Google Maps查看
# https://maps.google.com/?q=39.9073,116.3916
```

---

## 6. 网站情报

### 网站技术栈
```bash
# whatweb
whatweb target.com

# Wappalyzer CLI
npm install -g wappalyzer
wappalyzer https://target.com

# BuiltWith
# https://builtwith.com/target.com
```

### 历史快照
```bash
# Wayback Machine
curl "https://archive.org/wayback/available?url=target.com"

# 查看历史快照
# https://web.archive.org/web/*/target.com

# waybackurls
go install github.com/tomnomnom/waybackurls@latest
echo target.com | waybackurls > urls.txt
```

### robots.txt和sitemap
```bash
curl https://target.com/robots.txt
curl https://target.com/sitemap.xml
curl https://target.com/.well-known/security.txt
```

---

## 7. 自动化OSINT框架

### SpiderFoot
```bash
git clone https://github.com/smicallef/spiderfoot.git
cd spiderfoot && pip install -r requirements.txt

# Web界面
python sf.py -l 127.0.0.1:5001

# 命令行
python sfcli.py -s target.com -m sfp_dnsresolve,sfp_whois
```

### Recon-ng
```bash
sudo apt install recon-ng

# 启动
recon-ng

# 创建工作区
workspaces create target

# 安装模块
marketplace install all

# 搜索模块
modules search whois
modules load recon/domains-hosts/hackertarget

# 设置选项
options set SOURCE target.com
run
```

### OSINT Framework
```
https://osintframework.com
# 交互式决策树，引导你选择合适的OSINT工具
```

---

## 8. Google Dorking

### 常用Dork
```
site:target.com                     # 限定域名
filetype:pdf                        # 文件类型
intitle:"index of"                  # 目录列表
inurl:admin                         # URL包含admin
intext:password                     # 内容包含password
cache:target.com                    # 缓存
link:target.com                     # 链接到目标
related:target.com                  # 相似网站
```

### 实用Dork组合
```
site:target.com filetype:pdf
site:target.com intitle:"index of"
site:target.com inurl:login
site:target.com ext:php inurl:?
site:target.com "api_key" OR "api_secret"
site:pastebin.com "target.com"
site:github.com "target.com" password
"target.com" "password" filetype:txt
intitle:"Dashboard" inurl:"/admin"
```

---

## Pitfalls

1. **OSINT不等于入侵** — 只收集公开信息
2. **信息可能过时** — WHOIS可能有隐私保护
3. **Sherlock假阳性多** — 需要手动验证
4. **Shodan/Censys需要API key** — 免费额度有限
5. **Google Dorking可能被限速** — 用代理或休息间隔
6. **社交工程需要授权** — 未授权的社会工程是违法的
7. **图片EXIF可能被清除** — 社交平台通常会去除EXIF
8. **waybackurls可能很大** — 需要过滤和去重
