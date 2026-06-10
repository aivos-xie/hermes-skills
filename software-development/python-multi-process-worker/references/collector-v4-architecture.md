# Collector v4.0 Architecture Reference

## Overview
Multi-process parallel tech resource collector running on Alibaba Cloud ECS (2C2G, 47.96.236.144).

## Process Layout (20 processes)
```
main_v4.py
├── trend_0..3    (4 processes) — GitHub Trending per-language
├── search_0..3   (4 processes) — GitHub API keyword search
├── docs_0..3     (4 processes) — Official tech docs (Python, Docker, K8s, etc.)
├── blog_0..3     (4 processes) — dev.to, Medium, Hackernoon articles
└── disc_0..3     (4 processes) — Link discovery from collected content
```

## Data Sources
| Source | URL Pattern | Interval |
|--------|------------|----------|
| GitHub Trending | `github.com/trending/{lang}?since=daily` | 60s |
| GitHub API Search | `api.github.com/search/repositories?q={topic}` | 60s |
| Tech Docs | Official docs (17 sites) | 60s |
| Tech Blogs | dev.to, Medium, Hackernoon seeds | 60s |
| Discovery | Extract links from collected .md files | 60s |

## Storage Structure
```
/opt/collector/data/
├── docs/{category}/{filename}_{hash}.md   — collected content
├── seen_{worker_name}.json                — per-process dedup state
├── collector_{worker_name}.log            — per-process logs
├── counter.json                           — global count
└── stats.json                             — statistics
```

## File Format
```markdown
# {original_url}
Collected: {ISO timestamp}
Source: {trending|search|docs|blog|discovery}
Size: {bytes}

{original content}
```

## Dedup Strategy
- URL hash (MD5 first 12 chars) → skip if seen
- Content hash (MD5 first 12 chars) → skip duplicate content
- Per-process seen files (no cross-process locking needed)
- Periodic save (every 50 items)

## Safe Scaling
| Server Spec | Max Processes | Expected Files/Hour |
|-------------|---------------|---------------------|
| 2C 2G | 20-25 | ~500-1000 |
| 2C 4G | 50 | ~2000-3000 |
| 4C 8G | 100 | ~5000+ |

## Lessons Learned
1. Started with 5 processes → too slow
2. Scaled to 20 → good balance
3. Tried 100 → server locked up, SSH unreachable, needed cloud console restart
4. Sweet spot for 2G: 20 processes with 60s intervals
