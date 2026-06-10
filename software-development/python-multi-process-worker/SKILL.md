---
name: python-multi-process-worker
description: Build and deploy multi-process Python workers on remote servers — parallel data collection, web scraping, batch processing with shared state management.
tags: [python, multiprocessing, parallel, worker, collector, scraper]
triggers:
  - multi-process Python worker
  - parallel data collection
  - batch scraping with multiprocessing
  - Process + Manager pattern
  - worker process orchestration
---

# Multi-Process Python Worker Pattern

Build robust parallel workers using Python's `multiprocessing` module with proper shared state, watchdog monitoring, and safe resource limits.

## Architecture

```
main.py (orchestrator)
├── worker_type_1 × N (processes)
├── worker_type_2 × N
├── worker_type_3 × N
└── shared: Manager().Value, Manager().Lock, Manager().Event
```

## Core Pattern

```python
from multiprocessing import Process, Manager, Value

def worker(pid, counter, lock, stop_event):
    """Each worker has independent seen set for dedup"""
    seen = set()
    while not stop_event.is_set():
        # do work
        with lock:
            counter.value += 1
        # sleep between rounds
        for _ in range(60):
            if stop_event.is_set(): break
            time.sleep(1)

def main():
    manager = Manager()
    counter = manager.Value('i', 0)
    lock = manager.Lock()
    stop = manager.Event()
    
    procs = []
    for i in range(NUM_WORKERS):
        p = Process(target=worker, args=(i, counter, lock, stop))
        p.start()
        procs.append(p)
    
    signal.signal(signal.SIGTERM, lambda s,f: (stop.set(), [p.join() for p in procs], sys.exit(0)))
    
    # main loop
    while time.time() - start < DURATION:
        time.sleep(300)  # periodic status save
    stop.set()
```

## Process Count Guidelines (CRITICAL)

**2G RAM server: MAX 20-25 processes**
**4G RAM server: MAX 50 processes**
**8G RAM server: MAX 100 processes**

⚠️ **PITFALL: Too many processes (100+) on 2G server = SSH lockout, server unresponsive.**
Each Python process uses ~20-40MB RAM. 100 processes = 2-4GB, leaving nothing for OS/SSH.

## Shared State Options

### Option 1: Manager().Value + Lock (Recommended)
- Best for simple counters
- Atomic updates with lock
- Low overhead

### Option 2: Per-process seen files
- Each process maintains its own `seen_{name}.json`
- No cross-process locking for dedup
- Load on init, save periodically

### Option 3: Manager().list() / Manager().dict()
- ⚠️ **PITFALL: `ListProxy` has no `.add()` method** — use regular `set()` operations only with `Manager().set()` or use per-process local sets
- Higher overhead than Value+Lock

## Watchdog Pattern

```bash
#!/bin/bash
# Run via cron every 5 minutes
# IMPORTANT: Only output on failure. Empty stdout = silent (no_user_notification in no_agent mode)
HOST="hz-server"
MIN_PROCESSES=20

COUNT=$(ssh -o ConnectTimeout=5 $HOST "ps aux | grep worker_main | grep -v grep | wc -l" 2>/dev/null)

if [ -z "$COUNT" ] || [ "$COUNT" -lt "$MIN_PROCESSES" ]; then
    echo "⚠️ Only $COUNT processes, restarting..."
    ssh $HOST "pkill -f worker_main; cd /app && nohup python3 main.py > /dev/null 2>&1 &"
fi
# Normal: no output = no notification sent to user
```

Deploy via Hermes cron with `no_agent=True, script="watchdog.sh"`.
User preference: don't report normal watchdog status. Only alert on failures or milestones.

## Pitfalls

1. **requests + gzip**: `requests` library auto-decompresses gzip. Do NOT manually `gzip.decompress(resp.content)` — causes `BadGzipFile` error. Just use `resp.text`.

2. **Manager().list() `.add()` error**: `ListProxy` doesn't support `.add()`. Use per-process local sets or `Manager().set()`.

3. **Process count vs RAM**: Each process ~20-40MB. Formula: `safe_count = (available_RAM_MB - 500) / 30`. Always leave 500MB for OS.

4. **SSH lockout**: If too many processes exhaust RAM, SSH becomes unreachable. Only fix is server restart via cloud console.

5. **Seen file persistence**: Save seen state periodically (every N items or every 5 min), not on every collect. Disk I/O becomes bottleneck otherwise.

6. **GitHub API rate limiting**: Without auth token, rate limit is 60 req/hour. Add `?token=xxx` or use `Authorization` header.

7. **Batch distribution**: When N processes share a work list, use `list[pid::N]` to distribute evenly without coordination.

## References

- See `references/collector-v4-architecture.md` for the full collector implementation details
