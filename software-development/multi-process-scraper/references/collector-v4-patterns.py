#!/usr/bin/env python3
"""
Multi-Process Collector v4.0 — 50-process version
Deployed on 2C2G Alibaba Cloud Linux 4 server (47.96.236.144)

Key patterns:
- 10 processes per type (trending/search/docs/blogs/discovery)
- Per-process seen sets (not shared Manager proxies)
- Manager.Value('i', 0) for shared counter only
- Manager.Event() for stop signal
- 60-second sleep loop with 1-second stop checks
- Per-process log files: collector_{name}.log

Run: nohup python3 main_v4.py > /dev/null 2>&1 &
Stop: kill -9 $(ps aux | grep main_v4 | grep -v grep | awk '{print $2}')
"""

# === WORKER TEMPLATE ===
def worker_search(pid, counter, lock, stop):
    name = f"search_{pid}"
    init_seen(name)  # load seen_{name}.json into process_seen[name]
    log(f"启动", name)
    session = create_session()
    
    while not stop.is_set():
        try:
            topics = random.sample(GITHUB_SEARCH_TOPICS, 3)
            for topic in topics:
                if stop.is_set(): break
                content, _, _ = fetch_url(session, f"https://api.github.com/search/repositories?q={topic}&sort=stars&per_page=5")
                if not content: continue
                try:
                    for repo in json.loads(content).get("items", []):
                        collect(session, f"https://raw.githubusercontent.com/{repo['full_name']}/main/README.md",
                                topic.replace(" ", "_"), "search", counter, lock, name)
                except: pass
                time.sleep(2)  # GitHub API rate limit
            save_seen(name)
            for _ in range(60):  # wait 60 seconds
                if stop.is_set(): break
                time.sleep(1)
        except Exception as e:
            log(f"❌ {e}", name, "ERROR")
            time.sleep(10)

# === MAIN SPAWN ===
def main():
    manager = Manager()
    counter = manager.Value('i', 0)
    lock = manager.Lock()
    stop = manager.Event()
    
    procs = []
    for i in range(10):  # 10 per type
        procs.append(Process(target=worker_trending, args=(i, counter, lock, stop)))
        procs.append(Process(target=worker_search, args=(i, counter, lock, stop)))
        procs.append(Process(target=worker_docs, args=(i, counter, lock, stop)))
        procs.append(Process(target=worker_blogs, args=(i, counter, lock, stop)))
        procs.append(Process(target=worker_discovery, args=(i, counter, lock, stop)))
    
    for p in procs: p.start()

# === WORK DISTRIBUTION ===
# For docs/blogs: split by PID modulo
batch = TECH_DOCS[pid::10]  # worker 0 gets items [0,10,20,...], worker 1 gets [1,11,21,...]

# For search/trending: each worker picks random topics independently
topics = random.sample(GITHUB_SEARCH_TOPICS, 3)
