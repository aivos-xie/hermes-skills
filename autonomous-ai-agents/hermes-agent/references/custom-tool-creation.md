# Creating Custom Tools for Hermes

## Tool Registration Pattern

Hermes tools live in `~/.hermes/tools/` and are auto-discovered via `tools/registry.py`.

### Template: External API Tool

```python
"""
Description of what this tool does
"""
import os
import json
import requests
from tools.registry import registry

# Configuration
API_BASE_URL = "https://api.example.com/v1"
API_KEY = os.getenv("MY_API_KEY", "")

def check_requirements() -> bool:
    return bool(API_KEY)

def tool_handler(args, **kwargs):
    """Handler receives parsed args dict, returns JSON string"""
    prompt = args.get("prompt", "")
    if not prompt:
        return json.dumps({"error": "Missing required parameter"})
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {"prompt": prompt}
    
    try:
        response = requests.post(API_BASE_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return json.dumps({"success": True, "data": result})
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"API call failed: {str(e)}"})

registry.register(
    name="my_tool",
    toolset="custom",  # toolset name for grouping
    schema={
        "name": "my_tool",
        "description": "What this tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Parameter description"
                },
                "mode": {
                    "type": "string",
                    "description": "Mode selection",
                    "default": "default",
                    "enum": ["default", "alternate"]
                }
            },
            "required": ["prompt"]
        }
    },
    handler=tool_handler,
    check_fn=check_requirements,
    requires_env=["MY_API_KEY"],
)
```

### Key Points
- Handler must return a **JSON string**, not a dict
- `check_fn` controls when the tool appears (only when requirements met)
- `requires_env` lists env vars needed (shown in tool availability check)
- Env vars can be set in `~/.hermes/.env`
- Tool changes take effect on **next session** (`/reset` or restart)
- Use `timeout=60` or higher for LLM API calls (they can be slow)

### Multi-Model Pattern
Support multiple models via an enum parameter with a default:

```python
MODELS = {
    "model-a": "model-a-id",
    "model-b": "model-b-id",
}
DEFAULT_MODEL = "model-a"

# In handler:
model_key = args.get("model", DEFAULT_MODEL)
model_id = MODELS.get(model_key)
# If model_id is None, let the API auto-select
if model_id:
    payload["model"] = model_id
```

## Pitfalls

1. **Don't use `from hermes_tools import tool`** — that's for `execute_code` inline tools, not registered tools. Use `from tools.registry import registry` + `registry.register()`.

2. **API key in .env** — Set `ARK_API_KEY=xxx` in `~/.hermes/.env`, not hardcoded. The tool reads via `os.getenv()`.

3. **Timeout for LLM APIs** — Default 15s is too short for code generation. Use `timeout=60` or `timeout=120`.

4. **Tool not showing up** — Check: (a) file in `~/.hermes/tools/`, (b) `check_fn` returns True, (c) env vars set, (d) session restarted.
