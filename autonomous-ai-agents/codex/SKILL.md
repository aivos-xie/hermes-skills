---
name: codex
description: "Delegate coding to OpenAI Codex CLI (features, PRs)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Codex, OpenAI, Code-Review, Refactoring]
    related_skills: [claude-code, hermes-agent]
---

# Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex) via the Hermes terminal. Codex is OpenAI's autonomous coding agent CLI.

## When to use

- Building features
- Refactoring
- PR reviews
- Batch issue fixing

Requires the codex CLI and a git repository.

## Prerequisites

- **Codex installed** (two methods):
  - npm: `npm install -g @openai/codex`
  - Standalone binary (Rust, recommended): download from [GitHub Releases](https://github.com/openai/codex/releases)
    - Linux x86_64: `codex-x86_64-unknown-linux-musl.tar.gz`
    - Linux ARM: `codex-aarch64-unknown-linux-musl.tar.gz`
    - macOS ARM: `codex-aarch64-apple-darwin.tar.gz`
    - macOS x86: `codex-x86_64-apple-darwin.tar.gz`
    - Windows x86: `codex-x86_64-pc-windows-msvc.exe.zip`
    - Version naming: `rust-v0.139.0` format (the `rust-` prefix indicates Rust build)
  - Extract and place binary in PATH
- OpenAI auth configured: either `OPENAI_API_KEY` or Codex OAuth credentials
  from the Codex CLI login flow
- **Must run inside a git repository** — Codex refuses to run outside one
- **Network**: needs access to OpenAI API (api.openai.com) — requires proxy on servers without direct access
- Use `pty=true` in terminal calls — Codex is an interactive terminal app

For Hermes itself, `model.provider: openai-codex` uses Hermes-managed Codex
OAuth from `~/.hermes/auth.json` after `hermes auth add openai-codex`. For the
standalone Codex CLI, a valid CLI OAuth session may live under
`~/.codex/auth.json`; do not treat a missing `OPENAI_API_KEY` alone as proof
that Codex auth is missing.

## One-Shot Tasks

```
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

For scratch work (Codex needs a git repo):
```
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

## Background Mode (Long Tasks)

```
# Start in background with PTY
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send input if Codex asks a question
process(action="submit", session_id="<id>", data="yes")

# Kill if needed
process(action="kill", session_id="<id>")
```

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed but auto-approves file changes in workspace |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |

## PR Reviews

Clone to a temp directory for safe review:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## Parallel Issue Fixing with Worktrees

```
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Codex in each
terminal(command="codex --yolo exec 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## Batch PR Reviews

```
# Fetch all PR refs
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# Review multiple PRs in parallel
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87'", workdir="~/project", background=true, pty=true)

# Post results
terminal(command="gh pr comment 86 --body '<review>'", workdir="~/project")
```

## Server Compatibility Check

When user asks "can server X run Codex", check:
```bash
uname -m && free -h && df -h / && cat /etc/os-release | head -3
```

Minimum: x86_64 or aarch64, ~200MB free RAM, ~100MB disk. The binary itself is lightweight — main resource cost is the API call context, not local compute.

**Key pitfall**: Codex needs outbound HTTPS to `api.openai.com`. Servers in China (Alibaba Cloud etc.) without a proxy will fail silently or timeout. Always check network access before recommending installation.

## Custom Providers (Non-OpenAI)

Codex supports non-OpenAI providers via config fields discovered in the config schema:

| Config Key | Purpose |
|------------|---------|
| `model_provider` | Select active provider from the `model_providers` map |
| `model_providers` | Define custom provider entries (extends built-in list) |
| `openai_base_url` | Override the built-in `openai` provider's base URL |
| `model` | Model name to use |

**Quick setup for OpenAI-compatible APIs** (DeepSeek, Together AI, etc.):
```bash
# In ~/.codex/config.json or via environment:
export OPENAI_BASE_URL="https://api.deepseek.com/v1"
export OPENAI_API_KEY="sk-..."
export MODEL="deepseek-coder"
```

**Works with**: DeepSeek, Together AI, SiliconFlow, Ollama (local), vLLM, any OpenAI-compatible endpoint.

**Caveat**: Codex requires strong tool-calling and code-understanding capabilities. Smaller/weaker models will produce poor results. GPT-4-class or equivalent recommended.

## Pitfalls

1. **Always use `pty=true`** — Codex is an interactive terminal app and hangs without a PTY
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch
3. **Large binary downloads** — Standalone binaries are 60-100MB. On bandwidth-limited servers, ask user before downloading. Consider npm install instead if Node.js is available.
4. **China servers** — api.openai.com is blocked. Need proxy or alternative endpoint.
5. **`--full-auto` for building** — auto-approves changes within the sandbox
6. **Background for long tasks** — use `background=true` and monitor with `process` tool
7. **Don't interfere** — monitor with `poll`/`log`, be patient with long-running tasks
8. **Parallel is fine** — run multiple Codex processes at once for batch work
9. **Cancel cleanup** — if a large binary download is interrupted, `rm` partial files immediately (`codex-*.tar.gz`, `codex-*.zip`)
