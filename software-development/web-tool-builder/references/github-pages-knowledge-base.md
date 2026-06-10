# GitHub Pages Knowledge Base + MCP Server

## 决策树：国内用户托管方案

| 场景 | 最佳选择 | 原因 |
|------|----------|------|
| 免费+开源 | **GitHub Pages** | 免费，国内偶尔慢但能访问 |
| 免费+全球CDN | Cloudflare Pages | 国内不稳定，不推荐 |
| 国内用户+有服务器 | 阿里云nginx | 最快，但占用服务器资源 |

**关键决策：** 用户说"我的服务器是租的"→ 用GitHub Pages，不占服务器资源。

## 架构：Markdown文档 + MCP Server

```
project/
├── index.html              # 首页（搜索+分类+Agent接入）
├── knowledge.html          # 知识库浏览页（分类+文档列表+搜索）
├── search.html             # 搜索页（fuse.js前端搜索）
├── doc.html                # 文档查看器（客户端渲染markdown）
├── download.html           # 下载Skill页
├── mcp.html                # Agent接入指南
├── about.html              # 关于/贡献指南
├── docs/                   # Markdown文档（按分类目录）
│   ├── {分类名}/
│   │   └── *.md
├── assets/
│   ├── app.js              # 共享JS（header/footer）
│   ├── style.css           # 样式
│   ├── search-index.json   # 搜索索引（fuse.js）
│   ├── categories.json     # 分类统计
│   ├── all-docs.json       # 全部文档元数据
│   ├── knowledge-index.json # AI专用结构化索引
│   └── modules.json        # Skill模块列表
└── mcp-server/
    ├── index.js            # MCP Server（4个Tool）
    └── package.json
```

**关键决策：文档用Markdown不用HTML**
- 体积小（38MB vs 150MB+）
- 更新方便，git diff清晰
- 客户端用marked.js渲染

## GitHub Pages 部署（无需gh CLI）

```bash
# 1. 创建仓库
TOKEN=$(python3 -c "...")
curl -s -X POST https://api.github.com/user/repos \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"repo-name","public":true}'

# 2. 推送
git remote add origin "https://USER:${TOKEN}@github.com/USER/repo.git"
git push -u origin main

# 3. 开启Pages
curl -s -X POST "https://api.github.com/repos/USER/repo/pages" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source":{"branch":"main","path":"/"}}'
```

## MCP Server 核心实现

```javascript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "tech-knowledge", version: "1.0.0" });

// Tool 1: 搜索
server.tool("search_knowledge", "搜索知识库", {
  query: z.string(), category: z.string().optional(), limit: z.number().optional().default(5),
}, async ({ query, category, limit }) => {
  const q = query.toLowerCase();
  let results = searchData.filter(d => {
    const text = `${d.title} ${d.summary} ${d.category}`.toLowerCase();
    return text.includes(q) && (!category || d.category.includes(category));
  }).slice(0, limit);
  return { content: [{ type: "text", text: JSON.stringify({ results, total: results.length }) }] };
});

// Tool 2: 获取文档
server.tool("get_document", "获取文档详情", {
  path: z.string(),
}, async ({ path }) => {
  const content = readFileSync(join(__dirname, path), "utf-8");
  return { content: [{ type: "text", text: content.slice(0, 8000) }] };
});

// Tool 3: 列出分类
server.tool("list_categories", "列出所有分类", {}, async () => { /* ... */ });

// Tool 4: 列出Skill
server.tool("list_skills", "列出可下载Skill", {}, async () => { /* ... */ });

const transport = new StdioServerTransport();
await server.connect(transport);
```

**package.json必须：** `"type": "module"` (ESM)

## 数据清洗Pipeline

```python
def clean_readme(content):
    # 1. 去掉 # https://raw.githubusercontent.com/... 头
    # 2. 去掉 Collected: / Source: / Size: 元数据
    # 3. 去掉 shields.io badge图片
    # 4. 去掉 <p align="center"> badge块
    # 5. 去掉 base64 长行（>500字符）
    # 6. 去掉 HTML注释
    # 7. 合并多余空行
```

**二次过滤（数据质量）：**
```python
def is_useful(doc):
    title = doc['title'].strip()
    if len(title) < 3: return False
    if title.lower() in ['readme', 'iii', 'index', 'test', 'demo']: return False
    if title.startswith('[') and title.endswith(']'): return False
    if re.match(r'^[\d\._-]+$', title): return False
    return True

# 去重（同名项目只保留一个）
seen = set()
for doc in docs:
    key = doc['title'].lower().strip()
    if key in seen: continue
    if not is_useful(doc): continue
    seen.add(key)
    unique_docs.append(doc)

# 删除只有1篇文档的分类（质量太低）
valid_cats = {name: docs for name, docs in cat_docs.items() if len(docs) >= 2}
```

**效果：** 203篇→95篇，60分类→32分类

## SSH批量数据传输

**错误：逐个文件SSH（234个文件=234次连接，超慢）**
```bash
ssh server "cat file1" > local1  # ❌ 每个文件一次连接
```

**正确：批量scp/rsync**
```bash
scp server:/path/docs/*/*.md ./local/docs/  # ✅ 一次传输
rsync -avz server:/path/docs/ ./local/docs/  # ✅ 增量同步
```

## 搜索实现（fuse.js）

```html
<script src="https://cdn.jsdelivr.net/npm/fuse.js@7.0.0/dist/fuse.min.js"></script>
<script>
const fuse = new Fuse(searchData, {
  keys: ['title', 'summary', 'tags', 'category'],
  threshold: 0.3,
});
</script>
```

## 文档查看器（doc.html）

```javascript
// 用marked.js客户端渲染markdown
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
const params = new URLSearchParams(location.search);
const file = params.get('file');  // ?file=docs/python/README.md_xxx.md
fetch('/' + file).then(r => r.text()).then(md => {
  document.getElementById('docContent').innerHTML = marked.parse(md);
});
```

## 定时同步

加入现有cron脚本：
```python
# sync_to_github.py 增加知识库同步
git_push(kb_dir, token, "tech-knowledge")
```

## Pitfalls

- **push rejected "repository rule violations"** — 大文件（.tar.gz/.zip）被拦截，删除后重试
- **Pages未生效** — 首次需5-10分钟
- **Token格式** — 用python3读.env，不要grep（有特殊字符）
- **gh CLI装不上** — 阿里云网络慢，直接curl调GitHub API
- **fuse.js上限** — ~5000条目后浏览器变慢
- **Node MCP Server** — 必须ESM格式（type:module）
- **marked.js CDN** — 用jsdelivr，不用unpkg（国内更稳定）
- **⚠️ GitHub Pages子目录路径** — 部署在 `username.github.io/repo/` 下，所有路径必须用相对路径（`assets/xxx`），不能用绝对路径（`/assets/xxx`）。绝对路径会解析到 `username.github.io/assets/xxx` 导致404。修复：`sed -i 's|href="/|href="|g'` 和 `sed -i 's|src="/|src="|g'` 批量替换
- **图片加载** — 关键图片（如赞赏码）建议用 `raw.githubusercontent.com` 绝对URL：`https://raw.githubusercontent.com/USER/REPO/main/assets/img.jpg`
- **采集数据过滤** — 远程服务器的docs/目录可能包含大量非技术内容（CSS/JS/图片的README），需先按目录名过滤，只保留真正的技术文档目录（如llm_agent, test_automation等），跳过www, m, github, cdn, img等
- **⚠️ 深色模式图片不可见** — 二维码等深色图片在深色主题网站上会"消失"。必须加白色边框：`ImageOps.expand(img, border=30, fill='white')`。用户反馈"看不到赞赏码"→ 根因是深色背景+深色图片=不可见
- **⚠️ 客户端库缺失导致页面空白** — HTML页面使用fuse.js/marked.js等库时，必须在**每个使用该库的HTML文件**中显式添加`<script src="CDN">`标签。不能依赖其他页面加载。症状：页面加载正常但内容不渲染，console报`Fuse is not defined`
- **⚠️ 数据质量二次过滤** — 第一次清洗只去掉了格式噪音（badge/base64/图片），还需要第二次过滤去掉内容噪音（无意义标题、重复项目、单篇分类）。两步清洗缺一不可
- **Hermes auxiliary API Key批量修复** — 多个auxiliary section的api_key为空时，用Python脚本批量修复：遍历config.yaml所有section，找到provider=volcengine且api_key=''的，统一设为'${ARK_API_KEY}'。一次性修复8个空key
