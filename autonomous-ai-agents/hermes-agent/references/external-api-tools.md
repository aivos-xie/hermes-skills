# Integrating External AI APIs as Hermes Tools

Pattern for adding external AI provider APIs (Volcengine Ark, DashScope, etc.) as callable tools in Hermes.

## Tool File Location

Place tool files in `~/.hermes/tools/` — auto-discovered by Hermes on startup.

## Tool Registration Pattern

```python
import os
import json
import requests
from tools.registry import registry

# API配置
API_BASE_URL = "https://api.example.com/v1/chat/completions"
API_KEY = os.getenv("YOUR_API_KEY", "fallback-key")

def check_requirements() -> bool:
    return bool(API_KEY)

def your_tool_handler(args, **kwargs):
    prompt = args.get("prompt", "")
    if not prompt:
        return json.dumps({"error": "请提供输入"})
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": "your-model-name",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 4096
    }
    
    try:
        response = requests.post(API_BASE_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content
    except Exception as e:
        return json.dumps({"error": str(e)})

registry.register(
    name="your_tool_name",
    toolset="custom",
    schema={
        "name": "your_tool_name",
        "description": "工具描述",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "输入"}
            },
            "required": ["prompt"]
        }
    },
    handler=your_tool_handler,
    check_fn=check_requirements,
    requires_env=["YOUR_API_KEY"],
)
```

## Volcengine Ark API (方舟)

- Base URL: `https://ark.cn-beijing.volces.com/api/v3/chat/completions`
- API Key format: `ark-xxxxx-xxxxx-xxxxx`
- List models: `GET /api/v3/models` (same auth header)
- Response includes `reasoning_content` for thinking models

### CodingPlan Models (as of 2026-06)
- `doubao-seed-2-0-code-preview-260215` — 豆包代码模型
- `deepseek-v4-pro-260425` — DeepSeek V4 Pro (Agent增强)
- `deepseek-v4-flash-260425` — DeepSeek V4 Flash (快速经济)

### Key Pitfalls
- Model names change frequently — always verify with `GET /api/v3/models` first
- Some models require activation in the Volcengine console before use
- Thinking models return `reasoning_content` separately from `content`

## Environment Variables

Set in `~/.hermes/.env`:
```
YOUR_API_KEY=your-key-here
```

## Restart Required

Tools are discovered at startup. After adding a tool file, restart Hermes or use `/reset`.
