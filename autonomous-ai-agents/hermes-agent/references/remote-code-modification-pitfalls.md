# Remote Code Modification Pitfalls

When modifying Python (or other code) files on remote servers via SSH from Hermes, these patterns cause failures. Avoid them.

## ❌ Pitfall 1: `sed` to delete lines by keyword from structured code

```bash
# BROKEN — deletes any line containing the keyword, including dict keys,
# comments, variable names, and string literals. Destroys Python structure.
ssh server 'sed -i "/操作系统/d" /opt/app/scraper.py'
```

**Symptom:** `SyntaxError: closing parenthesis ']' does not match opening parenthesis '{'` — dict/list brackets become unbalanced.

**Fix:** Use Python's `re` module for surgical removal of dict blocks, or write the complete replacement file and scp it.

## ❌ Pitfall 2: SSH heredoc with complex Python code

```bash
# BROKEN — bash interprets quotes, parens, $, backticks inside the heredoc
# before Python ever sees it. CJK characters and f-strings make it worse.
ssh server 'cat > script.py << "EOF"
question_bank = {
    "高等数学": [("函数f(x)=x²...", "0", "f'(x)=2x")],
}
EOF'
```

**Symptom:** `SyntaxError: unterminated string literal` or `unexpected token (`.

**Fix:** Write the file locally first, then scp:

```python
# 1. Write locally (execute_code or write_file)
with open('/tmp/script.py', 'w', encoding='utf-8') as f:
    f.write(script_code)

# 2. SCP to remote
terminal('scp /tmp/script.py server:/opt/app/script.py')

# 3. Replace and restart
terminal('ssh server "cd /opt/app && cp script.py main.py && systemctl restart app"')
```

## ✅ Correct Pattern: Local write → SCP → Replace → Restart

```bash
# Step 1: Backup
ssh server 'cd /opt/app && cp main.py main.py.bak'

# Step 2: Write complete replacement locally
# (use execute_code or write_file tool)

# Step 3: Upload
scp /tmp/new_script.py server:/opt/app/main.py

# Step 4: Verify syntax
ssh server 'python3 -c "import py_compile; py_compile.compile(\"/opt/app/main.py\", doraise=True)"'

# Step 5: Restart service
ssh server 'systemctl restart app && systemctl status app --no-pager | head -5'
```

## Notes

- Always backup before modifying (`cp file file.bak`)
- Always verify Python syntax after remote edits before restarting
- For small surgical edits (single-line changes), `sed` is fine — the danger is multi-line block deletion from structured data
- SSH alias `hz-server` (杭州服务器 47.96.236.144) is configured in `~/.ssh/config`
