"""
Hermes Remote Command API
Deploy on remote server when SSH is unavailable.
Usage: python3 hermes-remote-api.py
"""
from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

# Change this token in production!
TOKEN = os.getenv("HERMES_API_TOKEN", "hermes2024")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'hermes-remote-api'})

@app.route('/exec', methods=['POST'])
def exec_cmd():
    # Verify bearer token
    auth = request.headers.get('Authorization', '')
    if auth != f'Bearer {TOKEN}':
        return jsonify({'error': 'unauthorized'}), 401
    
    data = request.get_json(silent=True) or {}
    cmd = data.get('cmd', '').strip()
    
    if not cmd:
        return jsonify({'error': 'no command provided'}), 400
    
    # Block dangerous commands (optional safety)
    blocked = ['rm -rf /', 'mkfs', 'dd if=', ':(){ :|:& };:']
    if any(b in cmd for b in blocked):
        return jsonify({'error': 'command blocked for safety'}), 403
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=120,
            cwd='/root'
        )
        return jsonify({
            'stdout': result.stdout,
            'stderr': result.stderr,
            'code': result.returncode
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'command timed out (120s)'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("HERMES_API_PORT", "9090"))
    print(f"Starting Hermes Remote API on port {port}")
    print(f"Token: {TOKEN[:4]}...{TOKEN[-4:]}")
    app.run(host='0.0.0.0', port=port)
