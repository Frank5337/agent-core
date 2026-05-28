# Website RAG 链路说明

这份文档说明当前 `http://localhost:8002/` 页面从“输入网址”到“生成 RAG 问答”的完整链路，以及内部运行原理。

适用服务：

- 前端页面：`services/ai-service/frontend/index.html`
- 后端服务：`services/ai-service`

## 1. 总体目标

当前这套能力的目标是：

1. 用户在页面输入一个网站地址。
2. 系统抓取该网站首页及站内若干页面。
3. 将网页正文清洗、切片并写入知识库。
4. 为每个切片生成向量。
5. 用户提问时先做向量检索，再把检索结果交给大模型回答。

这本质上是一个面向网站内容的 `RAG` 流程：

`网页抓取 -> 文本切片 -> 向量化 -> 检索 -> 上下文增强 -> 大模型回答`

## 2. 入口与页面加载

浏览器访问：

`http://localhost:8002/`

后端入口在 [main.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/main.py:1)。

页面加载过程：

1. FastAPI 启动时执行 `on_startup()`。
2. `on_startup()` 调用 `init_db()`，初始化数据库表和必要字段。
3. 浏览器访问 `/` 时，FastAPI 返回 `frontend/index.html`。

对应代码：

- [main.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/main.py:1)
- [bootstrap.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/bootstrap.py:1)

## 3. 页面上的两个核心动作

页面主要有两个动作：

1. `抓取并入库`
2. `开始提问`

这两个动作分别对应两个后端接口：

- `POST /api/v1/rag/ingest-website`
- `POST /api/v1/rag/ask`

前端都在 [index.html](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/frontend/index.html:1) 里通过 `fetch()` 调用。

## 4. 第一步：输入网址并抓取网页

### 4.1 前端发请求

用户点击 `抓取并入库` 后，前端会提交：

```json
{
  "url": "https://example.com",
  "knowledge_base_name": "example.com",
  "max_pages": 5,
  "same_domain_only": true
}
```

其中：

- `url`：起始网址
- `knowledge_base_name`：知识库名，可为空
- `max_pages`：最多抓多少页
- `same_domain_only`：是否只抓同域链接

### 4.2 后端路由进入

请求首先进入 [rag.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/api/routes/rag.py:1) 的 `ingest_website()`。

这个路由只做两件事：

1. 获取数据库会话 `db`
2. 调用 `rag_service.ingest_website(db, payload)`

### 4.3 网站抓取

真正的抓取逻辑在 [website_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/website_service.py:1)。

内部流程：

1. `crawl()` 从用户输入的起始 URL 开始。
2. 用一个队列按广度优先方式抓取页面。
3. 每抓到一页，解析 HTML：
   - 提取 `<title>`
   - 提取可见正文
   - 提取页面里的链接
4. 对文本做清洗：
   - 去掉脚本、样式、无意义导航文本
   - 去掉重复行
   - 合并空白字符
5. 如果设置了 `same_domain_only=true`，只保留同域链接继续抓取。
6. 抓到 `max_pages` 或没有更多链接时结束。

产出是 `WebsiteContent` 列表，每个元素包含：

- `url`
- `title`
- `text`
- `links`

## 5. 第二步：写入知识库与文档

网站抓取完成后，逻辑回到 [rag_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/rag_service.py:1)。

### 5.1 创建或复用知识库

`_get_or_create_knowledge_base()` 会：

1. 先按名称查询知识库
2. 如果存在，就直接复用
3. 如果不存在，就新建

知识库数据表对应：

- `knowledge_bases`

### 5.2 重建知识库内容

当前策略是“重新抓取时重建该知识库中的文档与切片”。

`_reset_knowledge_base_documents()` 会：

1. 删除该知识库已有的 `documents`
2. 删除关联的 `chunks`
3. 重置 `document_count`

这样做的原因：

- 避免旧页面、旧切片、旧索引污染新一轮抓取结果
- 简化当前实现，不做增量合并

### 5.3 每个网页生成一个文档

每个 `WebsiteContent` 会调用 `_upsert_document()`，进一步进入 [document_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/document_service.py:1)。

写入的文档字段包括：

- `name`：页面标题
- `source_type`：`url`
- `source_uri`：原始页面地址
- `mime_type`：`text/html`
- `content`：清洗后的正文
- `status`：初始 `draft`

对应表：

- `documents`

## 6. 第三步：文档切片

文档创建后，会立即调用 `document_service.parse_document()`。

切片逻辑：

1. 先清掉该文档已有 chunk
2. 按 `chunk_size` 和 `chunk_overlap` 做滑动窗口切分
3. 每一段生成一个 `ChunkModel`
4. 更新文档的 `chunk_count`
5. 文档状态改成 `parsed`

当前切片策略是简单的“定长窗口切片”，不是语义切片。

对应表：

- `chunks`

每个 chunk 主要字段：

- `chunk_index`
- `content`
- `token_count`
- `embedding_json`
- `embedding_model`
- `embedding_status`

## 7. 第四步：生成向量

文档切片完成后，RAG 服务会立即调用：

`embedding_service.ensure_chunk_embeddings(...)`

对应实现：

- [embedding_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/embedding_service.py:1)

### 7.1 当前支持两种向量模式

#### 模式 A：远程 embedding

当满足以下条件时启用：

- 配置了 API Key
- 并且当前 `base_url` 不是 DeepSeek

此时会请求：

- `POST {base_url}/embeddings`

返回的向量会写入 `chunk.embedding_json`。

#### 模式 B：本地 hash embedding

当前实际运行就是这个模式。

原因：

- 当前配置的是 `DeepSeek`
- 我们没有接入一个明确可用的远程 embedding 接口

本地模式的实现方式：

1. 对 chunk 文本分词
2. 把 token 哈希到固定维度向量槽位
3. 做归一化
4. 将向量 JSON 存入 `embedding_json`

这不是最强的语义 embedding，但能把检索链路完整跑通。

### 7.2 向量持久化

向量不是只在内存里使用，而是存回数据库：

- `embedding_json`
- `embedding_model`
- `embedding_status`

这样后续提问时就不需要重新为所有 chunk 计算向量。

## 8. 第五步：用户提问

### 8.1 前端发起问答请求

用户点击 `开始提问` 后，前端会发：

```json
{
  "knowledge_base_id": "...",
  "question": "这个网站是做什么的？",
  "top_k": 3
}
```

### 8.2 路由进入

请求进入 [rag.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/api/routes/rag.py:1) 的 `ask()`。

再转到：

`rag_service.ask(db, payload)`

## 9. 第六步：向量检索

提问时真正的检索逻辑在：

- [retrieval_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/retrieval_service.py:1)

### 9.1 检索流程

1. 先确保当前知识库的 chunk 都有向量：
   - `embedding_service.ensure_chunk_embeddings(...)`
2. 对用户问题生成 query embedding：
   - `embedding_service.embed_query(question)`
3. 读出该知识库的所有 chunk
4. 逐个做相似度计算：
   - `cosine_similarity(query_embedding, chunk_embedding)`
5. 再加少量词法分和标题分：
   - `lexical_score`
   - `title_score`
6. 综合得到最终 `score`
7. 取 `top_k` 结果

### 9.2 返回结果结构

检索返回的是 `RetrievalResult` 列表，里面有：

- `document_id`
- `document_name`
- `source_url`
- `chunk_id`
- `chunk_index`
- `snippet`
- `score`
- `content`

其中：

- `snippet` 用于前端显示引用
- `content` 用于后续喂给生成模型

## 10. 第七步：上下文增强与大模型回答

检索结果拿到之后，RAG 服务会调用：

`generation_service.answer_question(question, results)`

实现文件：

- [generation_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/generation_service.py:1)

### 10.1 当前回答模式

当前是：

- `DeepSeek` 负责生成回答
- 本地 hash embedding 负责检索

这可以理解为：

`本地向量检索 + DeepSeek 大模型生成`

### 10.2 Prompt 组织方式

生成前会把检索到的 top K 上下文拼成结构化 prompt，例如：

```text
[Context 1]
Page: 某页面标题
URL: 某页面地址
Score: 0.81
Content: 某段正文

[Context 2]
...

User question: 用户问题
```

### 10.3 生成接口

当前对 DeepSeek 走的是兼容接口：

- `POST {base_url}/chat/completions`

因为当前 `.env` 里配置的是：

- `AIMP_OPENAI_BASE_URL=https://api.deepseek.com`
- `AIMP_RAG_GENERATION_MODEL=deepseek-v4-flash`

如果将来换成标准 OpenAI 兼容服务，也支持切到：

- `/responses`

### 10.4 返回前端的数据

最终返回：

```json
{
  "knowledge_base_id": "...",
  "question": "...",
  "answer": "...",
  "citations": [
    {
      "document_name": "...",
      "source_url": "...",
      "snippet": "...",
      "score": 0.81
    }
  ]
}
```

前端现在的显示方式是：

1. 先显示回答正文
2. 不自动展开引用
3. 显示 `查看引用（N）` 按钮
4. 点击后展开引用片段

## 11. 当前运行模式

当前可以通过：

`GET /api/v1/system/rag-status`

查看实际运行状态。

对应文件：

- [system.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/api/routes/system.py:1)

当前你这台机器上的模式是：

- `provider = deepseek`
- `llm_mode = deepseek`
- `embedding_mode = local-hash`

这意味着：

- 生成是 `DeepSeek`
- 检索是本地向量检索
- 还没有接入独立的远程 embedding 服务

## 12. 这条链路里各模块的职责

### 前端

- [index.html](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/frontend/index.html:1)

职责：

- 收集 URL、页数上限、问题
- 调用后端接口
- 展示回答和引用

### 路由层

- [rag.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/api/routes/rag.py:1)

职责：

- 接收 HTTP 请求
- 做异常转 HTTP 错误

### 抓取层

- [website_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/website_service.py:1)

职责：

- 抓网页
- 提取标题
- 提取正文
- 抽取链接

### 文档层

- [document_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/document_service.py:1)

职责：

- 建文档
- 切片
- 更新文档状态

### 向量层

- [embedding_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/embedding_service.py:1)

职责：

- 生成 chunk embedding
- 生成 query embedding
- 计算向量相似度

### 检索层

- [retrieval_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/retrieval_service.py:1)

职责：

- 做 top K 检索
- 组装 snippet 和 score

### 生成层

- [generation_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/generation_service.py:1)

职责：

- 组织上下文 prompt
- 调用 DeepSeek / OpenAI 兼容接口
- 输出最终回答

### 编排层

- [rag_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/rag_service.py:1)

职责：

- 把抓取、建库、切片、向量化、检索、生成串成一条完整链路

## 13. 当前实现的优点

- 链路完整，已经是真正的 `RAG` 结构，不是简单规则拼接
- 支持网站多页抓取
- 支持知识库重建
- 支持向量持久化
- 支持切换到远程大模型生成

## 14. 当前实现的限制

- 当前 embedding 仍是本地 hash 向量，不是正式语义 embedding
- 切片还是定长窗口，没有做语义分段
- 站点抓取没有做 robots、去重策略增强、反爬兼容
- 生成前没有做 rerank
- 没有单独的向量库，当前向量保存在 SQLite 文本字段里

## 15. 下一步建议

如果继续升级，建议按这个顺序：

1. 接正式 embedding 服务
2. 换成 `pgvector` 或 `Milvus`
3. 增加 rerank
4. 优化网页正文抽取
5. 加抓取任务状态和异步队列

这样整条链路就会从“可运行的 RAG”升级到“效果更稳的生产版 RAG”。
