---
name: digital-forensics
description: 数字取证 — 磁盘/内存/网络取证、日志分析、时间线重建
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [forensics, disk, memory, network, log-analysis, timeline, autopsy, volatility]
---

# 数字取证工具链

## 核心工具

| 工具 | 用途 |
|------|------|
| **Autopsy** | 磁盘取证框架(GUI) |
| **The Sleuth Kit (TSK)** | 命令行磁盘取证 |
| **Volatility** | 内存取证 |
| **Wireshark/tshark** | 网络取证 |
| **plaso/log2timeline** | 日志时间线分析 |
| **bulk_extractor** | 批量数据提取 |
| **Binwalk** | 固件/嵌入文件分析 |
| **foremost** | 文件恢复 |
| **testdisk** | 分区恢复 |
| **exiftool** | 元数据提取 |
| **Guymager** | 磁盘镜像 |
| **dc3dd** | 安全磁盘镜像 |
| **AFF4** | 取证镜像格式 |
| **ELK Stack** | 日志分析平台 |
| **Chainsaw** | Windows事件日志分析 |
| **Eric Zimmerman工具** | Windows取证 |
| **KAPE** | Windows取证采集 |

---

## 1. 磁盘取证

### 创建镜像
```bash
# dd
sudo dd if=/dev/sda of=disk.img bs=4M status=progress

# dc3dd(带哈希)
sudo dc3dd if=/dev/sda of=disk.img hash=sha256 log=hash.log

# Guymager(GUI)
guymager &

# 验证镜像
md5sum /dev/sda
md5sum disk.img
```

### The Sleuth Kit (TSK)
```bash
sudo apt install sleuthkit

# 查看分区
mmls disk.img

# 查看文件系统
fsstat -o 2048 disk.img

# 列出文件
fls -o 2048 disk.img            # 已删除的标*
fls -r -o 2048 disk.img         # 递归

# 提取文件
icat -o 2048 disk.img 1234 > extracted_file

# 恢复删除文件
fls -d -o 2048 disk.img         # 列出已删除
icat -o 2048 disk.img inode > recovered.file

# 时间线
mactime -b disk.img -d > timeline.csv

# 搜索文件
tsk_loaddisk -i raw disk.img
```

### Autopsy (GUI)
```bash
sudo apt install autopsy
autopsy &
# 浏览器打开 http://localhost:9999/autopsy
# 1. 创建Case
# 2. 添加数据源(镜像文件)
# 3. 分析: 文件浏览、关键词搜索、时间线、哈希匹配
```

---

## 2. 内存取证

### Volatility 3
```bash
# 安装
pip install volatility3

# 识别系统
vol -f memory.dmp windows.info

# 进程列表
vol -f memory.dmp windows.pslist
vol -f memory.dmp windows.pstree

# 网络连接
vol -f memory.dmp windows.netscan

# 命令行历史
vol -f memory.dmp windows.cmdline

# 注册表
vol -f memory.dmp windows.registry.hivelist
vol -f memory.dmp windows.registry.userassist

# DLL列表
vol -f memory.dmp windows.dlllist

# 文件列表
vol -f memory.dmp windows.filescan
vol -f memory.dmp windows.dumpfiles -Q 0x12345 -D output/

# 提取进程
vol -f memory.dmp windows.memmap -p 1234 --dump

# 恶意软件检测
vol -f memory.dmp windows.malfind

# 驱动列表
vol -f memory.dmp windows.modules
vol -f memory.dmp windows.modscan

# SSDT钩子检测
vol -f memory.dmp windows.ssdt

# 服务列表
vol -f memory.dmp windows.svcscan

# 计划任务
vol -f memory.dmp windows.tasks
```

### Linux内存取证
```bash
vol -f memory.dmp linux.pslist
vol -f memory.dmp linux.bash
vol -f memory.dmp linux.check_syscall
vol -f memory.dmp linux.proc_maps
```

---

## 3. 网络取证

### Wireshark/tshark
```bash
sudo apt install wireshark tshark

# 读取pcap
tshark -r capture.pcap

# 过滤HTTP
tshark -r capture.pcap -Y "http.request"
tshark -r capture.pcap -Y "http.request.full_uri"

# 过滤DNS
tshark -r capture.pcap -Y "dns"

# 过滤特定IP
tshark -r capture.pcap -Y "ip.addr == 192.168.1.100"

# 提取文件
tshark -r capture.pcap --export-objects http,output_dir/
tshark -r capture.pcap --export-objects smb,output_dir/
tshark -r capture.pcap --export-objects imf,output_dir/

# TCP流重组
tshark -r capture.pcap -z "follow,tcp,ascii,0"

# 统计
tshark -r capture.pcap -z "conv,tcp"
tshark -r capture.pcap -z "io,stat,1"

# 导出
tshark -r capture.pcap -Y "http" -Tfields -e http.host -e http.request.uri
```

### 网络流量分析流程
```
1. 统计概览: endpoints, protocols, conversations
2. DNS查询: 找恶意域名
3. HTTP请求: 找C2通信、数据外泄
4. 文件提取: 从流量中恢复传输的文件
5. 异常检测: 非常规端口、长连接、大量数据传输
```

---

## 4. 日志分析

### plaso/log2timeline
```bash
sudo apt install plaso

# 创建时间线
log2timeline.py timeline.plaso disk.img

# 导出为CSV
psort.py -o l2tcsv timeline.plaso -w timeline.csv

# 过滤时间范围
psort.py timeline.plaso "date > '2024-01-01' AND date < '2024-01-31'"

# 输出格式
psort.py -o json timeline.plaso -w timeline.json
```

### Chainsaw (Windows日志)
```bash
# 安装
git clone https://github.com/WithSecureLabs/chainsaw.git

# 分析EVTX日志
chainsaw hunt evtx_logs/ -s sigma_rules/ --csv --output results/

# 搜索关键词
chainsaw search "mimikatz" evtx_logs/
chainsaw search "powershell" evtx_logs/
```

### Linux日志
```bash
# 系统日志
cat /var/log/syslog
cat /var/log/auth.log
cat /var/log/kern.log

# 登录记录
last -f /var/log/wtmp
lastb -f /var/log/btmp
who /var/log/wtmp

# SSH日志
grep "sshd" /var/log/auth.log
grep "Failed password" /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -rn

# Web日志
cat /var/log/apache2/access.log
cat /var/log/nginx/access.log

# 命令历史
cat ~/.bash_history
cat /root/.bash_history
```

### Windows事件日志
```powershell
# 导出事件日志
wevtutil epl Security security.evtx
wevtutil epl System system.evtx
wevtutil epl Application application.evtx

# PowerShell查询
Get-WinEvent -LogName Security -FilterXPath "*[System[EventID=4624]]" | Select-Object -First 10
Get-WinEvent -LogName Security -FilterXPath "*[System[EventID=4625]]"  # 登录失败

# 关键事件ID
4624 - 登录成功
4625 - 登录失败
4672 - 特权分配
4688 - 进程创建
4720 - 账户创建
4732 - 组成员变更
1102 - 日志清除
```

---

## 5. 文件恢复

### foremost
```bash
sudo apt install foremost

# 恢复所有文件类型
foremost -i disk.img -o output/

# 指定文件类型
foremost -t jpg,png,pdf -i disk.img -o output/

# 从原始设备
foremost -i /dev/sdb -o /tmp/recovered/
```

### testdisk
```bash
sudo apt install testdisk

# 恢复分区
testdisk disk.img

# 恢复文件
photorec disk.img
```

---

## 6. 元数据分析

### exiftool
```bash
sudo apt install libimage-exiftool-perl

# 查看元数据
exiftool image.jpg
exiftool document.pdf
exiftool video.mp4

# 提取GPS坐标
exiftool -GPSLatitude -GPSLongitude image.jpg

# 提取所有文件的元数据
exiftool -r /path/to/directory/

# 移除元数据
exiftool -all= image.jpg
```

### 从图片提取信息
```bash
# 隐写分析
steghide extract -sf image.jpg
stegsolve image.png

# strings
strings image.jpg | grep -i "flag\|password\|key"

# binwalk
binwalk -e image.png
```

---

## 7. 时间线分析

### 创建综合时间线
```bash
# 从磁盘镜像
log2timeline.py timeline.plaso disk.img
psort.py timeline.plaso -o l2tcsv -w timeline.csv

# 从内存
vol -f memory.dmp timeliner

# 合并多源
psort.py timeline1.plaso timeline2.plaso -o l2tcsv -w combined.csv

# 可视化
# 导入到Excel/Tableau/ELK
```

### 时间线分析要点
```
1. 事件发生的顺序
2. 恶意软件首次出现的时间
3. 横向移动路径
4. 数据外泄时间点
5. 日志是否有被清除的迹象
6. 文件创建/修改/访问时间
7. 注册表修改时间
8. 网络连接时间线
```

---

## 8. 云/容器取证

### Docker取证
```bash
# 导出容器文件系统
docker export container_id > container.tar

# 查看容器日志
docker logs container_id

# 检查容器进程
docker top container_id

# 容器镜像检查
docker inspect image_name
docker history image_name

# 文件系统差异
docker diff container_id
```

### AWS取证
```bash
# EBS快照
aws ec2 create-snapshot --volume-id vol-xxx

# CloudTrail日志
aws logs filter-log-events --log-group-name CloudTrail

# S3访问日志
aws s3api get-bucket-logging --bucket my-bucket
```

---

## Pitfalls

1. **先创建镜像再分析** — 永远不要在原始证据上操作
2. **验证哈希** — 镜像前后MD5/SHA256必须一致
3. **Volatility profile要匹配** — 不同OS需要不同profile
4. **时间戳注意时区** — UTC vs 本地时间
5. **内存易失** — 先采集内存再关机
6. **加密磁盘** — BitLocker/LUKS需要先解密
7. **日志可能被清除** — 检查1102事件(日志清除)
8. **云取证需要权限** — 需要云服务商配合
