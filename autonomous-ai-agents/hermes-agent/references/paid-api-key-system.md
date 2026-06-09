# Paid API Key System Pattern

Reusable pattern for adding license key validation to a FastAPI backend. Users must provide a valid key with remaining uses to access API endpoints.

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS license_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,           -- format: CX-XXXX-XXXX-XXXX
    max_uses INTEGER DEFAULT 100,       -- total allowed queries
    used_count INTEGER DEFAULT 0,       -- consumed queries
    expires_at TIMESTAMP,               -- NULL = never expires
    note TEXT DEFAULT '',               -- buyer label
    status TEXT DEFAULT 'active',       -- active|disabled|expired|exhausted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_key ON license_keys(key);
```

## Key Generation

```python
import secrets

def generate_key(prefix="CX"):
    """Generate formatted key: CX-XXXX-XXXX-XXXX"""
    part = secrets.token_hex(2).upper()
    return f"{prefix}-{part[:4]}-{part[4:8]}-{secrets.token_hex(2).upper()}"
```

## Validation Flow

```python
def validate_key(key: str):
    """Returns (valid, message, info_dict)"""
    if not key:
        return False, "请提供密钥", None
    row = db.execute("SELECT * FROM license_keys WHERE key = ?", (key,)).fetchone()
    if not row:
        return False, "密钥不存在", None
    if row['status'] != 'active':
        return False, "密钥已被禁用", None
    if row['expires_at'] and parse(row['expires_at']) < now():
        db.execute("UPDATE license_keys SET status='expired' WHERE id=?", (row['id'],))
        return False, "密钥已过期", None
    remaining = row['max_uses'] - row['used_count']
    if remaining <= 0:
        db.execute("UPDATE license_keys SET status='exhausted' WHERE id=?", (row['id'],))
        return False, "查询次数已用完", None
    return True, "ok", {"remaining": remaining, ...}

def consume_key(key: str):
    """Decrement remaining uses by 1"""
    db.execute("UPDATE license_keys SET used_count = used_count + 1 WHERE key = ?", (key,))
```

## Protected Endpoint Pattern

```python
@app.post("/search")
async def search(request: Request):
    body = await request.json()
    key = body.get("key", "").strip()
    
    # Validate key first
    valid, msg, info = validate_key(key)
    if not valid:
        return JSONResponse({"code": -1, "message": msg, "error": "auth_failed"})
    
    # Process request
    result = do_search(body)
    
    # Consume one use
    consume_key(key)
    
    return {"code": 1, "answer": result, "remaining": info['remaining'] - 1}
```

## Admin Endpoints

All admin endpoints require a static `ADMIN_TOKEN` (set in .env):

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/admin/generate-key` | POST | Batch generate keys (count, max_uses, days, note) |
| `/admin/keys` | GET | List all keys with pagination |
| `/admin/disable-key` | POST | Toggle key status (active/disabled) |
| `/admin/reset-key` | POST | Reset used_count and extend expiry |
| `/admin/delete-key` | POST | Permanently delete a key |

## Admin UI

Single-page HTML admin panel with:
- Dashboard stats (active keys, total questions, today's queries)
- Batch key generation with configurable uses/days/note
- Key list with filter/search, inline actions (copy/disable/reset/delete)
- Mobile-friendly responsive design

Access: `GET /admin` → serves static HTML (no login required for the page itself; admin API calls include the token in the request body).

## Userscript Integration

The Tampermonkey script stores the key in `GM_setValue('license_key', '')` and sends it with every API request. On first load, it shows a key input dialog. If the key expires mid-session, it re-prompts.

```javascript
// In search request
data: JSON.stringify({ title, options, type, key: licenseKey })

// Handle auth failure
if (data.code === -1) {
    isValidated = false;
    showKeyDialog('密钥已失效: ' + data.message);
}
```

## Pitfalls

- **Empty answer caching**: Don't cache empty/null answers from AI — they pollute the database. Check `if answer and answer.strip()` before `save_to_local()`.
- **MiMo reasoning model**: MiMo returns answers in `reasoning_content`, not `content`. Check both: `msg.get('content', '') or msg.get('reasoning_content', '')`.
- **Key format**: Use a recognizable prefix (CX-, KEY-, etc.) so keys are easy to identify in logs.
- **Rate limiting**: Consider adding per-key rate limiting (e.g., max 10 queries/minute) to prevent abuse.
- **SQLite concurrency**: For high-traffic setups, use PostgreSQL instead. SQLite handles ~100 concurrent reads but only 1 write at a time.
