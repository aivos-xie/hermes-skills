# Skill Sync & Backup to GitHub

## Pattern

Automate syncing `~/.hermes/skills/` to a **public** GitHub repository on a cron schedule. Memory files are included but sanitized of sensitive information.

## Sync Script

Path: `~/.hermes/scripts/sync_skills_to_github.py`

```python
#!/usr/bin/env python3
"""Sync skills + sanitized memory to GitHub."""
import os, re, subprocess
from pathlib import Path

SENSITIVE_PATTERNS = [
    r'(?:api[_-]?key|token|secret|password|passwd|pwd)\s*[=:]\s*["\']?([A-Za-z0-9_\-\.]+)["\']?',
    r'1[3-9]\d{9}',                          # phone numbers
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # emails
    r'\b(?:\d{1,3}\.){3}\d{1,3}\b',          # IP addresses
    r'(?:cookie|session|token)\s*[=:]\s*["\']?([A-Za-z0-9_\-\.]+)["\']?',
    r'https?://(?:localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)[^\s]*',
]

def remove_sensitive(text):
    for p in SENSITIVE_PATTERNS:
        text = re.sub(p, '[REDACTED]', text, flags=re.IGNORECASE)
    return text

skills_dir = Path.home() / '.hermes' / 'skills'
memory_file = Path.home() / 'user_memory.md'
public_memory = skills_dir / 'memory' / 'public-memory.md'
public_memory.parent.mkdir(parents=True, exist_ok=True)

if memory_file.exists():
    with open(memory_file, 'r', encoding='utf-8') as f:
        clean = remove_sensitive(f.read())
    with open(public_memory, 'w', encoding='utf-8') as f:
        f.write(clean)

os.chdir(skills_dir)
if not (skills_dir / '.git').exists():
    subprocess.run(['git', 'init'], check=True)
    subprocess.run(['git', 'remote', 'add', 'origin',
        f'https://x-access-token:{os.environ.get("GITHUB_TOKEN","")}@github.com/USER/REPO.git'], check=True)

subprocess.run(['git', 'add', '-A'], check=True)
subprocess.run(['git', 'commit', '-m',
    f'auto: skills sync {subprocess.check_output(["date","+%Y-%m-%d"]).decode().strip()}'], check=True)
subprocess.run(['git', 'push', 'origin', 'main'], check=True)
```

## Cron Job Setup

```bash
# Via Hermes cron
hermes cron create "0 2 * * *" --name skills-memory-sync \
  --prompt "Run: python3 ~/.hermes/scripts/sync_skills_to_github.py"
```

## Sensitive Info Filter Rules

| Category | Pattern | Replacement |
|----------|---------|-------------|
| API Key/Token/Password | `key=value`, `token: "xxx"` | `[REDACTED]` |
| Phone numbers | `1XXXXXXXXXX` | `[REDACTED]` |
| Emails | `user@domain.com` | `[REDACTED]` |
| IP addresses | `x.x.x.x` | `[REDACTED]` |
| Cookie values | `cookie=xxx` | `[REDACTED]` |
| Private URLs | `localhost`, `192.168.*`, `10.*` | `[REDACTED]` |

## Pitfalls

- **Repo must be public if user requests it** — check before creating. Default to private.
- **GITHUB_TOKEN must be in `.env`** — the sync script reads it from environment.
- **First push needs `git push -u origin main`** — subsequent pushes use `git push origin main`.
- **Memory file `user_memory.md` is the source of truth** — the sanitized version goes to `memory/public-memory.md`.
- **Commit message includes date** — makes it easy to find specific syncs.
