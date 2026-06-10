---
name: knowledge-base-mcp
version: 1.0.0
description: Build AI knowledge bases with MCP Server — structured docs, search index, Agent integration
tags: [knowledge-base, mcp, ai-agent, structured-data, documentation]
triggers:
  - 知识库
  - knowledge base
  - MCP Server
  - Agent接入
  - 结构化知识
  - 技术文档站
---

# 知识库 + MCP Server 架构

## 核心概念

知识库不是原始文档堆砌，而是**AI专用的结构化知识**：
- **patterns** — 架构模式、设计模式、代码模式
- **decisions** — 技术选型、架构决策、方案对比
- **strategies** — 重构策略、测试策略、部署策略
- **references** — API参考、命令速查、配置指南

## 项目结构

```
project/
├── index.html              # 首页（搜索+分类+Agent接入）
├── search.html             # 搜索页（fuse.js前端搜索）
├── doc.html                # 文档查看器（客户端渲染markdown）
├── download.html           # 下载Skill页
├── mcp.html                # Agent接入指南
├── about.html              # 关于/贡献指南
├── docs/                   # Markdown文档（按分类目录）
│   ├── {分类名}/
│   │   └── *.md
├── assets/
│   ├── app.js              # 共享JS（header/footer/搜索）
│   ├── style.css           # 样式
│   ├── search-index.json   # 搜索索引（fuse.js用）
│   ├── categories.json     # 分类统计
│   ├── all-docs.json       # 全部文档元数据
│   ├── knowledge-index.json # AI专用结构化索引
│   └── modules.json        # Skill模块列表
└── mcp-server/
    ├── index.js            # MCP Server（4个Tool）
    └── package.json
```

## 关键设计决策

### 文档用Markdown，不用HTML
- 原始README → 清洗 → 保留.md格式
- 客户端用 `marked.js` 渲染
- 体积小（38MB vs 150MB+ HTML）
- 更新方便，git diff清晰

### 搜索用fuse.js前端搜索
- 零服务器成本
- 搜索索引是JSON文件
- 支持模糊匹配

### Agent接入用MCP协议
- 任何MCP兼容Agent都能调用
- 4个Tool: search_knowledge / get_document / list_categories / list_skills
- 本地运行或通过npx

## MCP Server 实现要点

```javascript
// 核心Tool定义
server.tool("search_knowledge", "搜索知识库", {
  query: z.string(),
  category: z.string().optional(),
  limit: z.number().optional().default(5),
}, async ({ query, category, limit }) => {
  // 从search-index.json搜索
  // 返回{title, category, summary, url}
});

server.tool("get_document", "获取文档详情", {
  path: z.string(),  // 如 docs/python/README.md_xxx.md
}, async ({ path }) => {
  // 读取本地markdown文件
  // 返回截断内容（前8000字符）
});
```

## 数据清洗Pipeline

处理GitHub README的关键步骤：
1. 去掉 `# https://raw.githubusercontent.com/...` 头
2. 去掉 `Collected:` / `Source:` / `Size:` 元数据行
3. 去掉 shields.io badge图片链接
4. 去掉居中的 `<p align="center">` badge块
5. 去掉base64编码的长行（>500字符）
6. 去掉HTML注释 `<!-- ... -->`
7. 合并多余空行

## SSH批量数据传输

**不要逐个文件SSH读取，太慢！**
```bash
# 错误：每个文件一次SSH调用（234个文件 = 234次连接）
ssh server "cat file1" > local1
ssh server "cat file2" > local2

# 正确：批量scp
scp server:/path/docs/*/*.md ./local/docs/

# 更好：rsync（增量同步）
rsync -avz server:/path/docs/ ./local/docs/
```

## Pitfalls

- **Node.js MCP Server需要ESM** — package.json必须有 `"type": "module"`
- **marked.js CDN** — 用 `https://cdn.jsdelivr.net/npm/marked/marked.min.js`
- **搜索索引更新** — 每次数据更新后必须重新生成search-index.json
- **文档路径** — doc.html用 `?file=docs/xxx/yyy.md` 参数加载
- **GitHub Pages 1GB限制** — 纯markdown够用，加图片会超
