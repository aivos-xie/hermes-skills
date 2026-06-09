# AList API Reference

Base URL: `http://localhost:5244`

## Authentication

```bash
# Login
TOKEN=$(curl -s http://localhost:5244/api/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"USER","password":"PASS"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")
```

## User Management

```bash
# Get current user info
curl -s http://localhost:5244/api/me -H "Authorization: $TOKEN"

# List all users (admin only)
curl -s http://localhost:5244/api/admin/user/list -H "Authorization: $TOKEN"

# Update user (change username/password/permissions)
curl -s http://localhost:5244/api/admin/user/update -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{
    "id": 2,
    "username": "new_name",
    "password": "new_pass",
    "role": [2],
    "disabled": false,
    "permission": 65535,
    "base_path": "/",
    "sso_id": ""
  }'
```

### Permission Bits
- 1 = View
- 2 = Download  
- 4 = Upload
- 8 = Mkdir
- 16 = Rename
- 32 = Move
- 64 = Copy
- 128 = Delete

Common combos:
- Guest with upload: `15` (1+2+4+8)
- Full admin: `65535`

### User IDs
- id=1 is always `guest`
- id=2 is the first admin user

## Storage Management

```bash
# List storages
curl -s http://localhost:5244/api/admin/storage/list -H "Authorization: $TOKEN"

# Create storage
curl -s http://localhost:5244/api/admin/storage/create -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{
    "mount_path": "/",
    "order": 0,
    "driver": "Local",
    "cache_expiration": 30,
    "status": "work",
    "addition": "{\"root_folder_path\":\"/host\",\"thumbnail\":false,\"show_hidden\":true,\"mkdir_perm\":\"777\"}"
  }'

# Update storage
curl -s http://localhost:5244/api/admin/storage/update -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"id":1, ...same fields as create...}'

# Delete storage
curl -s http://localhost:5244/api/admin/storage/delete -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"id":1}'
```

## File Operations

```bash
# List directory
curl -s http://localhost:5244/api/fs/list -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"path":"/","password":"","page":1,"per_page":50}'

# Upload file
curl -s http://localhost:5244/api/fs/put -X PUT \
  -H "Authorization: $TOKEN" \
  -H "File-Path: /path/to/file.txt" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @local_file.txt

# Create directory
curl -s http://localhost:5244/api/fs/mkdir -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"path":"/new_folder"}'

# Delete file/folder
curl -s http://localhost:5244/api/fs/remove -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"dir":"/path","names":["file.txt"]}'
```

## Common Pitfalls

1. **Role must be array**: `"role":[2]` not `"role":2`
2. **Password update API**: Use `/api/admin/user/update` NOT `/api/me/update-password` (returns HTML)
3. **Guest user ID**: Always id=1, admin users start from id=2
4. **Read-only mount**: `-v /:/host:ro` prevents uploads, remove `:ro`
5. **Storage UNIQUE constraint**: Cannot create duplicate mount_path, must update existing
