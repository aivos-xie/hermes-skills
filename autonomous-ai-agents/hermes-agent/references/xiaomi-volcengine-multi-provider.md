# Xiaomi + Volcengine Multi-Provider Configuration

## Setup Pattern
Main model = Xiaomi MiMo (fixed). Volcengine = sub-agents + fallback.

```bash
# Main model (Xiaomi) - DO NOT CHANGE without explicit "换主模型"
hermes config set model.default mimo-v2.5-pro
hermes config set model.provider xiaomi
hermes config set model.base_url https://token-plan-cn.xiaomimimo.com/v1

# Sub-agent delegation (Volcengine)
hermes config set delegation.model deepseek-v4-pro-260425
hermes config set delegation.provider volcengine

# Auxiliary models
hermes config set auxiliary.vision.provider xiaomi
hermes config set auxiliary.vision.model mimo-v2-omni
hermes config set auxiliary.compression.provider volcengine
hermes config set auxiliary.compression.model deepseek-v4-flash-260425
hermes config set auxiliary.web_extract.provider volcengine
hermes config set auxiliary.web_extract.model deepseek-v4-flash-260425

# Fallback (auto-switch when Xiaomi is down)
hermes config set fallback_providers '["volcengine"]'

# STT (Xiaomi)
hermes config set stt.enabled true
hermes config set stt.provider xiaomi
hermes config set stt.xiaomi.model mimo-v2.5-asr
```

## Available Volcengine Models (as of 2026-06)
```bash
source ~/.hermes/.env && curl -s "https://ark.cn-beijing.volces.com/api/v3/models" \
  -H "Authorization: Bearer $ARK_API_KEY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in sorted(data.get('data', []), key=lambda x: x['id']):
    if m.get('status') != 'Shutdown':
        print(f\"{m['id']:50s} {m.get('status', '')}\")"
```

Key models:
- deepseek-v4-pro-260425 — best reasoning, default sub-agent
- deepseek-v4-flash-260425 — fast, cheap (compression/web)
- doubao-seed-2-0-pro-260215 — Doubao flagship
- doubao-seed-2-0-code-preview-260215 — code specialist
- doubao-smart-router-250928 — auto-routes to best model
- kimi-k2-250905, glm-4-7-251222, qwen3-32b-20250429

## Pitfall: "add" ≠ "replace"
When user says "加入方舟体系" or "add volcengine", they mean auxiliary/sub-agent — NOT replacing the main model. Only change `model.default`/`model.provider` when user explicitly says "换主模型".
