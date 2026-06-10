---
name: multi-process-scraper
description: Build high-throughput multi-process Python scrapers/collectors for small servers
tags: [python, scraper, multiprocessing, web-scraping, data-collection]
triggers:
  - building a web scraper or data collector
  - need to scrape many URLs in parallel
  - multi-process Python scraping
  - collector architecture
---

# Multi-Process Python Scraper / Collector Architecture

Build high-throughput data collectors that maximize CPU/network utilization on small servers (2C2G+).

## When to Use
- Scraping 100+ URLs with multiple data sources
- Need continuous collection over hours (not one-shot)
- Server has idle CPU/network you want to saturate
- Single-threaded scraper is too slow

## Architecture (v4.0 pattern)

```
main.py
├── worker_type_A × N  (e.g. 10 trending scrapers)
├── worker_type_B × N  (e.g. 10 search scrapers)
├── worker_type_C × N  (e.g. 10 docs scrapers)
└── watchdog.sh         (cron, auto-restart)
```

Each worker is an independent `Process` with its own:
- Session (requests.Session)
- Seen set (URL + content hashes, saved to JSON)
- Log file (collector_{name}.log)

## Key Design Decisions

### 1. Shared State: Manager.Value for counter only
```python
manager = Manager()
counter = manager.Value('i', 0)  # shared atomic counter
lock = manager.Lock()
stop = manager.Event()
```
Do NOT use `Manager.list()` or `Manager.set()` for seen-URLs — they're slow (proxy overhead on every `.add()`). Each process maintains its own local `set()` and saves to its own JSON file.

### 2. Per-Process Dedup (NOT global)
```python
process_seen = {}  # {name: {"urls": set(), "contents": set()}}

def collect(url, ...):
    uh = url_hash(url)
    if uh in process_seen[name]["urls"]:
        return False
    process_seen[name]["urls"].add(uh)
    # ... fetch and save ...
```
Cross-process dedup is optional (check other processes' seen files) but adds complexity. Per-process dedup is fast and sufficient — duplicate files are cheap.

### 3. Work Distribution
Split work across N identical workers by PID modulo:
```python
# 4 docs workers share 17 URLs
batch = TECH_DOCS[pid::4]  # worker 0 gets [0,4,8,12], worker 1 gets [1,5,9,13], ...
```
For search/trending: each worker picks random topics independently.

### 4. Sleep Loop (not cron)
```python
while not stop.is_set():
    do_work()
    save_seen()
    for _ in range(60):  # 60 seconds between rounds
        if stop.is_set(): break
        time.sleep(1)
```
Check `stop` every second so SIGTERM is responsive.

### 5. requests Library Handles Gzip Automatically
```python
# WRONG — causes BadGzipFile on API responses
if resp.headers.get("Content-Encoding") == "gzip":
    content = gzip.decompress(resp.content).decode()

# RIGHT — just use resp.text
content = resp.text
```

## Watchdog Pattern

```bash
#!/bin/bash
# collector/watchdog.sh — run via cron every 5 min
HOST="hz-server"
MIN_PROCESSES=20
COUNT=$(ssh $HOST "ps aux | grep main_v | grep -v grep | wc -l")
if [ "$COUNT" -lt "$MIN_PROCESSES" ]; then
    ssh $HOST "kill -9 \$(ps aux | grep main_v | grep awk...) 2>/dev/null"
    ssh $HOST "cd /opt/collector && nohup python3 main_v4.py > /dev/null 2>&1 &"
fi
```

Cron job setup:
```python
cronjob(action='create', no_agent=True, script='collector/watchdog.sh', schedule='*/5 * * * *')
```

## Scaling Guide

| Server | Processes | Threads/proc | Expected throughput |
|--------|-----------|-------------|-------------------|
| 2C2G   | 20        | 4           | ~200 files/hour   |
| 2C4G   | 50        | 4           | ~500 files/hour   |
| 4C8G   | 100       | 8           | ~2000 files/hour  |

Memory per process: ~25-40MB. Keep total < 80% of RAM.

**⚠️ CRITICAL: Do NOT exceed the table above.** 100 processes on 2C2G will crash the server completely — SSH becomes unreachable, requiring a hard reboot via cloud console. Always start conservative (20) and scale up only after confirming memory headroom.

## Size Monitoring Pattern

Track data growth and notify at intervals (e.g. every 100MB). Use a state file to remember the last checkpoint:

```bash
#!/bin/bash
# collector/size_monitor.sh — run via cron every 5 min
STATE_FILE="/tmp/collector_size_state"
CURRENT=$(ssh hz-server "du -sm /opt/collector/data/ | awk '{print \$1}'" 2>/dev/null)
LAST=0
[ -f "$STATE_FILE" ] && LAST=$(cat "$STATE_FILE")
DIFF=$((CURRENT - LAST))
if [ $DIFF -ge 100 ]; then
    echo "$CURRENT" > "$STATE_FILE"
    echo "📊 采集进度: ${CURRENT}MB / 1000MB"
fi
# Empty output = silent (no notification)
```

## Silent Watchdog Pattern

The watchdog should ONLY output when something is wrong. In `no_agent` cron mode, empty stdout = no message sent to user.

```bash
#!/bin/bash
# collector/watchdog.sh — only outputs on failure
HOST="hz-server"
MIN_PROCESSES=20
COUNT=$(ssh -o ConnectTimeout=5 $HOST "ps aux | grep main_v | grep -v grep | wc -l" 2>/dev/null)
if [ -z "$COUNT" ] || [ "$COUNT" -lt "$MIN_PROCESSES" ]; then
    echo "⚠️ 进程异常: $COUNT 个，正在重启..."
    ssh $HOST "kill -9 \$(ps aux | grep main_v | grep -v grep | awk '{print \$2}') 2>/dev/null"
    ssh $HOST "cd /opt/collector && nohup python3 main_v4.py > /dev/null 2>&1 &"
    sleep 3
    NEW=$(ssh $HOST "ps aux | grep main_v | grep -v grep | wc -l" 2>/dev/null)
    echo "✅ 已重启: $NEW 个进程"
fi
```

Setup with no_agent cron (no token consumption):
```python
cronjob(action='create', no_agent=True, script='collector/watchdog.sh', schedule='*/5 * * * *')
```

## Pitfalls

1. **GitHub API rate limit**: 60 req/hour unauthenticated. Space requests 2+ seconds apart.
2. **`Manager.list().add()` is SLOW**: Use per-process local sets, not shared proxies.
3. **gzip double-decode**: requests handles it. Don't manually decompress.
4. **Process zombies on kill**: Use `stop_event.set()` + `join(timeout=10)` before `terminate()`.
5. **Log file explosion**: Each process writes its own log. Rotate or truncate periodically.
6. **⚠️ Server crash from too many processes**: 100 processes on 2C2G exhausted all memory + swap, making SSH unreachable. Had to reboot via Alibaba Cloud console. Safe limit: 20-30 on 2C2G.
7. **User preference: silent monitoring**: Don't report normal watchdog status. Only notify on failures or milestones (size thresholds).

## References
- See `references/collector-v4.py` for the full working v4.0 code (50-process version)
- See `references/watchdog.sh` for the watchdog script
