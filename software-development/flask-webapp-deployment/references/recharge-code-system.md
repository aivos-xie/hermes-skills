# Recharge Code System Pattern

A complete pattern for implementing prepaid code systems (充值码) in Flask applications.

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS recharge_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    times INTEGER DEFAULT 100,
    used_by TEXT,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Create Codes (Batch or Custom)

```python
@app.route('/admin/api/codes/create', methods=['POST'])
def admin_create_codes():
    d = request.json
    t = d.get('times', 100)
    c = d.get('count', 10)
    custom_code = d.get('code', '').strip().upper()
    codes = []
    conn = get_db()
    
    if custom_code:
        # Custom code
        try:
            conn.execute("INSERT INTO recharge_codes(code,times) VALUES(?,?)", (custom_code, t))
            conn.commit()
            codes.append(custom_code)
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'error': 'Code already exists'}), 400
    else:
        # Batch generate
        for _ in range(c):
            code = f"RC-{uuid.uuid4().hex[:8].upper()}"
            conn.execute("INSERT INTO recharge_codes(code,times) VALUES(?,?)", (code, t))
            codes.append(code)
        conn.commit()
    
    conn.close()
    return jsonify({'codes': codes})
```

### Recharge (Use Code)

```python
@app.route('/api/recharge', methods=['POST'])
def recharge():
    d = request.json
    u = d.get('username', '').strip()
    code = d.get('code', '').strip().upper()
    conn = get_db()
    rc = conn.execute("SELECT * FROM recharge_codes WHERE code=? AND used_by IS NULL", (code,)).fetchone()
    if not rc:
        conn.close()
        return jsonify({'error': 'Invalid or used code'}), 400
    conn.execute("UPDATE users SET balance=balance+? WHERE username=?", (rc['times'], u))
    conn.execute("UPDATE recharge_codes SET used_by=?,used_at=datetime('now') WHERE code=?", (u, code))
    conn.commit()
    bal = conn.execute("SELECT balance FROM users WHERE username=?", (u,)).fetchone()['balance']
    conn.close()
    return jsonify({'message': 'Recharged', 'added': rc['times'], 'balance': bal})
```

## Frontend: Copyable Codes

```javascript
// Copy to clipboard
function copyText(text) {
    navigator.clipboard.writeText(text)
        .then(() => toast('Copied: ' + text))
        .catch(() => {
            // Fallback for older browsers
            const ta = document.createElement('textarea');
            ta.value = text;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            toast('Copied');
        });
}

// Render code list with copy buttons
function loadCodes() {
    api('/codes').then(d => {
        document.getElementById('cl').innerHTML = d.codes.map(c => `
            <div class="list-item">
                <div>
                    <code onclick="copyText('${c.code}')">${c.code}</code>
                    <button class="copy-btn" onclick="copyText('${c.code}')">Copy</button>
                    <span class="badge ${c.used_by ? 'badge-red' : 'badge-green'}">
                        ${c.used_by ? 'Used' : 'Available'} ${c.times}x
                    </span>
                </div>
            </div>
        `).join('');
    });
}
```

## Custom Code Form

```html
<div class="card">
    <h3>🎫 Generate Codes</h3>
    <div class="form-row">
        <label>Custom Code</label>
        <input id="customCode" placeholder="Leave empty for auto-generate" style="flex:1">
    </div>
    <div class="form-row">
        <label>Times</label>
        <input id="ct" type="number" value="100" style="width:90px">
        <label>Count</label>
        <input id="cc" type="number" value="10" style="width:90px">
        <button onclick="mkCodes()">Generate</button>
    </div>
</div>
```

## Key Features

1. **Custom codes**: Users can specify their own code string
2. **Batch generation**: Auto-generate multiple codes at once
3. **One-time use**: Each code can only be redeemed once
4. **Copy-friendly**: Click to copy functionality
5. **Balance tracking**: Users have a balance that increases on recharge
