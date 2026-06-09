# Volcengine Ark (火山方舟) API Reference

## Overview
Volcengine Ark is ByteDance's model-as-a-service platform. It provides access to Doubao, DeepSeek, Kimi, GLM, MiniMax and other models via a unified OpenAI-compatible API.

## API Details
- **Base URL**: `https://ark.cn-beijing.volces.com/api/v3/chat/completions`
- **Auth**: Bearer token in Authorization header
- **Format**: OpenAI-compatible chat completions
- **API Key format**: `ark-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

## Available Models (as of 2026-06, queried from /api/v3/models)

**推理/对话 (Chat)**
- `deepseek-v4-pro-260425` — 最强推理+编码
- `deepseek-v4-flash-260425` — 快速便宜
- `deepseek-v3-2-251201`
- `doubao-seed-2-0-pro-260215` — 豆包旗舰
- `doubao-seed-2-0-lite-260428` — 轻量
- `doubao-seed-2-0-mini-260428` — 更小
- `doubao-seed-2-0-code-preview-260215` — 代码专用
- `doubao-1-5-pro-32k-250115` / `doubao-1-5-lite-32k-250115`
- `doubao-smart-router-250928` — 自动路由
- `kimi-k2-250905` (Retiring)
- `glm-4-7-251222` / `glm-4-5-air-20250728`
- `qwen3-32b-20250429` / `qwen3-14b` / `qwen3-8b` / `qwen3-0-6b`

**视觉**
- `doubao-1-5-vision-pro-32k-250115`
- `doubao-seed-1-6-vision-250815`

**视频生成**
- `doubao-seedance-2-0-260128` / fast版
- `doubao-seedance-1-5-pro-251215`

**图片生成**
- `doubao-seedream-5-0-260128`
- `doubao-seedream-4-5-251128`

**3D**
- `doubao-seed3d-2-0-260328`
- `hitem3d-2-0-251223`

**Embedding**
- `doubao-embedding-vision-251215` / `250615`

Use `/api/v3/models` endpoint to get the live list (filter `status != 'Shutdown'`).

## Listing Available Models
```bash
curl -s "https://ark.cn-beijing.volces.com/api/v3/models" \
  -H "Authorization: Bearer $ARK_API_KEY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('data', []):
    if m.get('status') != 'Shutdown':
        print(f\"{m['id']} - {m.get('name', '')} - {m.get('status', '')}\")"
```

## Response Format
```json
{
  "choices": [{
    "message": {
      "content": "response text",
      "reasoning_content": "thinking process (for thinking models)"
    }
  }],
  "model": "actual-model-used",
  "usage": {
    "total_tokens": 100,
    "completion_tokens_details": {"reasoning_tokens": 50}
  }
}
```

## CodingPlan vs Regular API
- CodingPlan is a subscription plan with access to multiple models
- Same API endpoint, just different models available
- Can use `auto` mode (no model param) for smart routing
- CodingPlan models may have higher discount coefficients (cost more tokens)

## Pitfalls
1. **Model not found (404)** — Check model ID via `/api/v3/models` endpoint
2. **Timeout** — DeepSeek Pro with thinking enabled can take 30-60s for simple prompts
3. **GitHub downloads from China** — Use `ghproxy.cc` mirror: `https://ghproxy.cc/https://github.com/...`
