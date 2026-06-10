#!/bin/bash
# Watchdog script for multi-process Python worker
# Deploy via Hermes cron: no_agent=True, script="collector/watchdog.sh"
# Schedule: */5 * * * * (every 5 minutes)

HOST="hz-server"           # SSH alias
PROCESS_NAME="main_v4"     # Process name to monitor
MIN_PROCESSES=20           # Minimum expected processes
RESTART_CMD="cd /opt/collector && nohup python3 main_v4.py > /dev/null 2>&1 &"

# Check process count
COUNT=$(ssh -o ConnectTimeout=5 $HOST "ps aux | grep $PROCESS_NAME | grep -v grep | wc -l" 2>/dev/null)

if [ -z "$COUNT" ] || [ "$COUNT" -eq 0 ]; then
    echo "❌ 进程不存在，正在重启..."
    ssh -o ConnectTimeout=5 $HOST "pkill -f $PROCESS_NAME 2>/dev/null; $RESTART_CMD"
    sleep 3
    NEW=$(ssh -o ConnectTimeout=5 $HOST "ps aux | grep $PROCESS_NAME | grep -v grep | wc -l" 2>/dev/null)
    echo "✅ 重启完成: $NEW 个进程"
elif [ "$COUNT" -lt "$MIN_PROCESSES" ]; then
    echo "⚠️ 进程不足: $COUNT/$MIN_PROCESSES，正在重启..."
    ssh -o ConnectTimeout=5 $HOST "pkill -f $PROCESS_NAME 2>/dev/null; $RESTART_CMD"
    sleep 3
    NEW=$(ssh -o ConnectTimeout=5 $HOST "ps aux | grep $PROCESS_NAME | grep -v grep | wc -l" 2>/dev/null)
    echo "✅ 重启完成: $NEW 个进程"
else
    echo "✅ 正常: $COUNT 个进程运行中"
fi

# Status report
FILES=$(ssh -o ConnectTimeout=5 $HOST "find /opt/collector/data/docs -name '*.md' 2>/dev/null | wc -l" 2>/dev/null)
SIZE=$(ssh -o ConnectTimeout=5 $HOST "du -sh /opt/collector/data/ 2>/dev/null | awk '{print \$1}'" 2>/dev/null)
echo "📊 文件: ${FILES:-?} | 大小: ${SIZE:-?}"
