---
name: bug-bounty
version: 1.0.0
description: Bug bounty hunting methodology — reconnaissance, exploitation, and report writing for HackerOne, Bugcrowd, and private programs
tags: [security, bug-bounty, pentesting, web-security, reconnaissance, hacking]
triggers:
  - bug bounty
  - vulnerability hunting
  - bounty program
  - HackerOne
  - Bugcrowd
  - recon pipeline
  - web app testing
  - vulnerability disclosure
---

# Bug Bounty Methodology

## Reconnaissance Pipeline

### Tool Installation

```bash
# Install Go (required for most tools)
wget https://go.dev/dl/go1.23.4.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.23.4.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> ~/.bashrc
source ~/.bashrc

# Subfinder — subdomain enumeration
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# httpx — HTTP probing
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# Katana — web crawling
go install -v github.com/projectdiscovery/katana/cmd/katana@latest

# Nuclei — vulnerability scanning
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Additional tools
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/tomnomnom/waybackurls@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest

# Amass (comprehensive subdomain enum)
go install -v github.com/owasp-amass/amass/v4/...@latest

# ffuf — web fuzzer
go install -v github.com/ffuf/ffuf/v2@latest

# Gau — fetch known URLs
go install -v github.com/lc/gau/v2/cmd/gau@latest

# Update Nuclei templates
nuclei -update-templates
```

---

## Phase 1: Subdomain Enumeration

### Passive Enumeration

```bash
# subfinder — fast passive subdomain enumeration
subfinder -d target.com -all -o subdomains_subfinder.txt

# assetfinder
assetfinder --subs-only target.com > subdomains_assetfinder.txt

# crt.sh (Certificate Transparency)
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sort -u > subdomains_crt.txt

# Amass — thorough but slow
amass enum -passive -d target.com -o subdomains_amass.txt

# Combine and deduplicate
cat subdomains_*.txt | sort -u > all_subdomains.txt
echo "[*] Found $(wc -l < all_subdomains.txt) unique subdomains"
```

### Active Enumeration (DNS Resolution)

```bash
# dnsx — resolve subdomains
cat all_subdomains.txt | dnsx -silent -a -resp -o resolved.txt

# Extract just live domains
cat resolved.txt | awk '{print $1}' | sort -u > live_subdomains.txt
```

### Recursive Subdomain Enumeration

```bash
# For each found subdomain, enumerate its subdomains
while read domain; do
    subfinder -d "$domain" -silent
done < live_subdomains.txt | sort -u >> all_subdomains.txt
```

---

## Phase 2: HTTP Probing and Screenshots

```bash
# httpx — probe for live HTTP services
cat live_subdomains.txt | httpx -silent -status-code -title -tech-detect -follow-redirects -o httpx_results.txt

# With screenshots
cat live_subdomains.txt | httpx -silent -screenshot -screenshot-timeout 10 -o httpx_with_screenshots.txt

# Filter by status code
cat httpx_results.txt | grep "\[200\]" | awk '{print $1}' > live_200.txt
cat httpx_results.txt | grep "\[301\]\|\[302\]" | awk '{print $1}' > redirects.txt
cat httpx_results.txt | grep "\[403\]" | awk '{print $1}' > forbidden_403.txt  # Interesting for bypass testing

# Extract interesting technologies
cat httpx_results.txt | grep -i "wordpress\|joomla\|drupal\|php\|asp\|tomcat\|jenkins\|gitlab\|grafana\|kibana"
```

---

## Phase 3: Port Scanning

```bash
# naabu — fast port scanner
naabu -list live_subdomains.txt -top-ports 1000 -silent -o open_ports.txt

# Common interesting ports to watch for
# 22 — SSH
# 80, 443, 8080, 8443 — Web
# 3000 — Grafana, Gitea
# 5000 — Docker registry, Flask
# 6379 — Redis
# 8443 — Alternative HTTPS
# 9090 — Prometheus
# 27017 — MongoDB
```

---

## Phase 4: URL Discovery and Crawling

```bash
# Katana — modern web crawler
katana -list live_200.txt -d 5 -jc -kf -o katana_urls.txt

# gau — fetch URLs from AlienVault OTX, Wayback, Common Crawl
cat live_subdomains.txt | gau --threads 5 --o gau_urls.txt

# waybackurls — Wayback Machine URLs
cat live_subdomains.txt | waybackurls > wayback_urls.txt

# Combine all URLs
cat katana_urls.txt gau_urls.txt wayback_urls.txt | sort -u > all_urls.txt
echo "[*] Found $(wc -l < all_urls.txt) unique URLs"

# Extract interesting endpoints
cat all_urls.txt | grep -iE "\.js$" | sort -u > js_files.txt
cat all_urls.txt | grep -iE "\.json$" | sort -u > json_endpoints.txt
cat all_urls.txt | grep -iE "\.xml$" | sort -u > xml_files.txt
cat all_urls.txt | grep -iE "\.(env|config|bak|old|swp|log)$" > sensitive_files.txt
cat all_urls.txt | grep -iE "api/|graphql|swagger|openapi" > api_endpoints.txt

# Extract parameters for testing
cat all_urls.txt | grep "=" | sort -u > parameterized_urls.txt
```

### JavaScript Analysis

```bash
# Extract secrets from JS files
cat js_files.txt | while read url; do
    curl -sk "$url" 2>/dev/null | grep -oiE "(api[_-]?key|secret|token|password|aws_access_key)['\"]?\s*[:=]\s*['\"][^'\"]+['\"]"
done

# LinkFinder for JS endpoint extraction
pip install linkfinder
cat js_files.txt | while read url; do
    python3 -m linkfinder.cli -i "$url" -o cli 2>/dev/null
done | sort -u > js_endpoints.txt
```

---

## Phase 5: Vulnerability Scanning

### Nuclei — Template-Based Scanning

```bash
# Basic scan
nuclei -l live_200.txt -t nuclei-templates/ -o nuclei_results.txt

# Scan with severity filter
nuclei -l live_200.txt -severity critical,high -o nuclei_critical.txt

# Scan for specific vulnerability types
nuclei -l live_200.txt -tags cve -o nuclei_cves.txt
nuclei -l live_200.txt -tags xss -o nuclei_xss.txt
nuclei -l live_200.txt -tags ssrf -o nuclei_ssrf.txt
nuclei -l live_200.txt -tags sqli -o nuclei_sqli.txt
nuclei -l live_200.txt -tags exposure -o nuclei_exposure.txt

# Scan for misconfigurations
nuclei -l live_200.txt -tags misconfig,config -o nuclei_misconfig.txt

# Scan for exposed panels
nuclei -l live_200.txt -tags panel,login -o nuclei_panels.txt

# Use custom templates
nuclei -l live_200.txt -t custom_templates/ -o nuclei_custom.txt

# Rate-limited scan (avoid WAF/bans)
nuclei -l live_200.txt -rate-limit 5 -bulk-size 5 -o nuclei_slow.txt
```

### Directory Bruteforcing

```bash
# ffuf — fast web fuzzer
# Directory discovery
ffuf -w /usr/share/seclists/Discovery/Web-Content/common.txt -u https://target.com/FUZZ -mc 200,301,302,403 -o ffuf_dirs.json -of json

# Subdomain bruteforce
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u https://FUZZ.target.com -mc 200,301,302 -o ffuf_subs.json

# Parameter fuzzing
ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -u "https://target.com/api?FUZZ=test" -mc 200 -o ffuf_params.json

# Virtual host discovery
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u https://target.com -H "Host: FUZZ.target.com" -mc 200 -o ffuf_vhosts.json
```

---

## Phase 6: Manual Testing — High-Value Vulnerabilities

### SSRF Testing

```bash
# Start interactsh callback listener
interactsh-client -v

# Test URLs in parameters
# Replace target parameter values with:
# http://YOUR_INTERACTSH_URL
# http://169.254.169.254/latest/meta-data/  (AWS metadata)
# http://metadata.google.internal/  (GCE metadata)
# http://169.254.169.254/metadata/v1/  (DigitalOcean)

# Common SSRF-prone parameters:
# url, uri, link, href, src, dest, redirect, feed, host, server
```

### XSS Testing

```bash
# Test reflected XSS in all parameterized URLs
# Payloads to try:
# <script>alert(1)</script>
# "><img src=x onerror=alert(1)>
# javascript:alert(1)
# {{constructor.constructor('alert(1)')()}}  (template injection)

# Use dalfox for automated XSS
go install -v github.com/hahwul/dalfox/v2@latest
cat parameterized_urls.txt | dalfox pipe --skip-bav -o xss_results.txt
```

### SQL Injection

```bash
# sqlmap
sqlmap -u "https://target.com/page?id=1" --batch --risk=3 --level=5

# Test POST parameters
sqlmap -u "https://target.com/login" --data="username=admin&password=test" --batch

# From URL list
cat parameterized_urls.txt | grep "=" | while read url; do
    sqlmap -u "$url" --batch --level=1 --risk=1 --smart
done
```

### IDOR and Access Control

```bash
# Test with two different accounts
# 1. Capture requests from account A (Burp/curl)
# 2. Replay with account B's session
# 3. Check if data is returned

# Common IDOR patterns:
# /api/users/123 → try /api/users/124
# /api/documents/abc-123 → try other UUIDs
# /api/orders?user_id=123 → try other user_ids
```

### GraphQL Testing

```bash
# Introspection query
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __schema { types { name fields { name type { name } } } } }"}'

# Use graphql-cop for automated testing
pip install graphql-cop
graphql-cop -t https://target.com/graphql
```

---

## Common Vulnerability Patterns to Look For

### Quick Wins (Most Likely to Be Accepted)

```
1. Exposed .git directory
   → curl -s https://target.com/.git/HEAD

2. Exposed .env file
   → curl -s https://target.com/.env

3. Exposed admin panels without auth
   → /admin, /manager, /console, /debug, /actuator

4. CORS misconfiguration
   → curl -H "Origin: https://evil.com" https://target.com/api/data -v
   → Check if Access-Control-Allow-Origin reflects evil.com

5. Host header injection
   → curl -H "Host: evil.com" https://target.com/password-reset

6. Open redirect
   → /redirect?url=https://evil.com
   → /login?returnTo=//evil.com

7. JWT issues
   → Algorithm confusion (RS256 → HS256)
   → None algorithm
   → Weak secrets (try hashcat)

8. Subdomain takeover
   → Check CNAME records pointing to unclaimed services
   → dig CNAME subdomain.target.com
   → Tools: subjack, canny
```

### Business Logic Bugs

```
1. Race conditions — send simultaneous requests (repeater → parallel)
2. Price manipulation — modify cart/checkout parameters
3. Privilege escalation — change role parameters in API calls
4. Rate limiting bypass — vary headers (X-Forwarded-For, etc.)
5. Account takeover — password reset flow flaws
```

---

## Report Writing

### Report Structure

```markdown
## Summary
[One paragraph: what the vulnerability is, impact, affected component]

## Severity: Critical/High/Medium/Low/Informational
CVSS Score: X.X (if applicable)

## Affected URL/Endpoint
https://target.com/api/v1/users/{id}/data

## Description
[Detailed technical explanation of the vulnerability]

## Steps to Reproduce
1. Login to https://target.com with a test account
2. Navigate to https://target.com/api/v1/users/2/data
3. Change `2` to `3` in the URL
4. Observe that user 3's data is returned

## Impact
[What can an attacker achieve? Data theft? Account takeover?]
[Quantify: how many users affected? What data exposed?]

## Proof of Concept
[Request/response showing the vulnerability]

GET /api/v1/users/3/data HTTP/1.1
Host: target.com
Authorization: Bearer <low_privilege_token>

HTTP/1.1 200 OK
{"email": "victim@email.com", "ssn": "123-45-6789", ...}

## Remediation
- Implement proper authorization checks on all API endpoints
- Verify that the authenticated user owns the requested resource
- Use indirect references (session-mapped IDs) instead of sequential IDs
```

### Writing Tips

```
1. Lead with impact — reviewers scan; the first sentence should convey severity
2. Be specific — exact URLs, exact parameters, exact payloads
3. Show don't tell — include raw HTTP requests/responses
4. Estimate affected users — "This affects all 50M users" gets attention
5. Suggest remediation — shows expertise and helps triage
6. Don't inflate severity — be honest; medium bugs with great reports get accepted
7. One bug per report — don't bundle issues
8. Clean up — remove your test data; don't leave XSS payloads live
```

---

## Platform-Specific Tips

### HackerOne

```
- Read the program's scope and policy BEFORE testing
- Use HackerOne's private programs for better signal-to-noise ratio
- Submit to new programs (less competition, more lenient triagers)
- Signal: programs with $$ in the range page usually pay well
- Use Hacktivity to learn what gets accepted
- Duplicate reports are common — be fast on new programs
- Bounties: Critical $2k-$50k, High $500-$5k, Medium $250-$1k
- Build reputation: 3+ accepted reports → private program invites
```

### Bugcrowd

```
- Bugcrowd tends to have stricter triage — be thorough
- Crowdstream (RTBP programs) have competitive bounties
- Bugcrowd University has free training resources
- Programs often have specific testing guidelines — follow them
- Use the submission form properly — severity matters for payout
- Bugcrowd pays via Payoneer/Bank — set up early
```

### General Tips

```
- Start with recon — 80% of bugs are found through thorough enumeration
- Focus on functionality, not just scanners — manual testing wins
- Specialize in 2-3 vulnerability classes (e.g., SSRF + auth + business logic)
- Read disclosed reports on HackerOne Hacktivity for learning
- Set up Burp Suite properly — CA cert, scope, match/replace rules
- Keep notes — Obsidian/Notion with templates per target
- Time management: don't spend >1 week on a single target without findings
- Join Discord communities (Nahamsec, STÖK, Bug Bounty Forum)
```

---

## Automated Recon Pipeline Script

```bash
#!/bin/bash
# recon.sh — Full recon pipeline for a target domain
# Usage: ./recon.sh target.com

set -e
TARGET=$1
OUTDIR="recon_${TARGET}_$(date +%Y%m%d)"
mkdir -p "$OUTDIR"

echo "[1/7] Subdomain enumeration..."
subfinder -d "$TARGET" -all -silent | sort -u > "$OUTDIR/subdomains.txt"
echo "  Found $(wc -l < "$OUTDIR/subdomains.txt") subdomains"

echo "[2/7] DNS resolution..."
cat "$OUTDIR/subdomains.txt" | dnsx -silent -a -resp | awk '{print $1}' | sort -u > "$OUTDIR/resolved.txt"
echo "  Resolved $(wc -l < "$OUTDIR/resolved.txt") domains"

echo "[3/7] HTTP probing..."
cat "$OUTDIR/resolved.txt" | httpx -silent -status-code -title -tech-detect > "$OUTDIR/httpx.txt"
cat "$OUTDIR/httpx.txt" | awk '{print $1}' > "$OUTDIR/live_urls.txt"
echo "  Found $(wc -l < "$OUTDIR/live_urls.txt") live web services"

echo "[4/7] URL discovery..."
cat "$OUTDIR/live_urls.txt" | gau --threads 5 2>/dev/null | sort -u > "$OUTDIR/gau_urls.txt"
katana -list "$OUTDIR/live_urls.txt" -d 3 -jc -silent 2>/dev/null | sort -u > "$OUTDIR/katana_urls.txt"
cat "$OUTDIR/gau_urls.txt" "$OUTDIR/katana_urls.txt" | sort -u > "$OUTDIR/all_urls.txt"
echo "  Found $(wc -l < "$OUTDIR/all_urls.txt") URLs"

echo "[5/7] Nuclei scan..."
nuclei -l "$OUTDIR/live_urls.txt" -severity critical,high -o "$OUTDIR/nuclei_critical.txt" -silent
echo "  Nuclei findings: $(wc -l < "$OUTDIR/nuclei_critical.txt" 2>/dev/null || echo 0)"

echo "[6/7] Directory bruteforce..."
ffuf -w /usr/share/seclists/Discovery/Web-Content/common.txt -u "$TARGET/FUZZ" -mc 200,301,302,403 -of json -o "$OUTDIR/ffuf.json" -s 2>/dev/null

echo "[7/7] Screenshot..."
cat "$OUTDIR/live_urls.txt" | httpx -silent -screenshot -screenshot-timeout 10 2>/dev/null

echo ""
echo "=== Recon Complete ==="
echo "Results in: $OUTDIR/"
echo "Subdomains:  $OUTDIR/subdomains.txt"
echo "Live URLs:   $OUTDIR/live_urls.txt"
echo "All URLs:    $OUTDIR/all_urls.txt"
echo "Nuclei:      $OUTDIR/nuclei_critical.txt"
```

---

## Daily Bug Bounty Workflow

```
Morning:
  1. Check new HackerOne/Bugcrowd programs
  2. Run recon on interesting new targets
  3. Review Nuclei results from overnight scans

Afternoon:
  4. Manual testing on high-value targets
  5. Deep-dive into interesting endpoints found in recon
  6. Write up any findings

Evening:
  7. Submit reports
  8. Read disclosed reports for learning
  9. Update recon pipelines with new tools/templates
```

---

## Pitfalls and Gotchas

1. **Stay in scope** — Testing out-of-scope assets can get you banned
2. **Don't exfiltrate data** — Prove access, don't download/extract real data
3. **No destructive testing** — Don't delete, modify, or DoS production systems
4. **Rate limiting** — Respect rate limits; getting IP banned wastes time
5. **Report fast** — Duplicates happen; the first reporter gets the bounty
6. **Don't use automated scanners blindly** — Nuclei + ffuf find low-hanging fruit; manual testing finds the real bugs
7. **Cloud metadata** — SSRF to 169.254.169.254 is increasingly blocked; try alternative IP formats (0x7f000001, 2130706433)
8. **WAF bypass** — Use encoding, case variation, HTTP/2, chunked transfer to bypass WAFs
