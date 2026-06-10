---
name: hermes-agent
description: "Configure, extend, or contribute to Hermes Agent."
version: 2.1.0
author: Hermes Agent + Teknium
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---

# Hermes Agent

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, messaging platforms, and IDEs. It belongs to the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw — autonomous coding and task-execution agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, DeepSeek, local models, and 15+ others) and runs on Linux, macOS, and WSL.

What makes Hermes different:

- **Self-improving through skills** — Hermes learns from experience by saving reusable procedures as skills. When it solves a complex problem, discovers a workflow, or gets corrected, it can persist that knowledge as a skill document that loads into future sessions. Skills accumulate over time, making the agent better at your specific tasks and environment.
- **Persistent memory across sessions** — remembers who you are, your preferences, environment details, and lessons learned. Pluggable memory backends (built-in, Honcho, Mem0, and more) let you choose how memory works.
- **Multi-platform gateway** — the same agent runs on Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, and 10+ other platforms with full tool access, not just chat.
- **Provider-agnostic** — swap models and providers mid-workflow without changing anything else. Credential pools rotate across multiple API keys automatically.
- **Profiles** — run multiple independent Hermes instances with isolated configs, sessions, skills, and memory.
- **Extensible** — plugins, MCP servers, custom tools, webhook triggers, cron scheduling, and the full Python ecosystem.

People use Hermes for software development, research, system administration, data analysis, content creation, home automation, and anything else that benefits from an AI agent with persistent context and full system access.

**This skill helps you work with Hermes Agent effectively** — setting it up, configuring features, spawning additional agent instances, troubleshooting issues, finding the right commands and settings, and understanding how the system works when you need to extend or contribute to it.

**Docs:** https://hermes-agent.nousresearch.com/docs/
- `references/docker-china-cloud.md` — Docker mirror config for Chinese cloud servers (Alibaba, Tencent, etc.) + QingLong panel deployment
- `references/xiaomi-mimo-multimodal-config.md` — Xiaomi MiMo multimodal model setup (vision, STT, TTS)
- `references/docker-china-cloud.md` — Docker mirror config for Chinese cloud servers (Alibaba, Tencent, etc.) + QingLong panel deployment
**Docker on Alibaba Cloud:** `references/docker-alibaba-cloud-linux.md` — Installation workarounds
**External AI API Tools:** `references/external-api-tools.md` — Integrate external AI APIs (Volcengine Ark, DashScope, etc.) as Hermes tools
**Weixin QR Login:** `references/weixin-qr-login-setup.md` — Programmatic QR login workaround (avoid interactive wizard)
**Skill Sync & Backup:** `references/skill-sync-github.md` — Automated GitHub sync with sensitive info filtering
**QQ Bot File Limits:** `references/qqbot-file-transfer.md` — File type support limitations
**Alibaba Cloud Security:** `references/alibaba-cloud-security.md` — ECS security hardening
**Volcengine Ark API:** `references/volcengine-ark-api.md` — 火山引擎方舟API接入（CodingPlan Agent模式）
**Custom Tool Creation:** `references/custom-tool-creation.md` — Creating custom Hermes tools

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Interactive chat (default)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider
hermes model

# Check health
hermes doctor
```

---

## CLI Reference

### Global Flags

```
hermes [flags] [command]

  --version, -V             Show version
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --pass-session-id         Include session ID in system prompt
```

No subcommand defaults to `chat`.

### Chat

```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  -m, --model MODEL         Model (e.g. anthropic/claude-sonnet-4)
  -t, --toolsets LIST       Comma-separated toolsets
  --provider PROVIDER       Force provider (openrouter, anthropic, nous, etc.)
  -v, --verbose             Verbose output
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --source TAG              Session source tag (default: cli)
```

### Configuration

```
hermes setup [section]      Interactive wizard (model|terminal|gateway|tools|agent)
hermes model                Interactive model/provider picker
hermes config               View current config
hermes config edit          Open config.yaml in $EDITOR
hermes config set KEY VAL   Set a config value
hermes config path          Print config.yaml path
hermes config env-path      Print .env path
hermes config check         Check for missing/outdated config
hermes config migrate       Update config with new options
hermes login [--provider P] OAuth login (nous, openai-codex)
hermes logout               Clear stored auth
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Show component status
```

### Tools & Skills

```
hermes tools                Interactive tool enable/disable (curses UI)
hermes tools list           Show all tools and status
hermes tools enable NAME    Enable a toolset
hermes tools disable NAME   Disable a toolset

hermes skills list          List installed skills
hermes skills search QUERY  Search the skills hub
hermes skills install ID    Install a skill (ID can be a hub identifier OR a direct https://…/SKILL.md URL; pass --name to override when frontmatter has no name)
hermes skills inspect ID    Preview without installing
hermes skills config        Enable/disable skills per platform
hermes skills check         Check for updates
hermes skills update        Update outdated skills
hermes skills uninstall N   Remove a hub skill
hermes skills publish PATH  Publish to registry
hermes skills browse        Browse all available skills
hermes skills tap add REPO  Add a GitHub repo as skill source
```

### MCP Servers

```
hermes mcp serve            Run Hermes as an MCP server
hermes mcp add NAME         Add an MCP server (--url or --command)
hermes mcp remove NAME      Remove an MCP server
hermes mcp list             List configured servers
hermes mcp test NAME        Test connection
hermes mcp configure NAME   Toggle tool selection
```

### Gateway (Messaging Platforms)

```
hermes gateway run          Start gateway foreground
hermes gateway install      Install as background service
hermes gateway start/stop   Control the service
hermes gateway restart      Restart the service
hermes gateway status       Check status
hermes gateway setup        Configure platforms
```

Supported platforms: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Home Assistant, DingTalk, Feishu, WeCom, BlueBubbles (iMessage), Weixin (WeChat), API Server, Webhooks. Open WebUI connects via the API Server adapter.

Platform docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### Sessions

```
hermes sessions list        List recent sessions
hermes sessions browse      Interactive picker
hermes sessions export OUT  Export to JSONL
hermes sessions rename ID T Rename a session
hermes sessions delete ID   Delete a session
hermes sessions prune       Clean up old sessions (--older-than N days)
hermes sessions stats       Session store statistics
```

### Cron Jobs

```
hermes cron list            List jobs (--all for disabled)
hermes cron create SCHED    Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         Edit schedule, prompt, delivery
hermes cron pause/resume ID Control job state
hermes cron run ID          Trigger on next tick
hermes cron remove ID       Delete a job
hermes cron status          Scheduler status
```

### Webhooks

```
hermes webhook subscribe N  Create route at /webhooks/<name>
hermes webhook list         List subscriptions
hermes webhook remove NAME  Remove a subscription
hermes webhook test NAME    Send a test POST
```

### Profiles

```
hermes profile list         List all profiles
hermes profile create NAME  Create (--clone, --clone-all, --clone-from)
hermes profile use NAME     Set sticky default
hermes profile delete NAME  Delete a profile
hermes profile show NAME    Show details
hermes profile alias NAME   Manage wrapper scripts
hermes profile rename A B   Rename a profile
hermes profile export NAME  Export to tar.gz
hermes profile import FILE  Import from archive
```

### Credential Pools

```
hermes auth add             Interactive credential wizard
hermes auth list [PROVIDER] List pooled credentials
hermes auth remove P INDEX  Remove by provider + index
hermes auth reset PROVIDER  Clear exhaustion status
```

### Other

```
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
hermes honcho setup/status  Honcho memory integration (requires honcho plugin)
hermes memory setup/status/off  Memory provider config
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
```

---

## Slash Commands (In-Session)

Type these during an interactive chat session. New commands land fairly
often; if something below looks stale, run `/help` in-session for the
authoritative list or see the [live slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands).
The registry of record is `hermes_cli/commands.py` — every consumer
(autocomplete, Telegram menu, Slack mapping, `/help`) derives from it.

### Session Control
```
/new (/reset)        Fresh session
/clear               Clear screen + new session (CLI)
/retry               Resend last message
/undo                Remove last exchange
/title [name]        Name the session
/compress            Manually compress context
/stop                Kill background processes
/rollback [N]        Restore filesystem checkpoint
/snapshot [sub]      Create or restore state snapshots of Hermes config/state (CLI)
/background <prompt> Run prompt in background
/queue <prompt>      Queue for next turn
/steer <prompt>      Inject a message after the next tool call without interrupting
/agents (/tasks)     Show active agents and running tasks
/resume [name]       Resume a named session
/goal [text|sub]     Set a standing goal Hermes works on across turns until achieved
                     (subcommands: status, pause, resume, clear)
/redraw              Force a full UI repaint (CLI)
```

### Configuration
```
/config              Show config (CLI)
/model [name]        Show or change model
/personality [name]  Set personality
/reasoning [level]   Set reasoning (none|minimal|low|medium|high|xhigh|show|hide)
/verbose             Cycle: off → new → all → verbose
/voice [on|off|tts]  Voice mode
/yolo                Toggle approval bypass
/busy [sub]          Control what Enter does while Hermes is working (CLI)
                     (subcommands: queue, steer, interrupt, status)
/indicator [style]   Pick the TUI busy-indicator style (CLI)
                     (styles: kaomoji, emoji, unicode, ascii)
/footer [on|off]     Toggle gateway runtime-metadata footer on final replies
/skin [name]         Change theme (CLI)
/statusbar           Toggle status bar (CLI)
```

### Tools & Skills
```
/tools               Manage tools (CLI)
/toolsets            List toolsets (CLI)
/skills              Search/install skills (CLI)
/skill <name>        Load a skill into session
/reload-skills       Re-scan ~/.hermes/skills/ for added/removed skills
/reload              Reload .env variables into the running session (CLI)
/reload-mcp          Reload MCP servers
/cron                Manage cron jobs (CLI)
/curator [sub]       Background skill maintenance (status, run, pin, archive, …)
/kanban [sub]        Multi-profile collaboration board (tasks, links, comments)
/plugins             List plugins (CLI)
```

### Gateway
```
/approve             Approve a pending command (gateway)
/deny                Deny a pending command (gateway)
/restart             Restart gateway (gateway)
/sethome             Set current chat as home channel (gateway)
/update              Update Hermes to latest (gateway)
/topic [sub]         Enable or inspect Telegram DM topic sessions (gateway)
/platforms (/gateway) Show platform connection status (gateway)
```

### Utility
```
/branch (/fork)      Branch the current session
/fast                Toggle priority/fast processing
/browser             Open CDP browser connection
/history             Show conversation history (CLI)
/save                Save conversation to file (CLI)
/copy [N]            Copy the last assistant response to clipboard (CLI)
/paste               Attach clipboard image (CLI)
/image               Attach local image file (CLI)
```

### Info
```
/help                Show commands
/commands [page]     Browse all commands (gateway)
/usage               Token usage
/insights [days]     Usage analytics
/gquota              Show Google Gemini Code Assist quota usage (CLI)
/status              Session info (gateway)
/profile             Active profile info
/debug               Upload debug report (system info + logs) and get shareable links
```

### Exit
```
/quit (/exit, /q)    Exit CLI
```

---

## Key Paths & Config

```
~/.hermes/config.yaml       Main configuration
~/.hermes/.env              API keys and secrets
$HERMES_HOME/skills/        Installed skills
~/.hermes/sessions/         Session transcripts
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

Profiles use `~/.hermes/profiles/<name>/` with the same layout.

### Config Sections

Edit with `hermes config edit` or `hermes config set section.key value`.

| Section | Key options |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length` |
| `agent` | `max_turns` (90), `tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `tool_progress`, `show_reasoning`, `show_cost` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider` |
| `security` | `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `base_url`, `api_key`, `max_iterations` (50), `reasoning_effort` |
| `checkpoints` | `enabled`, `max_snapshots` (50) |
| `auxiliary.compression` | `model`, `provider`, `api_key`, `base_url`, `timeout` — context compression model |
| `auxiliary.curator` | `model`, `provider`, `api_key`, `base_url`, `timeout` — curator/review model |
| `auxiliary.vision` | `model`, `provider`, `api_key`, `base_url` — vision/image analysis model |

Full config reference: https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### Providers

20+ providers supported. Set via `hermes model` or `hermes setup`.

| Provider | Auth | Key env var |
|----------|------|-------------|
| OpenRouter | API key | `OPENROUTER_API_KEY` |
| Anthropic | API key | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes auth` |
| OpenAI Codex | OAuth | `hermes auth` |
| GitHub Copilot | Token | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API key | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| DeepSeek | API key | `DEEPSEEK_API_KEY` |
| xAI / Grok | API key | `XAI_API_KEY` |
| Hugging Face | Token | `HF_TOKEN` |
| Z.AI / GLM | API key | `GLM_API_KEY` |
| MiniMax | API key | `MINIMAX_API_KEY` |
| MiniMax CN | API key | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API key | `KIMI_API_KEY` |
| Alibaba / DashScope | API key | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API key | `XIAOMI_API_KEY` |
| Kilo Code | API key | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API key | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API key | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API key | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| Custom endpoint | Config | `model.base_url` + `model.api_key` in config.yaml |
| GitHub Copilot ACP | External | `COPILOT_CLI_PATH` or Copilot CLI |

Full provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers

### Toolsets

Enable/disable via `hermes tools` (interactive) or `hermes tools enable/disable NAME`.

| Toolset | What it provides |
|---------|-----------------|
| `web` | Web search and content extraction |
| `search` | Web search only (subset of `web`) |
| `browser` | Browser automation (Browserbase, Camofox, or local Chromium) |
| `terminal` | Shell commands and process management |
| `file` | File read/write/search/patch |
| `code_execution` | Sandboxed Python execution |
| `vision` | Image analysis |
| `image_gen` | AI image generation |
| `video` | Video analysis and generation |
| `tts` | Text-to-speech |
| `skills` | Skill browsing and management |
| `memory` | Persistent cross-session memory |
| `session_search` | Search past conversations |
| `delegation` | Subagent task delegation |
| `cronjob` | Scheduled task management |
| `clarify` | Ask user clarifying questions |
| `messaging` | Cross-platform message sending |
| `todo` | In-session task planning and tracking |
| `kanban` | Multi-agent work-queue tools (gated to workers) |
| `debugging` | Extra introspection/debug tools (off by default) |
| `safe` | Minimal, low-risk toolset for locked-down sessions |
| `spotify` | Spotify playback and playlist control |
| `homeassistant` | Smart home control (off by default) |
| `discord` | Discord integration tools |
| `discord_admin` | Discord admin/moderation tools |
| `feishu_doc` | Feishu (Lark) document tools |
| `feishu_drive` | Feishu (Lark) drive tools |
| `yuanbao` | Yuanbao integration tools |
| `rl` | Reinforcement learning tools (off by default) |
| `moa` | Mixture of Agents (off by default) |

Full enumeration lives in `toolsets.py` as the `TOOLSETS` dict; `_HERMES_CORE_TOOLS` is the default bundle most platforms inherit from.

Tool changes take effect on `/reset` (new session). They do NOT apply mid-conversation to preserve prompt caching.

---

## Security & Privacy Toggles

Common "why is Hermes doing X to my output / tool calls / commands?" toggles — and the exact commands to change them. Most of these need a fresh session (`/reset` in chat, or start a new `hermes` invocation) because they're read once at startup.

### Secret redaction in tool output

Secret redaction is **off by default** — tool output (terminal stdout, `read_file`, web content, subagent summaries, etc.) passes through unmodified. If the user wants Hermes to auto-mask strings that look like API keys, tokens, and secrets before they enter the conversation context and logs:

```bash
hermes config set security.redact_secrets true       # enable globally
```

**Restart required.** `security.redact_secrets` is snapshotted at import time — toggling it mid-session (e.g. via `export HERMES_REDACT_SECRETS=true` from a tool call) will NOT take effect for the running process. Tell the user to run `hermes config set security.redact_secrets true` in a terminal, then start a new session. This is deliberate — it prevents an LLM from flipping the toggle on itself mid-task.

Disable again with:
```bash
hermes config set security.redact_secrets false
```

### PII redaction in gateway messages

Separate from secret redaction. When enabled, the gateway hashes user IDs and strips phone numbers from the session context before it reaches the model:

```bash
hermes config set privacy.redact_pii true    # enable
hermes config set privacy.redact_pii false   # disable (default)
```

### Command approval prompts

By default (`approvals.mode: manual`), Hermes prompts the user before running shell commands flagged as destructive (`rm -rf`, `git reset --hard`, etc.). The modes are:

- `manual` — always prompt (default)
- `smart` — use an auxiliary LLM to auto-approve low-risk commands, prompt on high-risk
- `off` — skip all approval prompts (equivalent to `--yolo`)

```bash
hermes config set approvals.mode smart       # recommended middle ground
hermes config set approvals.mode off         # bypass everything (not recommended)
```

Per-invocation bypass without changing config:
- `hermes --yolo …`
- `export HERMES_YOLO_MODE=1`

Note: YOLO / `approvals.mode: off` does NOT turn off secret redaction. They are independent.

### Shell hooks allowlist

Some shell-hook integrations require explicit allowlisting before they fire. Managed via `~/.hermes/shell-hooks-allowlist.json` — prompted interactively the first time a hook wants to run.

### Disabling the web/browser/image-gen tools

To keep the model away from network or media tools entirely, open `hermes tools` and toggle per-platform. Takes effect on next session (`/reset`). See the Tools & Skills section above.

---

## Voice & Transcription

### STT (Voice → Text)

Voice messages from messaging platforms are auto-transcribed.

Provider priority (auto-detected):
1. **Local faster-whisper** — free, no API key: `pip install faster-whisper`
2. **Groq Whisper** — free tier: set `GROQ_API_KEY`
3. **OpenAI Whisper** — paid: set `VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral** — set `MISTRAL_API_KEY`

Config:
```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

### TTS (Text → Voice)

| Provider | Env var | Free? |
|----------|---------|-------|
| Edge TTS | None | Yes (default) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | Paid |
| MiniMax | `MINIMAX_API_KEY` | Paid |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | Paid |
| NeuTTS (local) | None (`pip install neutts[all]` + `espeak-ng`) | Free |

Voice commands: `/voice on` (voice-to-voice), `/voice tts` (always voice), `/voice off`.

---

## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses — separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

### One-Shot Mode

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

Hermes uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### Multi-Agent Coordination

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### Session Resume

```
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### Remote Server Sub-Agent (SSH + tmux)

Deploy Hermes on a remote server and control it from the local agent via SSH. The remote agent runs persistently in tmux; the local agent sends commands and reads output over SSH.

**Setup steps:**
```bash
# 1. Install deps on remote
sshpass -p '$PASS' ssh root@$REMOTE "yum install -y git tmux"  # or apt

# 2. Clone Hermes
sshpass -p '$PASS' ssh root@$REMOTE "cd /opt && git clone --depth 1 https://github.com/NousResearch/hermes-agent.git"

# 3. Create venv and install
sshpass -p '$PASS' ssh root@$REMOTE "cd /opt/hermes-agent && python3 -m venv venv && source venv/bin/activate && pip install -e . -q"

# 4. Configure (write config + .env on remote)
sshpass -p '$PASS' ssh root@$REMOTE "mkdir -p /root/.hermes && cat > /root/.hermes/config.yaml << 'EOF'
model:
  default: mimo-v2.5-pro
  provider: xiaomi
  base_url: https://token-plan-cn.xiaomimimo.com/v1
agent:
  max_turns: 50
terminal:
  timeout: 120
EOF"

# 5. Start in tmux
sshpass -p '$PASS' ssh root@$REMOTE "tmux new-session -d -s hermes-agent -x 120 -y 40"
sshpass -p '$PASS' ssh root@$REMOTE "tmux send-keys -t hermes-agent 'cd /opt/hermes-agent && source venv/bin/activate && export XIAOMI_API_KEY=\$KEY && hermes chat --yolo' Enter"

# 6. Send commands
sshpass -p '$PASS' ssh root@$REMOTE "tmux send-keys -t hermes-agent 'your message' Enter"

# 7. Read output
sshpass -p '$PASS' ssh root@$REMOTE "tmux capture-pane -t hermes-agent -p -S -30"
```

**Control script pattern** (save locally as `hz-agent.sh`):
```bash
#!/bin/bash
SERVER="x.x.x.x"; PASS="xxx"; SESSION="hermes-agent"
case "$1" in
  send)  sshpass -p "$PASS" ssh root@$SERVER "tmux send-keys -t $SESSION '$2' Enter" ;;
  read)  sshpass -p "$PASS" ssh root@$SERVER "tmux capture-pane -t $SESSION -p -S -${2:-30}" ;;
  status) sshpass -p "$PASS" ssh root@$SERVER "tmux has-session -t $SESSION 2>/dev/null && echo 'running' || echo 'stopped'" ;;
  restart) # kill + re-create tmux session + re-launch hermes ;;
esac
```

**Pitfalls:**
- `hermes chat -q '中文'` fails because argparse treats CJK as a subcommand. Use `hermes -q '中文'` or pipe: `echo 'msg' | hermes chat`
- `sshpass` + SSH may redact secrets in tool output. Write .env on the remote server directly via `python3 -c "..."` rather than shell interpolation.
- The `--yolo` flag is needed for non-interactive operation (no approval prompts).
- `-Q` (quiet) suppresses the banner for cleaner output parsing.
- Wait 8-10 seconds after starting hermes in tmux before sending the first message — it needs time to initialize.

See `references/remote-agent-deployment.md` for full worked example.

### Tips

- **Prefer `delegate_task` for quick subtasks** — less overhead than spawning a full process
- **Use `-w` (worktree mode)** when spawning agents that edit code — prevents git conflicts
- **Set timeouts** for one-shot mode — complex tasks can take 5-10 minutes
- **Use `hermes chat -q` for fire-and-forget** — no PTY needed
- **Use tmux for interactive sessions** — raw PTY mode has `\\r` vs `\\n` issues with prompt_toolkit
- **For scheduled tasks**, use the `cronjob` tool instead of spawning — handles delivery and retry

---

## Durable & Background Systems

Four systems run alongside the main conversation loop. Quick reference
here; full developer notes live in `AGENTS.md`, user-facing docs under
`website/docs/user-guide/features/`.

### Delegation (`delegate_task`)

Synchronous subagent spawn — the parent waits for the child's summary
before continuing its own loop. Isolated context + terminal session.

- **Single:** `delegate_task(goal, context, toolsets)`.
- **Batch:** `delegate_task(tasks=[{goal, ...}, ...])` runs children in
  parallel, capped by `delegation.max_concurrent_children` (default 3).
- **Roles:** `leaf` (default; cannot re-delegate) vs `orchestrator`
  (can spawn its own workers, bounded by `delegation.max_spawn_depth`).
- **Not durable.** If the parent is interrupted, the child is
  cancelled. For work that must outlive the turn, use `cronjob` or
  `terminal(background=True, notify_on_complete=True)`.

Config: `delegation.*` in `config.yaml`.

### Cron (scheduled jobs)

Durable scheduler — `cron/jobs.py` + `cron/scheduler.py`. Drive it via
the `cronjob` tool, the `hermes cron` CLI (`list`, `add`, `edit`,
`pause`, `resume`, `run`, `remove`), or the `/cron` slash command.

- **Schedules:** duration (`"30m"`, `"2h"`), "every" phrase
  (`"every monday 9am"`), 5-field cron (`"0 9 * * *"`), or ISO timestamp.
- **Per-job knobs:** `skills`, `model`/`provider` override, `script`
  (pre-run data collection; `no_agent=True` makes the script the whole
  job), `context_from` (chain job A's output into job B), `workdir`
  (run in a specific dir with its `AGENTS.md` / `CLAUDE.md` loaded),
  multi-platform delivery.
- **Invariants:** 3-minute hard interrupt per run, `.tick.lock` file
  prevents duplicate ticks across processes, cron sessions pass
  `skip_memory=True` by default, and cron deliveries are framed with a
  header/footer instead of being mirrored into the target gateway
  session (keeps role alternation intact).

User docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/cron

### Curator (skill lifecycle)

Background maintenance for agent-created skills. Tracks usage, marks
idle skills stale, archives stale ones, keeps a pre-run tar.gz backup
so nothing is lost.

- **CLI:** `hermes curator <verb>` — `status`, `run`, `pause`, `resume`,
  `pin`, `unpin`, `archive`, `restore`, `prune`, `backup`, `rollback`.
- **Slash:** `/curator <subcommand>` mirrors the CLI.
- **Scope:** only touches skills with `created_by: "agent"` provenance.
  Bundled + hub-installed skills are off-limits. **Never deletes** —
  max destructive action is archive. Pinned skills are exempt from
  every auto-transition and every LLM review pass.
- **Telemetry:** sidecar at `~/.hermes/skills/.usage.json` holds
  per-skill `use_count`, `view_count`, `patch_count`,
  `last_activity_at`, `state`, `pinned`.

Config: `curator.*` (`enabled`, `interval_hours`, `min_idle_hours`,
`stale_after_days`, `archive_after_days`, `backup.*`).
User docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/curator

### Kanban (multi-agent work queue)

Durable SQLite board for multi-profile / multi-worker collaboration.
Users drive it via `hermes kanban <verb>`; dispatcher-spawned workers
see a focused `kanban_*` toolset gated by `HERMES_KANBAN_TASK` so the
schema footprint is zero outside worker processes.

- **CLI verbs (common):** `init`, `create`, `list` (alias `ls`),
  `show`, `assign`, `link`, `unlink`, `comment`, `complete`, `block`,
  `unblock`, `archive`, `tail`. Less common: `watch`, `stats`, `runs`,
  `log`, `dispatch`, `daemon`, `gc`.
- **Worker toolset:** `kanban_show`, `kanban_complete`, `kanban_block`,
  `kanban_heartbeat`, `kanban_comment`, `kanban_create`, `kanban_link`.
- **Dispatcher** runs inside the gateway by default
  (`kanban.dispatch_in_gateway: true`) — reclaims stale claims,
  promotes ready tasks, atomically claims, spawns assigned profiles.
  Auto-blocks a task after ~5 consecutive spawn failures.
- **Isolation:** board is the hard boundary (workers get
  `HERMES_KANBAN_BOARD` pinned in env); tenant is a soft namespace
  within a board for workspace-path + memory-key isolation.

User docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban

---

## Windows-Specific Quirks

Hermes runs natively on Windows (PowerShell, cmd, Windows Terminal, git-bash
mintty, VS Code integrated terminal). Most of it just works, but a handful
of differences between Win32 and POSIX have bitten us — document new ones
here as you hit them so the next person (or the next session) doesn't
rediscover them from scratch.

### Input / Keybindings

**Alt+Enter doesn't insert a newline.** Windows Terminal intercepts Alt+Enter
at the terminal layer to toggle fullscreen — the keystroke never reaches
prompt_toolkit. Use **Ctrl+Enter** instead. Windows Terminal delivers
Ctrl+Enter as LF (`c-j`), distinct from plain Enter (`c-m` / CR), and the
CLI binds `c-j` to newline insertion on `win32` only (see
`_bind_prompt_submit_keys` + the Windows-only `c-j` binding in `cli.py`).
Side effect: the raw Ctrl+J keystroke also inserts a newline on Windows —
unavoidable, because Windows Terminal collapses Ctrl+Enter and Ctrl+J to
the same keycode at the Win32 console API layer. No conflicting binding
existed for Ctrl+J on Windows, so this is a harmless side effect.

mintty / git-bash behaves the same (fullscreen on Alt+Enter) unless you
disable Alt+Fn shortcuts in Options → Keys. Easier to just use Ctrl+Enter.

**Diagnosing keybindings.** Run `python scripts/keystroke_diagnostic.py`
(repo root) to see exactly how prompt_toolkit identifies each keystroke
in the current terminal. Answers questions like "does Shift+Enter come
through as a distinct key?" (almost never — most terminals collapse it
to plain Enter) or "what byte sequence is my terminal sending for
Ctrl+Enter?" This is how the Ctrl+Enter = c-j fact was established.

### Config / Files

**HTTP 400 "No models provided" on first run.** `config.yaml` was saved
with a UTF-8 BOM (common when Windows apps write it). Re-save as UTF-8
without BOM. `hermes config edit` writes without BOM; manual edits in
Notepad are the usual culprit.

### `execute_code` / Sandbox

**WinError 10106** ("The requested service provider could not be loaded
or initialized") from the sandbox child process — it can't create an
`AF_INET` socket, so the loopback-TCP RPC fallback fails before
`connect()`. Root cause is usually **not** a broken Winsock LSP; it's
Hermes's own env scrubber dropping `SYSTEMROOT` / `WINDIR` / `COMSPEC`
from the child env. Python's `socket` module needs `SYSTEMROOT` to locate
`mswsock.dll`. Fixed via the `_WINDOWS_ESSENTIAL_ENV_VARS` allowlist in
`tools/code_execution_tool.py`. If you still hit it, echo `os.environ`
inside an `execute_code` block to confirm `SYSTEMROOT` is set. Full
diagnostic recipe in `references/execute-code-sandbox-env-windows.md`.

### Testing / Contributing

**`scripts/run_tests.sh` doesn't work as-is on Windows** — it looks for
POSIX venv layouts (`.venv/bin/activate`). The Hermes-installed venv at
`venv/Scripts/` has no pip or pytest either (stripped for install size).
Workaround: install `pytest + pytest-xdist + pyyaml` into a system Python
3.11 user site, then invoke pytest directly with `PYTHONPATH` set:

```bash
"/c/Program Files/Python311/python" -m pip install --user pytest pytest-xdist pyyaml
export PYTHONPATH="$(pwd)"
"/c/Program Files/Python311/python" -m pytest tests/foo/test_bar.py -v --tb=short -n 0
```

Use `-n 0`, not `-n 4` — `pyproject.toml`'s default `addopts` already
includes `-n`, and the wrapper's CI-parity guarantees don't apply off POSIX.

**POSIX-only tests need skip guards.** Common markers already in the codebase:
- Symlinks — elevated privileges on Windows
- `0o600` file modes — POSIX mode bits not enforced on NTFS by default
- `signal.SIGALRM` — Unix-only (see `tests/conftest.py::_enforce_test_timeout`)
- Winsock / Windows-specific regressions — `@pytest.mark.skipif(sys.platform != "win32", ...)`

Use the existing skip-pattern style (`sys.platform == "win32"` or
`sys.platform.startswith("win")`) to stay consistent with the rest of the
suite.

### Path / Filesystem

**Line endings.** Git may warn `LF will be replaced by CRLF the next time
Git touches it`. Cosmetic — the repo's `.gitattributes` normalizes. Don't
let editors auto-convert committed POSIX-newline files to CRLF.

**Forward slashes work almost everywhere.** `C:/Users/...` is accepted by
every Hermes tool and most Windows APIs. Prefer forward slashes in code
and logs — avoids shell-escaping backslashes in bash.

---

## Provider-Specific References

- `references/mimo-provider-setup.md` — Xiaomi MiMo model configuration for multimodal agent (vision, ASR, TTS)
- `references/docker-china-mirrors.md` — Working Docker mirrors for China + QingLong panel setup + API patterns

- **QQ Bot file transfer**: PDF and other document types may not auto-download. Ask user for screenshots or cloud links. See `references/qqbot-file-transfer.md`.
- **Weixin (WeChat) gateway setup**: QR login via two-phase Python script (curses UI not automatable), DM policy requirement, iLink Bot limitations. See `references/weixin-gateway-setup.md`.
- **Alibaba Cloud Security:** `references/alibaba-cloud-security.md` — ECS security hardening
- **Xiaomi + Volcengine Multi-Provider:** `references/xiaomi-volcengine-multi-provider.md` — Full setup pattern for Xiaomi main + Volcengine auxiliary/sub-agents

## Backup & Restore
- `references/hermes-backup-restore.md` — Full backup/restore procedures, selective restore, compression tips

## Deployment & Operations References

- `references/remote-agent-deployment.md` — Full worked example: deploying Hermes on a remote server via SSH + tmux, with control script template
- `references/remote-code-modification-pitfalls.md` — Pitfalls when modifying Python/code on remote servers via SSH
- `references/paid-api-key-system.md` — Reusable pattern for adding license key validation to FastAPI backends
- `references/weixin-qr-login-setup.md` — Weixin/WeChat QR login bypass for phone users (two-phase Python script approach)

## Multi-Provider Model Configuration

When the user wants to "add" a provider (e.g., "加入方舟体系"), they mean ADD it as auxiliary/sub-agent — NOT replace the main model. Common mistake: changing `model.default` or `model.provider` when the user only wants delegation/auxiliary models updated.

**Config keys for multi-provider setup:**
```bash
# Main model (DO NOT CHANGE unless user explicitly says "换主模型")
hermes config set model.default mimo-v2.5-pro
hermes config set model.provider xiaomi
hermes config set model.base_url https://token-plan-cn.xiaomimimo.com/v1

# Sub-agent delegation (what delegate_task uses)
hermes config set delegation.model deepseek-v4-pro-260425
hermes config set delegation.provider volcengine

# Auxiliary: vision, compression, web extract, etc.
hermes config set auxiliary.vision.model mimo-v2-omni
hermes config set auxiliary.vision.provider xiaomi
hermes config set auxiliary.compression.model deepseek-v4-flash-260425
hermes config set auxiliary.compression.provider volcengine

# Fallback (auto-switch when main model is down)
hermes config set fallback_providers '["volcengine"]'
```

**Pitfall: "add X" ≠ "replace main model"**
- User says "加入方舟" → set delegation/auxiliary to volcengine, leave `model.*` alone
- User says "换主模型" → only then change `model.default` and `model.provider`
- User says "不要更改主模型" → NEVER touch `model.*` keys
- When in doubt, ask: "你是要换主模型，还是加为辅助？"

**Listing available models from Volcengine Ark:**
```bash
source ~/.hermes/.env && curl -s "https://ark.cn-beijing.volces.com/api/v3/models" \
  -H "Authorization: Bearer $ARK_API_KEY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in sorted(data.get('data', []), key=lambda x: x['id']):
    if m.get('status') != 'Shutdown':
        print(f\"{m['id']:50s} {m.get('status', '')}\")"
```

---

## Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `pip install faster-whisper` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes login` — re-authenticate OAuth providers
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### Context compression 401 / AuthenticationError
Compression and curator models under `auxiliary.*` need explicit `api_key` in config.yaml — the provider's env var (e.g. `ARK_API_KEY`) is NOT auto-inherited. Fix:
```bash
hermes config set auxiliary.compression.api_key '${ARK_API_KEY}'
hermes config set auxiliary.curator.api_key '${ARK_API_KEY}'
```
Config path is `auxiliary.compression` (NOT `models.compression`). Verify with:
```python
python3 -c "import yaml; c=yaml.safe_load(open('$HOME/.hermes/config.yaml')); print(c.get('auxiliary',{}).get('compression',{}))"
```
Restart gateway after fixing: `hermes gateway restart`.

**Bulk fix for multiple empty api_keys:** If many auxiliary sections have empty api_keys (common after fresh setup), fix them all at once:
```python
import yaml
with open('config.yaml') as f:
    cfg = yaml.safe_load(f)
count = 0
for section_name, section in cfg.items():
    if isinstance(section, dict):
        for k, v in section.items():
            if isinstance(v, dict) and v.get('provider') == 'volcengine' and v.get('api_key') == '':
                v['api_key'] = '${ARK_API_KEY}'
                count += 1
            elif isinstance(v, dict):
                for k2, v2 in v.items():
                    if isinstance(v2, dict) and v2.get('provider') == 'volcengine' and v2.get('api_key') == '':
                        v2['api_key'] = '${ARK_API_KEY}'
                        count += 1
with open('config.yaml', 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)
print(f'Fixed {count} empty api_keys')
```
This fixes compression, curator, vision, kanban_decomposer, mcp, profile_describer, skills_hub, title_generation, triage_specifier, web_extract — all at once.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `/skill name` or `hermes -s name`

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`
- **Gateway restart hangs/times out**: `systemctl restart hermes-gateway` can hang for 60-180s. Workaround: kill processes directly with `pkill -9 -f "hermes.*gateway"` then `sudo systemctl start hermes-gateway`, or just wait — the service usually comes back on its own.

### Pairing (DM authorization)
- `hermes pairing list` — show pending codes + approved users
- `hermes pairing approve <platform> <code>` — approve a pending request
- `hermes pairing revoke <platform> <user_id>` — revoke access
- **Pitfall:** pairing codes expire. If `approve` says "not found or expired", check `hermes pairing list` — the user may already be approved.
- **Pitfall:** don't use `python3 -m hermes.cli.main pairing` — the module path is wrong. Use `hermes pairing` CLI directly.

### Cron jobs with SSH commands blocked by security scan
When a cron job runs in agent mode (default), the Tirith security scan blocks SSH-related commands (`sshpass`, `ssh`, etc.) because there's no user online to approve them. The job reports "被安全策略拦截" (blocked by security policy).

**Fix:** Use `no_agent=True` with a bash script — this skips the LLM and security scan entirely, running the script directly:
```bash
# Create the monitoring script
cat > ~/.hermes/scripts/collector/monitor.sh << 'EOF'
#!/bin/bash
HOST="hz-server"
COUNT=$(ssh -o ConnectTimeout=5 $HOST "ps aux | grep main | grep -v grep | wc -l" 2>/dev/null)
if [ -z "$COUNT" ] || [ "$COUNT" -lt 20 ]; then
    echo "⚠️ 进程异常: $COUNT 个"
fi
EOF
chmod +x ~/.hermes/scripts/collector/monitor.sh
```
Then update the cron job:
```
cronjob(action="update", job_id="...", no_agent=True, script="collector/monitor.sh", prompt="")
```
**Key rules for `no_agent=True` scripts:**
- Empty stdout = silent (nothing delivered to user) — design scripts to stay quiet when everything is normal
- Non-empty stdout = delivered as message
- Non-zero exit = error alert
- Script path resolves under `~/.hermes/scripts/`
- `.sh`/`.bash` runs via bash, everything else via Python

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **QQ Bot gateway setup**: QR code scan flow, config format pitfalls (env vars not top-level YAML), pairing approval, custom stop keywords. See `references/qqbot-gateway-setup.md`.
- **Weixin (WeChat) setup**: Two-phase QR login script (can't automate `hermes gateway setup` via PTY), DM policy requirement, iLink bot limitations. See `references/weixin-gateway-setup.md`.
- **Weixin (WeChat) gateway setup**: QR login via two-phase Python script (curses UI not automatable), `WEIXIN_DM_POLICY=open` required or DMs silently rejected, iLink Bot limitations. See `references/weixin-gateway-setup.md`.
- **QQ Bot file transfer**: PDF and other document types may not auto-download. Ask user for screenshots or cloud links. See `references/qqbot-file-transfer.md`.

## Deployment
- **QQ Bot file transfer**: PDF and other document types may not auto-download. Ask user for screenshots or cloud links. See `references/qqbot-file-transfer.md`.ry.vision.model <model_name>
```

---

## Alternatives & Migration

Hermes belongs to a family of personal AI assistants. Key alternatives:

| Feature | Hermes Agent | OpenClaw 🦞 |
|---------|-------------|-------------|
| Stars | Smaller | 378k+ (very popular) |
| Platforms | 15+ (Telegram, Discord, QQ, WeChat, etc.) | 24+ (adds WhatsApp, Signal, iMessage, LINE, etc.) |
| Skills | Manual + hub | 5400+ community skills |
| Voice | STT/TTS providers | macOS/iOS/Android native voice |
| Config | YAML + CLI | `openclaw onboard` wizard |
| Models | Any provider | Any provider |
| License | MIT | MIT |

**When to consider OpenClaw:**
- Need WhatsApp, Signal, or iMessage support
- Want a large pre-built skill library
- Prefer a more mature community/ecosystem

**When to stay with Hermes:**
- Already configured and working
- Need deep Python ecosystem integration
- Want fine-grained control over tools and config
- Using Hermes-specific features (profiles, kanban, credential pools)

**Migrating from OpenClaw to Hermes:**
```bash
hermes claw migrate
```

**Evaluating OpenClaw:** Install on a spare server first to test without disrupting existing Hermes setup.

## Where to Find Things

| Looking for... | Location |
|----------------|----------|
| Config options | `hermes config edit` or [Configuration docs](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| Available tools | `hermes tools list` or [Tools reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| Slash commands | `/help` in session or [Slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| Skills catalog | `hermes skills browse` or [Skills catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| Provider setup | `hermes model` or [Providers guide](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| Platform setup | `hermes gateway setup` or [Messaging docs](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP servers | `hermes mcp list` or [MCP guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| Profiles | `hermes profile list` or [Profiles docs](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| Cron jobs | `hermes cron list` or [Cron docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| Memory | `hermes memory status` or [Memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| Env variables | `hermes config env-path` or [Env vars reference](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI commands | `hermes --help` or [CLI reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| Gateway logs | `~/.hermes/logs/gateway.log` |
| Session files | `~/.hermes/sessions/` or `hermes sessions browse` |
| Source code | `~/.hermes/hermes-agent/` |

---

## Contributor Quick Reference

For occasional contributors and PR authors. Full developer docs: https://hermes-agent.nousresearch.com/docs/developer-guide/

### Project Layout

```
hermes-agent/
├── run_agent.py          # AIAgent — core conversation loop
├── model_tools.py        # Tool discovery and dispatch
├── toolsets.py           # Toolset definitions
├── cli.py                # Interactive CLI (HermesCLI)
├── hermes_state.py       # SQLite session store
├── agent/                # Prompt builder, context compression, memory, model routing, credential pooling, skill dispatch
├── hermes_cli/           # CLI subcommands, config, setup, commands
│   ├── commands.py       # Slash command registry (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG, env var definitions
│   └── main.py           # CLI entry point and argparse
├── tools/                # One file per tool
│   └── registry.py       # Central tool registry
├── gateway/              # Messaging gateway
│   └── platforms/        # Platform adapters (telegram, discord, etc.)
├── cron/                 # Job scheduler
├── tests/                # ~3000 pytest tests
└── website/              # Docusaurus docs site
```

Config: `~/.hermes/config.yaml` (settings), `~/.hermes/.env` (API keys).

### Adding a Tool (3 files)

**1. Create `tools/your_tool.py`:**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. Add to `toolsets.py`** → `_HERMES_CORE_TOOLS` list.

Auto-discovery: any `tools/*.py` file with a top-level `registry.register()` call is imported automatically — no manual list needed.

All handlers must return JSON strings. Use `get_hermes_home()` for paths, never hardcode `~/.hermes`.

### Adding a Slash Command

1. Add `CommandDef` to `COMMAND_REGISTRY` in `hermes_cli/commands.py`
2. Add handler in `cli.py` → `process_command()`
3. (Optional) Add gateway handler in `gateway/run.py`

All consumers (help text, autocomplete, Telegram menu, Slack mapping) derive from the central registry automatically.

### Agent Loop (High Level)

```
run_conversation():
  1. Build system prompt
  2. Loop while iterations < max:
     a. Call LLM (OpenAI-format messages + tool schemas)
     b. If tool_calls → dispatch each via handle_function_call() → append results → continue
     c. If text response → return
  3. Context compression triggers automatically near token limit
```

### Testing

```bash
python -m pytest tests/ -o 'addopts=' -q   # Full suite
python -m pytest tests/tools/ -q            # Specific area
```

- Tests auto-redirect `HERMES_HOME` to temp dirs — never touch real `~/.hermes/`
- Run full suite before pushing any change
- Use `-o 'addopts='` to clear any baked-in pytest flags

**Windows contributors:** `scripts/run_tests.sh` currently looks for POSIX venvs (`.venv/bin/activate` / `venv/bin/activate`) and will error out on Windows where the layout is `venv/Scripts/activate` + `python.exe`. The Hermes-installed venv at `venv/Scripts/` also has no `pip` or `pytest` — it's stripped for end-user install size. Workaround: install pytest + pytest-xdist + pyyaml into a system Python 3.11 user site (`/c/Program Files/Python311/python -m pip install --user pytest pytest-xdist pyyaml`), then run tests directly:

```bash
export PYTHONPATH="$(pwd)"
"/c/Program Files/Python311/python" -m pytest tests/tools/test_foo.py -v --tb=short -n 0
```

Use `-n 0` (not `-n 4`) because `pyproject.toml`'s default `addopts` already includes `-n`, and the wrapper's CI-parity story doesn't apply off-POSIX.

**Cross-platform test guards:** tests that use POSIX-only syscalls need a skip marker. Common ones already in the codebase:
- Symlink creation → `@pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require elevated privileges on Windows")` (see `tests/cron/test_cron_script.py`)
- POSIX file modes (0o600, etc.) → `@pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX mode bits not enforced on Windows")` (see `tests/hermes_cli/test_auth_toctou_file_modes.py`)
- `signal.SIGALRM` → Unix-only (see `tests/conftest.py::_enforce_test_timeout`)
- Live Winsock / Windows-specific regression tests → `@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific regression")`

**Monkeypatching `sys.platform` is not enough** when the code under test also calls `platform.system()` / `platform.release()` / `platform.mac_ver()`. Those functions re-read the real OS independently, so a test that sets `sys.platform = "linux"` on a Windows runner will still see `platform.system() == "Windows"` and route through the Windows branch. Patch all three together:

```python
monkeypatch.setattr(sys, "platform", "linux")
monkeypatch.setattr(platform, "system", lambda: "Linux")
monkeypatch.setattr(platform, "release", lambda: "6.8.0-generic")
```

See `tests/agent/test_prompt_builder.py::TestEnvironmentHints` for a worked example.

### Extending the system prompt's execution-environment block

Factual guidance about the host OS, user home, cwd, terminal backend, and shell (bash vs. PowerShell on Windows) is emitted from `agent/prompt_builder.py::build_environment_hints()`. This is also where the WSL hint and per-backend probe logic live. The convention:

- **Local terminal backend** → emit host info (OS, `$HOME`, cwd) + Windows-specific notes (hostname ≠ username, `terminal` uses bash not PowerShell).
- **Remote terminal backend** (anything in `_REMOTE_TERMINAL_BACKENDS`: `docker, singularity, modal, daytona, ssh, vercel_sandbox, managed_modal`) → **suppress** host info entirely and describe only the backend. A live `uname`/`whoami`/`pwd` probe runs inside the backend via `tools.environments.get_environment(...).execute(...)`, cached per process in `_BACKEND_PROBE_CACHE`, with a static fallback if the probe times out.
- **Key fact for prompt authoring:** when `TERMINAL_ENV != "local"`, *every* file tool (`read_file`, `write_file`, `patch`, `search_files`) runs inside the backend container, not on the host. The system prompt must never describe the host in that case — the agent can't touch it.

Full design notes, the exact emitted strings, and testing pitfalls:
`references/prompt-builder-environment-hints.md`.

**Refactor-safety pattern (POSIX-equivalence guard):** when you extract inline logic into a helper that adds Windows/platform-specific behavior, keep a `_legacy_<name>` oracle function in the test file that's a verbatim copy of the old code, then parametrize-diff against it. Example: `tests/tools/test_code_execution_windows_env.py::TestPosixEquivalence`. This locks in the invariant that POSIX behavior is bit-for-bit identical and makes any future drift fail loudly with a clear diff.

### Commit Conventions

```
type: concise subject line

Optional body.
```

Types: `fix:`, `feat:`, `refactor:`, `docs:`, `chore:`

### Key Rules

- **Never break prompt caching** — don't change context, tools, or system prompt mid-conversation
- **Message role alternation** — never two assistant or two user messages in a row
- Use `get_hermes_home()` from `hermes_constants` for all paths (profile-safe)
- Config values go in `config.yaml`, secrets go in `.env`
- New tools need a `check_fn` so they only appear when requirements are met
