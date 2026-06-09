---
name: cryptography-attacks
description: 密码学攻击 — 加密算法分析、侧信道、RSA攻击、哈希碰撞
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cryptography, rsa, aes, side-channel, hash-collision, crypto-attacks]
---

# 密码学攻击工具链

## 核心工具

| 工具 | 用途 |
|------|------|
| **SageMath** | 数学计算/密码分析 |
| **RsaCtfTool** | RSA自动化攻击 |
| **hashcat** | 哈希破解 |
| **CyberChef** | 编码/解码/加解密 |
| **openssl** | 命令行加密工具 |
| **hash_extender** | 哈希长度扩展攻击 |
| **PadBuster** | CBC Padding Oracle |
| **FeatherDuster** | 密码分析框架 |
| **Crypton** | 密码学挑战框架 |
| **pycryptodome** | Python密码学库 |
| **sagemath** | 数论/代数计算 |

---

## 1. RSA攻击

### 常见攻击场景
```
n = p * q (p和q相近) → Fermat分解
e很小(如3) → 直接开根
n可分解(小质数) → 直接分解
共模攻击(同n不同e) → 共模解密
低加密指数广播攻击(多条同明文) → CRT
dp泄露 → 计算p
d泄露 → 直接解密
Wiener攻击(大e小d) → 连分数
Boneh-Durfee(小d) → 格攻击
```

### SageMath RSA攻击
```python
# Fermat分解(p和q相近)
def fermat_factor(n):
    a = isqrt(n) + 1
    b2 = a*a - n
    while not is_square(b2):
        a += 1
        b2 = a*a - n
    return a - isqrt(b2), a + isqrt(b2)

p, q = fermat_factor(n)
phi = (p-1) * (q-1)
d = inverse_mod(e, phi)
m = pow(c, d, n)
print(long_to_bytes(m))

# 共模攻击(同n，不同e1,e2加密同一明文)
def common_modulus(n, e1, e2, c1, c2):
    g, s, t = xgcd(e1, e2)
    if s < 0: c1 = inverse_mod(c1, n)
    if t < 0: c2 = inverse_mod(c2, n)
    return (pow(c1, s, n) * pow(c2, t, n)) % n

# dp泄露(dp = d mod (p-1))
def dp_leak(dp, e, n, c):
    for k in range(1, e):
        p = (e * dp - 1) / k + 1
        if n % p == 0:
            q = n // p
            phi = (p-1)*(q-1)
            d = inverse_mod(e, phi)
            return long_to_bytes(pow(c, d, n))
    return None

# 低加密指数(e=3)
def low_e(c, e=3):
    m = Integer(c).nth_root(e)
    return long_to_bytes(int(m))
```

### RsaCtfTool
```bash
git clone https://github.com/RsaCtfTool/RsaCtfTool.git
cd RsaCtfTool && pip install -r requirements.txt

# 公钥解密
python RsaCtfTool.py --publickey pub.pem --private

# 已知n,e,c
python RsaCtfTool.py --publickey pub.pem --uncipherfile cipher.txt

# 自动尝试所有攻击
python RsaCtfTool.py --publickey pub.pem --attack auto
```

### openssl操作
```bash
# 查看公钥
openssl rsa -pubin -in pub.pem -text -noout

# 提取n和e
openssl rsa -pubin -in pub.pem -modulus -noout

# 私钥解密
openssl rsautl -decrypt -inkey priv.pem -in cipher.bin

# 生成私钥(已知p,q,e)
python3 -c "
from Crypto.PublicKey import RSA
import gmpy2
p,q,e = ...
n = p*q
phi = (p-1)*(q-1)
d = gmpy2.invert(e, phi)
key = RSA.construct((int(n), int(e), int(d), int(p), int(q)))
print(key.export_key().decode())
" > priv.pem
```

---

## 2. AES攻击

### Padding Oracle
```bash
# PadBuster
git clone https://github.com/AonCyberLabs/PadBuster.git

# 自动利用
perl padbuster.pl http://target.com/decrypt "encrypted_data" block_size -cookies="session=..."

# 解密
perl padbuster.pl http://target.com/decrypt "encrypted_data" 16 -decrypt

# 加密(伪造cookie)
perl padbuster.pl http://target.com/decrypt "encrypted_data" 16 -encrypt -plaintext '{"admin":1}'
```

### CBC字节翻转
```python
def cbc_bitflip(ciphertext_block, known_plaintext, desired_plaintext, block_size=16):
    """修改前一个密文块来改变明文"""
    ct = bytearray(ciphertext_block)
    for i in range(block_size):
        ct[i] ^= known_plaintext[i] ^ desired_plaintext[i]
    return bytes(ct)
```

### ECB模式攻击
```python
# ECB模式相同明文产生相同密文
# 逐字节暴力破解
def ecb_byte_at_a_time(oracle, block_size=16):
    known = b""
    for i in range(block_size):
        padding = b"A" * (block_size - 1 - i)
        target = oracle(padding)
        for c in range(256):
            test = oracle(padding + known + bytes([c]))
            if test[:len(padding) + i + 1] == target[:len(padding) + i + 1]:
                known += bytes([c])
                break
    return known
```

---

## 3. 哈希攻击

### 哈希长度扩展攻击
```bash
# hash_extender
git clone https://github.com/iagox86/hash_extender.git
cd hash_extender && make

# MD5长度扩展
./hash_extender -d "original_data" -s "known_hash" -a "appended_data" -f md5
./hash_extender -d "original_data" -s "known_hash" -a "appended_data" -f sha256

# Python版
pip install hashpumpy
import hashpumpy
new_hash, new_msg = hashpumpy.hashpump(original_hash, original_data, append_data, key_length)
```

### 哈希碰撞
```bash
# MD5碰撞
# fastcoll
git clone https://github.com/cr-marcstevens/hashclash.git
cd hashclash && make

# 生成两个相同MD5的文件
./fastcoll -p prefix.txt -o out1.txt out2.txt
md5sum out1.txt out2.txt  # MD5相同

# SHA1碰撞(已不安全)
# Google的SHAttered攻击
```

---

## 4. 编码/解码

### CyberChef (本地部署)
```bash
# 下载
wget https://github.com/gchq/CyberChef/releases/latest/download/CyberChef.zip
unzip CyberChef.zip
# 浏览器打开CyberChef.html

# 常用操作
# Base64编解码
# Hex编解码
# URL编解码
# JWT解码
# XOR加密/解密
# AES加解密
# RSA加解密
```

### 命令行编码
```bash
# Base64
echo -n "text" | base64
echo "dGV4dA==" | base64 -d

# Hex
echo -n "text" | xxd
echo "74657874" | xxd -r -p

# URL编码
python3 -c "import urllib.parse; print(urllib.parse.quote('text'))"

# JWT解码
echo "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.xxx" | cut -d. -f2 | base64 -d

# XOR
python3 -c "
import sys
key = b'key'
data = sys.stdin.buffer.read()
print(bytes(a ^ b for a, b in zip(data, key * (len(data)//len(key)+1))))
"
```

---

## 5. 侧信道攻击

### 时间侧信道
```python
import requests, time, string

def timing_attack(url, param, length=32):
    charset = string.ascii_letters + string.digits + "{}_"
    found = ""
    for i in range(length):
        max_time = 0
        best_char = ""
        for c in charset:
            test = found + c
            times = []
            for _ in range(5):
                start = time.time()
                requests.get(url, params={param: test})
                times.append(time.time() - start)
            avg = sum(times) / len(times)
            if avg > max_time:
                max_time = avg
                best_char = c
        found += best_char
        print(f"[{i}] {found}")
    return found
```

### 功耗侧信道
```bash
# ChipWhisperer
pip install chipwhisperer
# 需要硬件: ChipWhisperer Nano/Huskylens
```

---

## 6. XOR攻击

### 单字节XOR暴力
```python
def single_byte_xor(ciphertext):
    results = []
    for key in range(256):
        plaintext = bytes([b ^ key for b in ciphertext])
        score = sum(1 for b in plaintext if chr(b) in ' etaoinshrdlcumwfgypbvkjxqz')
        results.append((score, key, plaintext))
    results.sort(reverse=True)
    return results[0]

# 重用密钥XOR
def repeating_key_xor(ciphertext, key):
    return bytes(a ^ b for a, b in zip(ciphertext, key * (len(ciphertext)//len(key)+1)))
```

### 已知明文攻击
```python
# 如果知道部分明文
key = bytes(a ^ b for a, b in zip(ciphertext[:len(known_plaintext)], known_plaintext))
```

---

## 7. CTF密码学常用

### 维吉尼亚密码
```python
def vigenere_decrypt(ciphertext, key):
    result = []
    key_len = len(key)
    for i, c in enumerate(ciphertext):
        if c.isalpha():
            shift = ord(key[i % key_len].lower()) - ord('a')
            result.append(chr((ord(c.lower()) - ord('a') - shift) % 26 + ord('a')))
        else:
            result.append(c)
    return ''.join(result)
```

### 仿射密码
```python
def affine_decrypt(ciphertext, a, b):
    a_inv = pow(a, -1, 26)
    return ''.join(
        chr((a_inv * (ord(c) - ord('a') - b)) % 26 + ord('a'))
        if c.isalpha() else c for c in ciphertext
    )
```

### 格基约减(LLL)
```python
# SageMath中使用LLL
from sage.all import *

def attack_lattice(matrix):
    M = Matrix(ZZ, matrix)
    reduced = M.LLL()
    return reduced

# 部分密钥泄露
# knapsack/背包密码
# hidden number problem
```

---

## Pitfalls

1. **RSA的n太小可直接分解** — 用factordb.com查
2. **AES的IV是全0** — 可能是ECB模式伪装
3. **Padding Oracle需要区分错误** — 400 vs 500 vs 自定义错误
4. **哈希长度扩展不适用于HMAC** — HMAC的结构不同
5. **MD5已不安全** — 可在数秒内碰撞
6. **SHA1已不安全** — Google已实际碰撞
7. **SHA256目前安全** — 但不应用于密码存储(用bcrypt/argon2)
8. **随机数生成很重要** — 弱随机数=密码学崩塌
