---
name: multi-agent-dispatch
description: "多子Agent并行派发系统 — 按任务类型自动选择最优模型"
version: 1.0.0
author: aivos
metadata:
  hermes:
    tags: [agents, delegation, parallel, multi-model]
---

# 多子Agent派发系统

## 可用Agent池

| Agent代号 | 模型 | Provider | 擅长 | 输入能力 |
|-----------|------|----------|------|----------|
| `reasoner` | deepseek-v4-pro-260425 | volcengine | 深度推理、复杂分析、代码审查 | 文本 |
| `worker` | deepseek-v4-flash-260425 | volcengine | 快速执行、一般任务、搜索提取 | 文本 |
| `multimodal` | doubao-seed-2-0-lite-260428 | volcengine | 多模态理解、轻量辅助 | 文本+图片+视频+音频 |
| `vision` | mimo-v2-omni | xiaomi | 图像分析、视觉问答 | 文本+图片 |
| `main` | mimo-v2.5-pro | xiaomi | 主Agent、综合任务 | 文本 |

## 派发规则

### 单任务 — 直接派发
```python
# 深度推理任务
delegate_task(goal="...", model={"model":"deepseek-v4-pro-260425","provider":"volcengine"})

# 快速执行任务
delegate_task(goal="...", model={"model":"deepseek-v4-flash-260425","provider":"volcengine"})

# 多模态任务（需看图/视频）
delegate_task(goal="...", model={"model":"doubao-seed-2-0-lite-260428","provider":"volcengine"})

# 视觉分析
delegate_task(goal="...", model={"model":"mimo-v2-omni","provider":"xiaomi"})
```

### 批量并行 — 最多3个同时
```python
delegate_task(tasks=[
    {"goal": "分析XXX的架构设计", "model":{"model":"deepseek-v4-pro-260425","provider":"volcengine"}},
    {"goal": "搜索XXX的最新文档", "model":{"model":"deepseek-v4-flash-260425","provider":"volcengine"}},
    {"goal": "检查XXX的截图内容", "model":{"model":"doubao-seed-2-0-lite-260428","provider":"volcengine"}}
])
```

## 任务→Agent匹配

| 任务类型 | 首选Agent | 原因 |
|----------|-----------|------|
| 代码审查/架构分析 | reasoner | 需要深度理解 |
| 调试/排错 | reasoner | 需要推理链 |
| 文档搜索/总结 | worker | 速度优先 |
| 数据提取/格式化 | worker | 机械任务 |
| 图片/视频内容分析 | multimodal | 原生多模态 |
| 网页内容提取 | worker | 速度快 |
| 翻译 | worker | 够用 |
| 创意写作 | reasoner | 质量优先 |
| 简单问答 | multimodal | 最便宜 |
| OCR/图像理解 | vision | 小米视觉 |

## 辅助模型自动分配

以下由Hermes自动调度，无需手动派发：
- **压缩**: deepseek-v4-flash (上下文压缩)
- **Curator**: deepseek-v4-pro (技能维护需深度理解)
- **视觉辅助**: doubao-seed-2-0-lite-260428 (多模态)
- **Web提取**: deepseek-v4-flash
- **标题生成**: doubao-seed-2-0-lite-260428
- **审批判断**: deepseek-v4-flash

## config.yaml 配置

实际配置示例（2026-06-09）：

```yaml
# 主模型
model:
  default: mimo-v2.5-pro
  provider: xiaomi
  base_url: https://token-plan-cn.xiaomimimo.com/v1

# 子Agent默认模型
delegation:
  model: deepseek-v4-flash-260425
  provider: volcengine
  max_concurrent_children: 3
  child_timeout_seconds: 600
  max_spawn_depth: 1

# Provider定义
providers:
  volcengine:
    base_url: https://ark.cn-beijing.volces.com/api/v3
    api_key_env: ARK_API_KEY
    provider_type: openai

# 辅助模型
auxiliary:
  compression:
    model: deepseek-v4-flash-260425
    provider: volcengine
  curator:
    model: deepseek-v4-pro-260425
    provider: volcengine
  vision:
    model: doubao-seed-2-0-lite-260428
    provider: volcengine
  web_extract:
    model: deepseek-v4-flash-260425
    provider: volcengine
  approval:
    model: deepseek-v4-flash-260425
    provider: volcengine
  kanban_decomposer:
    model: doubao-seed-2-0-lite-260428
    provider: volcengine
  title_generation:
    model: doubao-seed-2-0-lite-260428
    provider: volcengine
  profile_describer:
    model: doubao-seed-2-0-lite-260428
    provider: volcengine
  skills_hub:
    model: doubao-seed-2-0-lite-260428
    provider: volcengine
  triage_specifier:
    model: doubao-seed-2-0-lite-260428
    provider: volcengine
  mcp:
    model: doubao-seed-2-0-lite-260428
    provider: volcengine
```

## 注意事项

1. `delegate_task` 的 model 参数格式: `{"model":"模型ID","provider":"provider名"}`
2. 批量派发上限3个（delegation.max_concurrent_children=3）
3. 子Agent无记忆，必须在context中传入所有必要信息
4. 子Agent不能递归派发（max_spawn_depth=1）
5. 子Agent超时600秒（delegation.child_timeout_seconds）
