# 库街区(Kurobbs) API参考

## 基础信息
- 域名: `api.kurobbs.com`
- Token格式: JWT (`eyJ`开头)
- Token有效期: 7-30天

## 关键API

### sdkLogin (登录)
```
POST https://api.kurobbs.com/user/sdkLogin
Content-Type: application/json
Body: {mobile, verifyCode, devId, ...}
Response: {"code":200, "data":{"token":"eyJ..."}}
```

### sendSms (发送验证码)
```
POST https://api.kurobbs.com/user/sendSms
Content-Type: application/json
需要内部访问令牌(APP内置)
Body: {"mobile":"手机号"}
Response: 无内部令牌时返回 {"code":220,"msg":"访问令牌不能为空"}
```

## Token获取方案

### 代理拦截方案
- 脚本: `/tmp/kuro_token_v3.js`
- 原理: 反向代理kurobbs.com，注入JS拦截`sdkLogin`响应
- 自动保存Token到青龙`KURO_TOKEN`
- 需gzip解压CDN响应

### 抓包方案
- ProxyPin/PCAPdroid抓取`sdkLogin`请求
- 响应`data.token`即为KURO_TOKEN

## 签到接口
- 签到需要`KURO_TOKEN`环境变量
- 具体签到API需抓包确认
