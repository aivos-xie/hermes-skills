# Xiaomi MiMo Provider Configuration

## Provider Details

- **Provider name**: `xiaomi`
- **Base URL**: `https://token-plan-cn.xiaomimimo.com/v1`
- **Auth**: `XIAOMI_API_KEY` env var

## Available Models (as of June 2026)

Official descriptions from [mimo.xiaomi.com](https://mimo.xiaomi.com):

| Model | Type | Official Description |
|-------|------|---------------------|
| `mimo-v2.5` | Text | "A leap in agency and multimodality." — Fast general text, conversation |
| `mimo-v2.5-pro` | Text | "A leap in agentic and long horizon coherence." — Agent tasks, long-context |
| `mimo-v2-pro` | Text | "Global Top-tier agent capabilities." — Top-tier agent model |
| `mimo-v2-omni` | Multimodal | "See, hear, act in the agentic era." — Vision + audio + text |
| `mimo-v2.5-asr` | Audio | "State-of-the-art open-source speech recognition." — STT |
| `mimo-v2.5-tts` | Audio | "Voice synthesis for the agent era." — TTS |
| `mimo-v2.5-tts-voiceclone` | Audio | "Give your agent a voice. Give it a soul." — TTS with voice cloning |
| `mimo-v2.5-tts-voicedesign` | Audio | Custom voice style design |
| `mimo-v2-tts` | Audio | Basic TTS (v2 series) |

## Full Multi-Role Configuration

Configure all MiMo models for a complete multimodal agent:

```bash
# Main text model
hermes config set model.default mimo-v2.5-pro
hermes config set model.provider xiaomi
hermes config set model.base_url https://token-plan-cn.xiaomimimo.com/v1

# Vision (multimodal) — for image analysis
hermes config set auxiliary.vision.provider xiaomi
hermes config set auxiliary.vision.model mimo-v2-omni

# STT — speech recognition
hermes config set stt.enabled true
hermes config set stt.provider xiaomi
hermes config set stt.xiaomi.model mimo-v2.5-asr

# TTS — text to speech
hermes config set tts.provider xiaomi
hermes config set tts.xiaomi.model mimo-v2.5-tts

# Delegation — subagent tasks
hermes config set delegation.model mimo-v2.5-pro
hermes config set delegation.provider xiaomi
```

## Notes

- Gateway restart required after model changes — `systemctl restart hermes-gateway` can hang; see troubleshooting in main SKILL.md
- `mimo-v2-omni` is the only model with vision/multimodal support
- `mimo-v2.5-pro` offers better agent/tool-use than base `mimo-v2.5`
- `mimo-v2-pro` is the top-tier agent model but may be slower
- ASR and TTS models require the xiaomi provider to support audio endpoints
- All models share the same base_url and API key
