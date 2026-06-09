#!/bin/bash
# AList Security Lockdown Script
# Usage: ./lockdown.sh <alist_url> <admin_user> <admin_password>

set -e

ALIST_URL="${1:-http://localhost:5244}"
ADMIN_USER="${2:-aivos}"
ADMIN_PASS="${3}"

if [ -z "$ADMIN_PASS" ]; then
    echo "Usage: $0 <alist_url> <admin_user> <admin_password>"
    echo "Example: $0 http://localhost:5244 aivos mypassword"
    exit 1
fi

echo "=== AList Security Lockdown ==="
echo "Target: $ALIST_URL"
echo ""

# Step 1: Login
echo "[1/4] Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$ALIST_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$ADMIN_USER\",\"password\":\"$ADMIN_PASS\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed!"
    echo "$LOGIN_RESPONSE"
    exit 1
fi
echo "✅ Login successful"

# Step 2: Get user list
echo ""
echo "[2/4] Fetching user list..."
USERS=$(curl -s -X GET "$ALIST_URL/api/admin/user/list" \
    -H "Authorization: $TOKEN")
echo "$USERS" | python3 -c "
import sys, json
data = json.load(sys.stdin)['data']['content']
print(f\"Found {len(data)} users:\")
for u in data:
    status = '❌ DISABLED' if u['disabled'] else '✅ ACTIVE'
    role = 'ADMIN' if 2 in u['role'] else 'GUEST'
    print(f\"  - {u['username']} ({role}) {status}\")
"

# Step 3: Disable guest user
echo ""
echo "[3/4] Disabling guest user..."
GUEST_ID=$(echo "$USERS" | python3 -c "
import sys, json
data = json.load(sys.stdin)['data']['content']
for u in data:
    if u['username'] == 'guest':
        print(u['id'])
        break
")

if [ -n "$GUEST_ID" ]; then
    curl -s -X POST "$ALIST_URL/api/admin/user/update" \
        -H "Content-Type: application/json" \
        -H "Authorization: $TOKEN" \
        -d "{\"id\":$GUEST_ID,\"username\":\"guest\",\"base_path\":\"/\",\"role\":[1],\"disabled\":true,\"permission\":0}" > /dev/null
    echo "✅ Guest user disabled"
else
    echo "⚠️  Guest user not found"
fi

# Step 4: Verify anonymous access is blocked
echo ""
echo "[4/4] Verifying anonymous access is blocked..."
ANON_TEST=$(curl -s -X GET "$ALIST_URL/api/fs/list" \
    -H "Content-Type: application/json" \
    -d '{"path":"/"}')

if echo "$ANON_TEST" | grep -q "401\|disabled\|login"; then
    echo "✅ Anonymous access blocked"
else
    echo "⚠️  Anonymous access may still be allowed"
    echo "$ANON_TEST"
fi

echo ""
echo "=== Lockdown Complete ==="
echo ""
echo "Admin login:"
echo "  URL: $ALIST_URL"
echo "  User: $ADMIN_USER"
echo "  Pass: $ADMIN_PASS"
