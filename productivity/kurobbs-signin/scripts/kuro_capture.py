"""
mitmproxy addon - 捕获库街区登录Token
当检测到kurobbs API返回token时，自动保存到青龙面板

用法: mitmdump -p 5701 --set upstream_cert=false -s kuro_capture.py --set block_global=false
"""
import json
import http.client
from mitmproxy import http, ctx

QL_HOST = "localhost"
QL_PORT = 5700
QL_USER = "aivos"
QL_PASS = "xyh14717461758@"

def get_ql_token():
    conn = http.client.HTTPConnection(QL_HOST, QL_PORT)
    conn.request("POST", "/api/user/login",
        json.dumps({"username": QL_USER, "password": QL_PASS}),
        {"Content-Type": "application/json"})
    resp = conn.getresponse()
    data = json.loads(resp.read())
    conn.close()
    return data["data"]["token"]

def save_to_qinglong(token_value):
    try:
        ql = get_ql_token()
        conn = http.client.HTTPConnection(QL_HOST, QL_PORT)
        conn.request("GET", "/api/envs?searchValue=KURO_TOKEN",
            headers={"Authorization": "Bearer " + ql})
        resp = conn.getresponse()
        envs = json.loads(resp.read())
        conn.close()

        existing = envs.get("data", [])
        conn = http.client.HTTPConnection(QL_HOST, QL_PORT)
        if existing:
            eid = existing[0]["id"]
            body = json.dumps({"id": eid, "name": "KURO_TOKEN", "value": token_value, "remarks": "库街区签到Token"})
            conn.request("PUT", "/api/envs", body, {"Content-Type": "application/json", "Authorization": "Bearer " + ql})
        else:
            body = json.dumps([{"name": "KURO_TOKEN", "value": token_value, "remarks": "库街区签到Token"}])
            conn.request("POST", "/api/envs", body, {"Content-Type": "application/json", "Authorization": "Bearer " + ql})
        resp = conn.getresponse()
        resp.read()
        conn.close()
        ctx.log.info(f"[CAPTURE] Token saved to QingLong! ({token_value[:30]}...)")
        return True
    except Exception as e:
        ctx.log.error(f"[ERROR] save failed: {e}")
        return False

class KuroTokenCapture:
    def __init__(self):
        self.captured = False

    def response(self, flow: http.HTTPFlow):
        if self.captured:
            return

        url = flow.request.pretty_url
        if "api.kurobbs.com" in url and ("sdkLogin" in url or "login" in url or "verify" in url):
            try:
                data = json.loads(flow.response.text)
                ctx.log.info(f"[LOGIN] {url} -> code={data.get('code')}")

                if data.get("code") == 200 and data.get("data"):
                    token = data["data"].get("token", "")
                    if token and len(token) > 20:
                        self.captured = True
                        ctx.log.info(f"[CAPTURE] Got token: {token[:30]}...")
                        if save_to_qinglong(token):
                            self._inject_success(flow)
            except Exception as e:
                ctx.log.error(f"[ERROR] parse response: {e}")

        # Also check response headers for token
        if "api.kurobbs.com" in url and flow.response:
            for header_val in flow.response.headers.get_all("set-cookie"):
                if "token=" in header_val:
                    parts = header_val.split("token=")
                    if len(parts) > 1:
                        token = parts[1].split(";")[0].strip()
                        if token and len(token) > 20 and not self.captured:
                            self.captured = True
                            ctx.log.info(f"[CAPTURE] Cookie token: {token[:30]}...")
                            save_to_qinglong(token)

    def _inject_success(self, flow):
        success_html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>成功</title>
<style>body{font-family:sans-serif;background:#0a0a0a;color:#e0e0e0;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}
.box{text-align:center;background:#1a3a1a;border:2px solid #388e3c;border-radius:16px;padding:40px;max-width:90%}
h1{color:#66bb6a}p{color:#aaa}</style></head>
<body><div class="box"><h1>✅ Token 获取成功！</h1>
<p>已自动保存到青龙面板</p><p>鸣潮/库街区签到任务已就绪</p>
<p style="margin-top:20px;color:#666;font-size:12px">可以关闭此页面，取消手机代理</p>
</div></body></html>"""
        flow.response = http.Response.make(200, success_html, {"Content-Type": "text/html; charset=utf-8"})

addons = [KuroTokenCapture()]
