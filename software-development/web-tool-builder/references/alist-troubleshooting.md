# AList Troubleshooting

Common issues when managing AList file manager instances.

## Permission Issues

### Problem: All users can log in (including guest)
AList enables guest access by default. The guest user has `disabled=false` in the database.

**Fix via API:**
```bash
# Login as admin
TOKEN=$(curl -s -X POST "http://localhost:5244/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"YOUR_PASS"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# Disable guest user (id=1)
curl -s -X POST "http://localhost:5244/api/admin/user/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"id":1,"username":"guest","password":"","base_path":"/","role":[1],"disabled":true,"permission":0}'
```

**Fix via database:**
```bash
sqlite3 /opt/alist/data/data.db "UPDATE x_users SET disabled=1 WHERE username='guest';"
```

### Problem: Anonymous file browsing still works
The storage may have anonymous access enabled. Check storage settings:
```bash
sqlite3 /opt/alist/data/data.db "SELECT id, driver, addition FROM x_storages;"
```

## Storage Issues

### Problem: "storage not found" after user update
Updating users via the admin API can reset storage configurations. The `root_folder_path` in the storage addition JSON may be empty or invalid.

**Diagnosis:**
```bash
sqlite3 /opt/alist/data/data.db "SELECT id, mount_path, addition FROM x_storages;"
```

**Fix:**
```bash
# Update root_folder_path directly
sqlite3 /opt/alist/data/data.db "UPDATE x_storages SET addition='{\"root_folder_path\":\"/opt/alist/data/storage\",...}' WHERE id=1;"
sudo docker restart alist
```

### Problem: Files not visible after restart
The storage directory path may not exist inside the container. AList Docker only mounts `/opt/alist/data`.

**Fix:** Store files in `/opt/alist/data/storage/` (inside the mounted volume), not `/opt/alist/storage/`.

## Password Management

### alist admin set command
The `alist admin set` command reads password from stdin interactively — it does NOT accept command-line arguments.

```bash
# This does NOT work:
sudo docker exec alist ./alist admin set username password

# This sets password to the username:
sudo docker exec alist ./alist admin set username password
# (the second arg is ignored, password is read from stdin)
```

**Better approach: Use the API**
```bash
# Get admin token
sudo docker exec alist ./alist admin token CURRENT_PASSWORD

# Update password via API
curl -s -X POST "http://localhost:5244/api/admin/user/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: $ADMIN_TOKEN" \
  -d '{"id":2,"username":"aivos","password":"NEW_PASS","base_path":"/","role":[2],"disabled":false,"permission":65535}'
```

### alist admin random
Generates a random password and prints it. Useful for recovery:
```bash
sudo docker exec alist ./alist admin random
# Output: password: HV0aHbPO
```

## Docker-Specific Issues

### Container doesn't have sqlite3
```bash
# Run sqlite3 from host, pointing to mounted data
sqlite3 /opt/alist/data/data.db "SELECT * FROM x_users;"
```

### Cannot exec with -t flag (TTY)
```bash
# Wrong:
sudo docker exec -it alist ./alist admin set user pass

# Right:
sudo docker exec alist ./alist admin random
```

## User Permission Values

| Permission Value | Meaning |
|-----------------|---------|
| 0 | No permissions |
| 65535 | All permissions |

## User Role Values

| Role Array | Meaning |
|------------|---------|
| [1] | Guest |
| [2] | Admin |
| [1,2] | Guest + Admin |