#!/bin/bash
# 采集器看门狗脚本 — 通过cron每5分钟运行
# 进程数不足时自动重启

HOST="hz-server"
MIN_PROCESSES=50

COUNT=$(ssh $HOST "ps aux | grep main_v | grep -v grep | wc -l" 2>/dev/null)

if [ "$COUNT" -lt "$MIN_PROCESSES" ]; then
    echo "⚠️ 进程异常: 只有 $COUNT 个进程，正在重启..."
    ssh $HOST "kill -9 \$(ps aux | grep main_v | grep -v grep | awk '{print \$2}') 2>/dev/null"
    sleep 2
    ssh $HOST "cd /opt/collector && nohup python3 main_v4.py > /dev/null 2>&1 &"
    sleep 5
    NEW_COUNT=$(ssh $HOST "ps aux | grep main_v | grep -v grep | wc -l" 2>/dev/null)
    echo "✅ 重启完成: $NEW_COUNT 个进程"
else
    echo "✅ 正常: $COUNT 个进程运行中"
fi

# 汇报文件统计
FILES=$(ssh $HOST "find /opt/collector/data/docs -name '*.md' | wc -l" 2>/dev/null)
SIZE=$(ssh $HOST "du -sh /opt/collector/data/ | awk '{print \$1}'" 2>/dev/null)
echo "📊 文件: $FILES | 大小: $SIZE"
