// ==UserScript==
// @name         Web App Helper
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Auto-fill and helper for web applications
// @match        *://example.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_setValue
// @grant        GM_getValue
// @connect      your-server.com
// ==/UserScript==

(function() {
    'use strict';

    const API_BASE = 'http://your-server.com';
    let username = GM_getValue('username', '');

    // Create floating UI panel
    function createUI() {
        const panel = document.createElement('div');
        panel.id = 'helper-panel';
        panel.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 99999;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            font-size: 14px;
            min-width: 280px;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        `;

        if (username) {
            panel.innerHTML = `
                <div style="font-weight:bold;font-size:16px;margin-bottom:12px">⚡ Web Helper</div>
                <div style="margin-bottom:8px">👤 ${username}</div>
                <div style="display:flex;gap:8px;flex-wrap:wrap">
                    <button onclick="helper.logout()" 
                            style="padding:8px 12px;background:rgba(255,255,255,0.2);border:none;color:white;border-radius:6px;cursor:pointer">
                        Logout
                    </button>
                    <button onclick="helper.refresh()" 
                            style="padding:8px 12px;background:rgba(255,255,255,0.2);border:none;color:white;border-radius:6px;cursor:pointer">
                        Refresh
                    </button>
                </div>
                <div id="helper-status" style="margin-top:8px;font-size:12px;opacity:0.8">Ready</div>
            `;
            checkStatus();
        } else {
            panel.innerHTML = `
                <div style="font-weight:bold;font-size:16px;margin-bottom:12px">⚡ Web Helper</div>
                <input id="helper-user" placeholder="Username" 
                       style="width:100%;padding:8px;margin-bottom:8px;border:1px solid rgba(255,255,255,0.3);border-radius:6px;background:rgba(255,255,255,0.1);color:white">
                <input id="helper-pass" type="password" placeholder="Password" 
                       style="width:100%;padding:8px;margin-bottom:8px;border:1px solid rgba(255,255,255,0.3);border-radius:6px;background:rgba(255,255,255,0.1);color:white">
                <div style="display:flex;gap:8px">
                    <button onclick="helper.login()" 
                            style="flex:1;padding:8px;background:white;color:#667eea;border:none;border-radius:6px;cursor:pointer;font-weight:bold">
                        Login
                    </button>
                    <button onclick="helper.register()" 
                            style="flex:1;padding:8px;background:rgba(255,255,255,0.2);border:none;color:white;border-radius:6px;cursor:pointer">
                        Register
                    </button>
                </div>
                <div id="helper-status" style="margin-top:8px;font-size:12px;opacity:0.8"></div>
            `;
        }

        document.body.appendChild(panel);
    }

    // API request helper
    function api(path, data, callback) {
        GM_xmlhttpRequest({
            method: 'POST',
            url: API_BASE + path,
            headers: { 'Content-Type': 'application/json' },
            data: JSON.stringify(data),
            onload: function(res) {
                try {
                    callback(null, JSON.parse(res.responseText));
                } catch(e) {
                    callback(e, null);
                }
            },
            onerror: function(err) {
                callback(err, null);
            }
        });
    }

    // Check status/balance
    function checkStatus() {
        api('/api/status', { username: username }, function(err, data) {
            if (data && data.balance !== undefined) {
                setStatus(`Balance: ${data.balance}`);
            }
        });
    }

    // Set status message
    function setStatus(msg) {
        const el = document.getElementById('helper-status');
        if (el) el.textContent = msg;
    }

    // Main helper object
    window.helper = {
        login: function() {
            const u = document.getElementById('helper-user').value.trim();
            const p = document.getElementById('helper-pass').value.trim();
            if (!u || !p) return alert('Please enter username and password');
            
            api('/api/login', { username: u, password: p }, function(err, data) {
                if (data && data.message) {
                    username = u;
                    GM_setValue('username', u);
                    location.reload();
                } else {
                    setStatus(data ? data.error : 'Login failed');
                }
            });
        },

        register: function() {
            const u = document.getElementById('helper-user').value.trim();
            const p = document.getElementById('helper-pass').value.trim();
            if (!u || !p) return alert('Please enter username and password');
            if (u.length < 2 || p.length < 4) return alert('Username min 2 chars, password min 4 chars');
            
            api('/api/register', { username: u, password: p }, function(err, data) {
                if (data && data.message) {
                    alert('Registration successful! Please login.');
                } else {
                    setStatus(data ? data.error : 'Registration failed');
                }
            });
        },

        logout: function() {
            GM_setValue('username', '');
            location.reload();
        },

        refresh: function() {
            checkStatus();
        },

        // Example: Recharge with code
        recharge: function() {
            const code = prompt('Enter recharge code:');
            if (!code) return;
            
            api('/api/recharge', { username: username, code: code }, function(err, data) {
                if (data && data.message) {
                    alert(`Recharged! Balance: ${data.balance}`);
                    checkStatus();
                } else {
                    alert(data ? data.error : 'Recharge failed');
                }
            });
        }
    };

    // Initialize
    createUI();
    
    // Auto-refresh status every 60 seconds
    if (username) {
        setInterval(checkStatus, 60000);
    }
})();
