# GitHub 双仓库同步模式

## 架构

| 仓库 | 可见性 | 内容 |
|------|--------|------|
| `hermes-skills` | 公开 | 所有技能文件，按类别分类 |
| `hermes-memory` | 私有 | 记忆文件（去除敏感信息）+ 更新日志 |

## 敏感信息过滤规则

以下内容必须替换为 `[REDACTED]`：
- API Key、Token、密码
- 手机号、邮箱地址
- 服务器 IP、登录凭据
- Cookie 值
- 私人 URL（localhost、内网 IP）

## 同步脚本

位于 `/home/admin/.hermes/scripts/sync_to_github.py`

## 定时任务

每天凌晨 2 点自动执行（cron job ID: `c0492caadcab`）

## 日志

记忆更新日志保存在 `~/.hermes/memory-repo/update.log`
格式：`[时间戳] Memory updated`
