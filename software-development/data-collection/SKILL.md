---
name: data-collection
description: "Parallel data collection from web sources, APIs, and documentation sites"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [data-collection, web-scraping, parallel-processing, python, multiprocessing]
    related_skills: [web-tool-builder, flask-web-tools, coding-principles]
triggers:
  - data collection
  - web scraping
  - crawl
  - 采集
  - 爬虫
  - parallel collection
---

# Data Collection Patterns

Reusable patterns for collecting data from web sources, APIs, and documentation sites. Optimized for multi-core servers.

## Architecture: Multi-Process Parallel Collector

**When to use**: Collecting from multiple independent sources simultaneously.

**Key insight**: Use `multiprocessing.Process` (not threads) for true parallelism on multi-core servers. Each process maintains its own state file, with a shared counter for progress tracking.

```python
from multiprocessing import Process, Manager, Lock, Value
import signal, sys, json
from pathlib import Path

# Shared counter (atomic via Lock)
shared_counter = Value('i', 0)
lock = Lock()
stop_event = multiprocessing.Event()

# Each process has its own seen-state file
def init_process_seen(process_name):
    seen_file = BASE_DIR / f"seen_{process_name}.json"
    if seen_file.exists():
        data = json.loads(seen_file.read_text())
        return set(data.get("urls", [])), set(data.get("contents", []))
    return set(), set()

def save_process_seen(process_name, seen_urls, seen_contents):
    seen_file = BASE_DIR / f"seen_{process_name}.json"
    data = {"urls": list(seen_urls), "contents": list(seen_contents)}
    seen_file.write_text(json.dumps(data, indent=2))

# Process function
def process_source(shared_counter, lock, stop_event):
    process_name = "source_name"
    seen_urls, seen_contents = init_process_seen(process_name)
    session = create_session()
    
    while not stop_event.is_set():
        # Collect data...
        with lock:
            shared_counter.value += 1
        # Periodic save
        if shared_counter.value % 50 == 0:
            save_process_seen(process_name, seen_urls, seen_contents)
        
        # Sleep with interrupt check
        for _ in range(interval):
            if stop_event.is_set():
                break
            time.sleep(1)

# Signal handling for graceful shutdown
def signal_handler(signum, frame):
    stop_event.set()
    for p in processes:
        p.join(timeout=30)
        if p.is_alive():
            p.terminate()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
```

### Why Per-Process State Files?

- `Manager().list()` returns `ListProxy` which **doesn't have `.add()` method**
- `Manager().set()` works but adds IPC overhead for every operation
- Per-process state files: no IPC, no lock contention, periodic sync
- Cross-process dedup: check other processes' seen files (optional, adds some overhead)

## Pitfalls

### 1. Python `requests` + gzip: Don't Manually Decompress

**Problem**: Manual `gzip.decompress(resp.content)` fails when server sends plain JSON with `Content-Encoding: gzip` header.

**Solution**: Use `resp.text` — requests handles decompression automatically.

```python
# ❌ WRONG - crashes on plain JSON responses
if resp.headers.get("Content-Encoding") == "gzip":
    content = gzip.decompress(resp.content).decode("utf-8")
else:
    content = resp.text

# ✅ CORRECT - requests handles it
content = resp.text
```

**Why it happens**: Some servers (like GitHub API) send `Content-Encoding: gzip` header but the actual content is plain JSON. `requests` transparently decompresses when using `.text`, but `.content` returns raw bytes.

### 2. `multiprocessing.Manager().list()` is ListProxy

**Problem**: `Manager().list()` returns a `ListProxy` object, not a real list.

```python
# ❌ WRONG - ListProxy has no .add()
shared_urls = manager.list()
shared_urls.add(url)  # AttributeError!

# ✅ CORRECT - use per-process state or Manager().dict()
# Option A: Per-process state (recommended for high-throughput)
# Option B: Manager().dict() with manual set operations
shared_urls = manager.dict()
shared_urls[url_hash] = True
```

### 3. URL Exhaustion in Loops

**Problem**: Fixed URL list + hash-based dedup = first round collects everything, subsequent rounds do nothing.

**Solution**: 
- Dynamic URL discovery (extract links from collected content)
- Multiple data sources (API search, trending, blogs, docs)
- Periodic refresh for changing content (GitHub Trending, search results)

## Data Source Patterns

### GitHub Trending (HTML scraping)
```python
# Extract repo links from trending page
repos = re.findall(r'href=["\'](/[^/]+/[^"\']+)["\']', content)
repos = [r for r in repos if r.count("/") == 2 and not r.startswith("/trending")]
# Then fetch README from raw.githubusercontent.com
```

### GitHub API Search
```python
# Search repositories by topic
url = f"https://api.github.com/search/repositories?q={topic}&sort=stars&per_page=10"
# Rate limit: 10 requests/minute for unauthenticated, 30 for authenticated
```

### Blog/Documentation Crawling
```python
# Extract article links with date patterns
article_patterns = [
    r'/\d{4}/\d{2}/',  # Date format
    r'/blog/', r'/article/', r'/post/', r'/tutorial/',
]
```

### Link Discovery from Collected Content
```python
# Scan collected files for new links
all_links = set()
for doc_file in collected_dir.glob("*.md"):
    content = doc_file.read_text()
    links = extract_links(content, "")
    all_links.update(links)
```

## Performance Tuning

- **Workers per process**: 4 threads for I/O-bound (network requests)
- **Process count**: 20 on 2C2G, 50 on 2C4G. Do NOT exceed — 100 processes on 2C2G crashes the server (SSH unreachable, requires hard reboot).
- **Request timeout**: 15s with 3 retries
- **Sleep between requests**: 0.5-2s to avoid rate limiting
- **Save interval**: Every 50 items or 5 minutes

## See Also

- `multi-process-scraper` — More complete reference with watchdog, size monitoring, scaling guide, and pitfalls
