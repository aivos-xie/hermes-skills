# GitHub Research Workflow

## Pattern: Parallel Research → Skill Creation

When the user says "learn from GitHub", "research X", "go study Y":

### Step 1: Decompose into parallel tasks
Split the research domain into 3 categories max (delegate_task limit).

### Step 2: Dispatch parallel subagents
```python
delegate_task(tasks=[
    {"goal": "Research GitHub for [cat A]. Check repos X, Y, Z. Get latest versions, install commands, usage. Return markdown.", "toolsets": ["web", "terminal", "file"]},
    {"goal": "Research GitHub for [cat B]. Return markdown.", "toolsets": ["web", "terminal", "file"]},
    {"goal": "Research GitHub for [cat C]. Return markdown.", "toolsets": ["web", "terminal", "file"]},
])
```

### Step 3: Synthesize into skills
From subagent results, create/update SKILL.md files with:
- Latest version numbers (verified from GitHub API)
- Install commands (from README, not training data)
- Usage examples
- Pitfalls section

### Step 4: Update memory
Add skill names to persistent memory.

## GitHub API tricks (unauthenticated)
- Rate limit: ~60 requests/hour unauthenticated
- `/repos/{owner}/{repo}/releases/latest` → latest version
- `/repos/{owner}/{repo}/tags` → recent tags
- `https://api.github.com/repos/{owner}/{repo}` → star count, description
- `https://raw.githubusercontent.com/{owner}/{repo}/main/README.md` → raw README

## Common pitfalls
- **Subagents may time out** — 3 parallel tasks on mimo-v2.5-pro can take 5-10 min each
- **GitHub API rate limit** — unauthenticated is ~60 req/hr, plan queries carefully
- **Don't report intermediate status** — user doesn't want "Still working..." messages
- **Always verify, don't trust training data** — tools change fast, versions expire
