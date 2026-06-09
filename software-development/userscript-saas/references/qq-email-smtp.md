# QQ邮箱 SMTP 配置（发送验证码邮件）

## 获取授权码

1. 登录 QQ邮箱网页版 (mail.qq.com)
2. 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
3. 开启 SMTP 服务
4. 按提示发送短信验证
5. 获取16位授权码（不是QQ密码！）

## Flask 集成代码

```python
import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 465
SMTP_USER = '你的QQ号@qq.com'
SMTP_PASS = '16位授权码'

def send_email(to_addr, subject, body):
    try:
        smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        smtp.login(SMTP_USER, SMTP_PASS)
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = to_addr
        smtp.sendmail(SMTP_USER, [to_addr], msg.as_string())
        smtp.quit()
        return True
    except Exception as e:
        print(f'发送邮件失败: {e}')
        return False
```

## 验证码流程

```python
import random, string
from datetime import datetime, timedelta

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json.get('email', '').strip()
    
    # 生成6位验证码
    code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.now() + timedelta(minutes=10)
    
    # 存入数据库
    conn.execute("INSERT INTO password_resets(email, code, expires_at) VALUES(?, ?, ?)",
                 (email, code, expires_at.isoformat()))
    conn.commit()
    
    # 发送邮件（不要返回code到前端！）
    body = f'【您的应用名】验证码：{code}，10分钟有效。'
    if send_email(email, '验证码', body):
        return jsonify({'message': '验证码已发送'})
    else:
        return jsonify({'error': '发送失败'}), 500
```

## 其他SMTP服务器

| 服务器 | SMTP地址 | 端口 | 备注 |
|--------|----------|------|------|
| QQ邮箱 | smtp.qq.com | 465 (SSL) | 最常用 |
| 163邮箱 | smtp.163.com | 465 (SSL) | 也需授权码 |
| Gmail | smtp.gmail.com | 587 (TLS) | 需应用专用密码 |
| Outlook | smtp.office365.com | 587 (TLS) | 需开启SMTP |

## 测试

```python
# 测试SMTP连接
import smtplib
smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)
smtp.login('QQ号@qq.com', '授权码')
print('SMTP连接成功！')
smtp.quit()
```

## 常见错误

- `535 Error: authentication failed` → 授权码错误，重新生成
- `Connection refused` → 端口错误，QQ邮箱用465
- `smtplib.SMTPSenderRefused` → 发件人地址和登录账号不一致
