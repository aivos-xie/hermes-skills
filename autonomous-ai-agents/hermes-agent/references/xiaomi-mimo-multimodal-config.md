# Xiaomi MiMo Multimodal Configuration

## Model Ecosystem

| Model | Type | Use Case |
|-------|------|----------|
| mimo-v2.5 | Text inference | Main conversation (fast) |
| mimo-v2.5-pro | Text inference | Agent tasks, long context coherence |
| mimo-v2-pro | Text inference | Top-tier agent capabilities |
| mimo-v2-omni | Multimodal | Vision + voice + text in one model |
| mimo-v2.5-asr | Speech recognition | Voice-to-text (STT) |
| mimo-v2.5-tts | Text-to-speech | Text-to-voice (TTS) |
| mimo-v2.5-tts-voiceclone | Voice cloning TTS | Mimic specific voices |
| mimo-v2.5-tts-voicedesign | Voice design TTS | Custom voice styles |
| mimo-v2-tts | TTS (v2) | Basic text-to-speech |

## Hermes Configuration for Full MiMo Multimodal

```bash
# Main model
hermes config set model.default mimo-v2-pro
hermes config set model.provider xiaomi

# Vision (image analysis)
hermes config set auxiliary.vision.provider xiaomi
hermes config set auxiliary.vision.model mimo-v2-omni

# STT (speech-to-text)
hermes config set stt.enabled true
hermes config set stt.provider xiaomi
hermes config set stt.xiaomi.model mimo-v2.5-asr

# TTS (text-to-speech)
hermes config set tts.provider xiaomi
hermes config set tts.xiaomi.model mimo-v2.5-tts

# Delegation (subagent tasks)
hermes config set delegation.model mimo-v2.5-pro
hermes config set delegation.provider xiaomi
```

## Provider Details
- Base URL: `https://token-plan-cn.xiaomimimo.com/v1`
- API Key env var: `XIAOMI_API_KEY`
- OpenAI-compatible API format

## Pitfalls

### vision_analyze fails with "Not supported model" even after config set
`auxiliary.vision.*` changes require a session restart (`/reset` or gateway restart). The running session still uses the old model for `vision_analyze`.

**Mid-session workaround** — call the Xiaomi API directly via `execute_code`:

```python
import base64, json, os, requests

img_path = "/path/to/image.jpg"
with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

api_key = ""
with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        if line.strip().startswith("XIAOMI_API_KEY="):
            api_key = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

resp = requests.post(
    "https://token-plan-cn.xiaomimimo.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    json={
        "model": "mimo-v2-omni",
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": "Describe this image in detail."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
        ]}],
        "max_tokens": 2000
    },
    timeout=60
)
print(resp.json()["choices"][0]["message"]["content"])
```

### Configuration drift: base_url / provider mismatch
If `model.base_url` points to one provider (e.g. xiaomi MiMo endpoint) but `model.provider` and `model.default` point to another (e.g. volcengine/deepseek), requests will fail or hit the wrong backend. This happens when multiple `hermes config set` calls partially overwrite each other, or when a model switch command only changes model.default without updating provider/base_url.

**Diagnosis**: `hermes config` — check the "◆ Model" line for conflicting base_url vs provider.

**Fix**: Set all three together:
```bash
hermes config set model.default mimo-v2.5-pro
hermes config set model.provider xiaomi
hermes config set model.base_url https://token-plan-cn.xiaomimimo.com/v1
```
Also check `delegation.model` / `delegation.provider` — those drift independently from the main model config.

### doubao-seed models do NOT support vision
`doubao-seed-2-0-lite-260428` (Volcengine) returns 404 "No endpoints found that support image input". Always configure `auxiliary.vision` with a multimodal-capable model like `mimo-v2-omni`.

## Notes
- mimo-v2.5 is fastest for basic text tasks
- mimo-v2-omni handles images natively (no separate vision model needed if used as main)
- Gateway restart required after config changes
