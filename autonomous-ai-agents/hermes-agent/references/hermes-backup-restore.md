# Hermes Agent Backup & Restore

## What to Back Up

| Path | Content | Priority |
|------|---------|----------|
| `~/.hermes/config.yaml` | Main config | Critical |
| `~/.hermes/.env` | API keys, secrets | Critical |
| `~/.hermes/auth.json` | OAuth tokens, credential pools | Critical |
| `~/.hermes/SOUL.md` | Personality definition | High |
| `~/.hermes/channel_directory.json` | Platform channel mappings | High |
| `~/.hermes/skills/` | Installed skills (20MB typical) | High |
| `~/.hermes/cron/` | Scheduled jobs + history | High |
| `~/.hermes/scripts/` | Custom scripts | High |
| `~/.hermes/memories/` | MEMORY.md + USER.md | High |
| `~/.hermes/memory-repo/` | Git-backed memory repo | Medium |
| `~/.hermes/sessions/` | Session transcripts (large, 70MB+) | Low (regenerable) |
| `~/.hermes/state.db` | SQLite session store (30MB+) | Low (regenerable) |
| `~/.hermes/cache/` | Model caches | Skip |

## Full Backup Command

```bash
BACKUP_DIR="/path/to/backup/hermes-backup-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

cd ~/.hermes && tar czf "$BACKUP_DIR/hermes-full-backup.tar.gz" \
  config.yaml \
  .env \
  auth.json \
  SOUL.md \
  channel_directory.json \
  skills/ \
  cron/ \
  scripts/ \
  memories/ \
  memory-repo/

# Compress further with xz (saves ~15% over gzip)
xz -9 "$BACKUP_DIR/hermes-full-backup.tar.gz"
```

## Restore Command

```bash
BACKUP_FILE="/path/to/backup/hermes-backup-YYYYMMDD.tar.gz.xz"

# If xz compressed
xz -d "$BACKUP_FILE"
tar xzf "${BACKUP_FILE%.xz}" -C ~/.hermes/

# If plain tar.gz
tar xzf "$BACKUP_FILE" -C ~/.hermes/

# Restart gateway if running
hermes gateway restart
```

## Selective Restore

```bash
# Config only
cp backup/config.yaml ~/.hermes/config.yaml

# Memories only
cp -r backup/memories/* ~/.hermes/memories/

# Skills only
cp -r backup/skills/* ~/.hermes/skills/

# Cron jobs only
cp -r backup/cron/* ~/.hermes/cron/
```

## Pitfalls

- `.env` contains API keys — never commit to public repos or share publicly
- `auth.json` contains OAuth tokens — treat as secrets
- Restoring `state.db` from a different Hermes version may cause schema issues — prefer fresh state
- `sessions/` directory can be 70MB+ — exclude from routine backups if space-constrained
- After restore, run `hermes doctor` to verify config integrity
- Cron job output history is in `cron/output/` — useful for debugging but not critical

## Automated Backup (GitHub Sync Pattern)

For automated backup to GitHub (private repo), see `references/skill-sync-github.md`.

## Compression Comparison

| Format | Typical Size | Command |
|--------|-------------|---------|
| tar (uncompressed) | ~25MB | `tar cf backup.tar` |
| tar.gz (gzip -9) | ~9MB | `tar czf backup.tar.gz` |
| tar.gz.xz (xz -9) | ~7.6MB | `xz -9 backup.tar.gz` |
