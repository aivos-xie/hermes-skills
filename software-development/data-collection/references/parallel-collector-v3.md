# Parallel Collector v3.0 — Full Working Example

## Architecture

```
main_v3.py (主进程)
├── process_trending()      # GitHub Trending, 每小时刷新
├── process_github_search() # GitHub API搜索, 每30分钟
├── process_tech_docs()     # 技术文档, 每2小时
├── process_tech_blogs()    # 技术博客, 每30分钟
└── process_discovery()     # 链接发现, 每15分钟
```

Each process:
- Has its own `seen_<name>.json` file for dedup
- Uses `ThreadPoolExecutor(max_workers=4)` for concurrent requests
- Saves state every 50 items
- Responds to `stop_event` for graceful shutdown

Shared state:
- `Manager().Value('i', 0)` — atomic counter with Lock
- `Manager().Lock()` — for counter updates
- `Manager().Event()` — stop signal

## Key Code Patterns

### Per-Process State
```python
process_seen_urls = {}
process_seen_contents = {}

def init_process_seen(process_name):
    seen_file = BASE_DIR / f"seen_{process_name}.json"
    if seen_file.exists():
        data = json.loads(seen_file.read_text())
        process_seen_urls[process_name] = set(data.get("urls", []))
        process_seen_contents[process_name] = set(data.get("contents", []))
    else:
        process_seen_urls[process_name] = set()
        process_seen_contents[process_name] = set()
```

### Cross-Process Dedup Check
```python
def collect_and_save(session, url, category, source, shared_counter, lock, process_name):
    uh = url_hash(url)
    
    # Check own process seen
    if uh in process_seen_urls.get(process_name, set()):
        return False
    
    # Optional: check other processes' seen files
    for other_name in process_seen_urls:
        if other_name != process_name and uh in process_seen_urls[other_name]:
            return False
    
    process_seen_urls.setdefault(process_name, set()).add(uh)
    # ... fetch and save
```

### Sleep with Interrupt Check
```python
# Instead of time.sleep(3600) which blocks for 1 hour
for _ in range(3600):
    if stop_event.is_set():
        break
    time.sleep(1)
```

## Data Sources Used

| Source | Refresh | Items/Round |
|--------|---------|-------------|
| GitHub Trending | 1 hour | ~90 repos (9 languages × 10) |
| GitHub API Search | 30 min | ~50 repos (5 topics × 10) |
| Tech Docs | 2 hours | 17 docs |
| Tech Blogs | 30 min | ~100 articles |
| Link Discovery | 15 min | ~100 links |

## Results (from production run)

- 5 processes, 7 total (main + 5 workers + monitor)
- ~140 files collected in first 20 minutes
- 71 categories
- 18M total size
- Processes stable at ~2% memory each

## Lessons Learned

1. **Don't use Manager().list()** — ListProxy doesn't have .add()
2. **Don't manually decompress gzip** — requests handles it via resp.text
3. **URL exhaustion is real** — need dynamic discovery + multiple sources
4. **Per-process state files** — better than shared state for high-throughput
5. **Sleep with interrupt check** — don't block for hours in sleep()
