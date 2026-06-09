---
name: alist-admin
description: AList file manager administration — user management, security hardening, API usage, and Docker deployment. Use when managing AList instances, changing passwords, configuring permissions, or troubleshooting login issues.
triggers:
  - alist
  - file manager
  - 网盘
  - file server
  - alist admin
  - alist password
  - alist user
---

# AList Administration

AList is a file listing program that supports multiple storage providers. This skill covers deployment, user management, security hardening, and API usage.

## Deployment (Docker)

```bash
# Standard Docker deployment
docker run -d --name alist \
  -p 5244:5244 \
  -v /opt/alist/data:/opt/alist/data \
  xhofe/alist:latest

# Check status
docker ps | grep alist
```

## Database Structure

AList uses SQLite with `x_` prefix for tables:
- **Database path**: `/opt/alist/data/data.db`
- **Users table**: `x_users`
- **Key columns**: `id`, `username`, `password`, `disabled`, `permission`, `role`

```bash
# Query users from host (sqlite3 not in container)
sqlite3 /opt/alist/data/data.db "SELECT id, username, disabled, permission, role FROM x_users;"
```

## User Management

### Reset Admin Password (CLI)

```bash
# Generate random password
docker exec alist ./alist admin random

# ⚠️ PITFALL: `alist admin set` does NOT accept piped input in Docker
# Use the API instead for setting specific passwords
```

### Reset Admin Password (API)

```bash
# Step 1: Get admin token (use current or random password)
docker exec alist ./alist admin token <current-password>

# Step 2: Login to get auth token
curl -s -X POST "http://localhost:5244/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<current-password>"}'

# Step 3: Update password via API
curl -s -X POST "http://localhost:5244/api/admin/user/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: <token>" \
  -d '{"id":2,"username":"admin","password":"<new-password>","base_path":"/","role":[2],"disabled":false,"permission":65535}'
```

### Disable Guest User

```bash
# Update database directly
sqlite3 /opt/alist/data/data.db "UPDATE x_users SET disabled=1 WHERE username='guest';"

# Or via API
curl -s -X POST "http://localhost:5244/api/admin/user/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: <token>" \
  -d '{"id":1,"username":"guest","base_path":"/","role":[1],"disabled":true,"permission":0}'
```

## Security Hardening

### Full Lockdown (Admin-Only Access)

1. **Disable guest user**: `disabled=1` in database
2. **Set restrictive permissions**: `permission=0` for guest
3. **Verify anonymous access blocked**:
   ```bash
   curl -s -X GET "http://localhost:5244/api/fs/list" \
     -H "Content-Type: application/json" \
     -d '{"path":"/"}'
   # Should return: {"code":401,"message":"Guest user is disabled, login please"}
   ```

### Permission Bits

- `0`: No permissions (view only when logged in)
- `1`: Can see hides
- `2`: Can access without password
- `4`: Can add offline download tasks
- `8`: Can mkdir
- `16`: Can rename
- `32`: Can move
- `64`: Can copy
- `128`: Can remove
- `256`: Can webdav read
- `512`: Can webdav manage
- `1024`: Can see hidden files
- `65535`: All permissions (admin)

### Role Values

- `[1]`: Guest (unauthenticated)
- `[2]`: Admin

## API Endpoints

### Authentication
- `POST /api/auth/login` — Login, returns token
- `POST /api/auth/login/hash` — Login with password hash

### User Management (Admin)
- `GET /api/admin/user/list` — List all users
- `POST /api/admin/user/update` — Update user (requires full user object)
- `POST /api/admin/user/create` — Create new user
- `POST /api/admin/user/delete` — Delete user

### File Operations
- `POST /api/fs/list` — List directory contents
- `POST /api/fs/get` — Get file info
- `POST /api/fs/dirs` — List directories only

## Common Pitfalls

1. **`alist admin set` in Docker**: Does not accept piped stdin. Use API instead.
2. **Wrong API endpoint**: `/api/me/update-password` returns HTML (frontend route). Use `/api/admin/user/update`.
3. **Role format**: Must be array `[2]`, not number `2`.
4. **Empty password field**: If password is empty in database, user cannot login. Use `alist admin random` to reset.
5. **Guest access**: Must set `disabled=1` AND `permission=0` to fully block anonymous access.
6. **`alist admin set` defaults to username**: Running `docker exec alist ./alist admin set` without piping input sets the password to the username (e.g., password becomes "admin"). Always use the API to set specific passwords.

## Troubleshooting

### Can't Login After Changes

```bash
# Check if user exists and is enabled
sqlite3 /opt/alist/data/data.db "SELECT id, username, disabled FROM x_users;"

# Reset to random password
docker exec alist ./alist admin random

# Login with random password and change via API
```

### Files Not Visible / Storage Not Found

**Root cause**: Docker only mounts `/opt/alist/data`, so storage must be INSIDE that path.

```bash
# ⚠️ PITFALL: Default storage path `/opt/alist/storage` is WRONG for Docker
# Docker only mounts /opt/alist/data, so use /opt/alist/data/storage instead

# Fix: Create correct storage directory
sudo mkdir -p /opt/alist/data/storage
sudo chmod 777 /opt/alist/data/storage

# Move files from old location if they exist
sudo mv /opt/alist/storage/* /opt/alist/data/storage/ 2>/dev/null

# Update storage configuration in database
sqlite3 /opt/alist/data/data.db "UPDATE x_storages SET addition='{\"root_folder_path\":\"/opt/alist/data/storage\",\"thumbnail\":false,\"thumb_cache_folder\":\"\",\"show_hidden\":true,\"mkdir_perm\":\"777\",\"recycle_bin_path\":\"delete permanently\"}' WHERE id=1;"

# Restart container
docker restart alist
```

### Storage Disappears After User Changes

When updating users via API, storage config can get corrupted. Always verify after:

```bash
# Check storage list
curl -s -X GET "http://localhost:5244/api/admin/storage/list" \
  -H "Authorization: <token>"

# If empty, recreate storage
curl -s -X POST "http://localhost:5244/api/admin/storage/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: <token>" \
  -d '{
    "mount_path": "/",
    "order": 0,
    "driver": "Local",
    "cache_expiration": 30,
    "status": "work",
    "addition": "{\"root_folder_path\":\"/opt/alist/data/storage\",\"thumbnail\":false,\"thumb_cache_folder\":\"\",\"show_hidden\":true,\"mkdir_perm\":\"777\",\"recycle_bin_path\":\"delete permanently\"}"
  }'
```

## Quick Reference

| Task | Command |
|------|---------|
| Reset admin password | `docker exec alist ./alist admin random` |
| Get admin token | `docker exec alist ./alist admin token <password>` |
| List users | `sqlite3 /opt/alist/data/data.db "SELECT * FROM x_users;"` |
| Disable guest | `sqlite3 ... "UPDATE x_users SET disabled=1 WHERE username='guest';"` |
| Check login | `curl -s -X POST http://localhost:5244/api/auth/login -d '{"username":"...","password":"..."}'` |
| Run lockdown script | `bash ~/.hermes/skills/devops/alist-admin/scripts/lockdown.sh <url> <user> <pass>` |
