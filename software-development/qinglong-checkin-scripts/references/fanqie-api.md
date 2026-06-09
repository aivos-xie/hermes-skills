# 番茄小说 API 详情

## 平台信息
- 开发商: 字节跳动 (ByteDance)
- APP包名: com.dragon.read
- APP ID (aid): 1967

## API域名（多个备用）
- https://api5-normal-sinfonlineb.fqnovel.com
- https://api3-normal-c-hl.amemv.com
- https://novel.snssdk.com
- https://reading.snssdk.com

## 签到接口
```
POST /reading/bookapi/v1/user_sign/v1
参数: iid, device_id, aid=1967, app_name=novel, device_platform=android
Cookie: install_id=xxx;passport_csrf_token=xxx
```

## 模拟阅读上报
```
POST /reading/bookapi/v1/behavior/report_read_time
Body: time=<秒数>
建议: 分3-6次上报，每次300-600秒，模拟真实阅读
```

## 领取阅读金币
```
POST /reading/bookapi/v1/coin/receive
```

## 查询用户信息
```
GET /reading/bookapi/v1/user/info
```

## 查询签到状态
```
GET /reading/bookapi/v1/sign_in/query
```

## 请求头
```
User-Agent: com.dragon.read/320 (Linux; U; Android 11; zh_CN; MI 12; Build/RKQ1.200826.002)
Content-Type: application/x-www-form-urlencoded
```

## Cookie获取方法
1. 安装 HttpCanary (Android免root)
2. 启动抓包 -> 打开番茄小说 -> 手动签到
3. 找到 fqnovel.com 的请求
4. 复制 Cookie 头中的 install_id 和 passport_csrf_token

## 注意事项
- Token有效期约1-2个月
- 阅读时长不要一次上报太多(最多60分钟)
- IP风控: 住宅IP安全，VPS IP可能触发验证
- 每日签到1次即可，不要频繁调用
