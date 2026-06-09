# 番茄小说API参考

## 签到接口

### POST 签到
```
URL: https://fanqienovel.com/api/reader/sign_in
Method: POST
Content-Type: application/json
```

### GET 查询签到状态
```
URL: https://fanqienovel.com/api/reader/sign_in/query
Method: GET
```

## 认证方式

网页端使用Cookie认证，关键字段：
- `sessionid` — 会话ID，登录后自动生成
- `novel_web_id` — 用户标识
- `ttwid` — 字节跳动通用设备ID

## Headers

```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
Referer: https://fanqienovel.com/
Cookie: sessionid=xxx; novel_web_id=xxx; ttwid=xxx
```

## APP端接口（需要签名，不推荐）

```
URL: https://api-access.fanqienovel.com/reading/sign_in/sign_in
Method: POST
认证: 设备Token + Cookie + X-Bogus签名
```

APP端需要 `X-Bogus` 签名参数（字节系特征），逆向难度大。网页端不需要。

## Cookie获取方式

### 手机端
1. Alook浏览器打开 fanqienovel.com，登录后查看开发者工具→Cookies
2. 或使用抓包工具（HttpCanary、Stream）

### 电脑端
1. 浏览器打开 fanqienovel.com，登录
2. F12 → Application → Cookies → fanqienovel.com
3. 复制 sessionid, novel_web_id, ttwid

## 已知开源项目

| 项目 | Stars | 说明 |
|------|-------|------|
| fanqie_auto_publish | 195 | 自动发布（Playwright） |
| Fanqie-novel-Downloader | 1064 | 小说下载器 |
| fanqie-novel-download | 421 | Python下载实现 |
| fanqie-downloader-api-v4 | 18 | 下载API（Docker） |

签到专用开源项目较少，大部分是下载/发布类。

## 注意事项

- Cookie有效期约数周，过期需重新获取
- 每日签到一次，重复签到返回"已签到"
- 字节系API路径可能更新，需关注变化
- 网页端风控较松，APP端有X-Bogus签名保护
