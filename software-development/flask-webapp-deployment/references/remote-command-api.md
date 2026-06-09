# Remote Command Execution API Pattern

A secure pattern for executing shell commands remotely via HTTP API.

## Implementation

```python
import subprocess

@app.route('/api/exec', methods=['POST'])
def api_exec():
    data = request.json
    token = data.get('token', '')
    
    # Validate token
    if token != os.getenv('API_TOKEN', 'your-secret-token'):
        return jsonify({'error': 'unauthorized'}), 401
    
    cmd = data.get('cmd', '')
    if not cmd:
        return jsonify({'error': 'No command provided'}), 400
    
    try:
        # Use Popen for better control
        proc = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(timeout=120)
        
        return jsonify({
            'stdout': stdout.decode('utf-8', errors='replace'),
            'stderr': stderr.decode('utf-8', errors='replace'),
            'code': proc.returncode
        })
    except subprocess.TimeoutExpired:
        proc.kill()
        return jsonify({'error': 'Command timed out'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## Usage Examples

### Basic Command

```bash
curl -X POST http://server/api/exec \
  -H "Content-Type: application/json" \
  -d '{"token":"your-secret","cmd":"echo hello && hostname"}'
```

### Response Format

```json
{
  "stdout": "hello\nmyserver\n",
  "stderr": "",
  "code": 0
}
```

### Error Response

```json
{
  "error": "unauthorized"
}
```

## Security Considerations

1. **Always use authentication** - Never expose without token
2. **Limit source IPs** - Use firewall rules to restrict access
3. **Timeout commands** - Prevent hanging processes
4. **Log all commands** - For audit trail
5. **Sanitize inputs** - Be careful with shell=True

## Firewall Configuration

```bash
# Only allow specific IP
sudo firewall-cmd --permanent --add-rich-rule='
  rule family="ipv4"
  source address="YOUR_IP/32"
  port protocol="tcp" port="8080"
  accept'

# Or use iptables
sudo iptables -A INPUT -p tcp --dport 8080 -s YOUR_IP -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8080 -j DROP
```

## Alternative: SSH Key-Based Access

Instead of HTTP API, consider SSH key-based access:

```bash
# Generate key pair
ssh-keygen -t ed25519 -f ~/.ssh/mykey -N ""

# Add public key to server
echo "ssh-ed25519 AAAA..." >> ~/.ssh/authorized_keys

# Execute commands
ssh -i ~/.ssh/mykey user@server "command"
```

## Use Cases

1. **Remote server management** - Execute commands without SSH
2. **Automated deployments** - CI/CD pipelines
3. **Monitoring scripts** - Health checks and alerts
4. **Batch operations** - Execute on multiple servers

## Complete Example with Logging

```python
import logging
from datetime import datetime

logging.basicConfig(filename='/var/log/api-exec.log', level=logging.INFO)

@app.route('/api/exec', methods=['POST'])
def api_exec():
    data = request.json
    token = data.get('token', '')
    
    if token != os.getenv('API_TOKEN'):
        logging.warning(f"Unauthorized access attempt from {request.remote_addr}")
        return jsonify({'error': 'unauthorized'}), 401
    
    cmd = data.get('cmd', '')
    logging.info(f"[{datetime.now()}] Executing: {cmd}")
    
    try:
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(timeout=120)
        
        result = {
            'stdout': stdout.decode('utf-8', errors='replace'),
            'stderr': stderr.decode('utf-8', errors='replace'),
            'code': proc.returncode
        }
        
        logging.info(f"[{datetime.now()}] Completed with code {proc.returncode}")
        return jsonify(result)
    except Exception as e:
        logging.error(f"[{datetime.now()}] Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
```
