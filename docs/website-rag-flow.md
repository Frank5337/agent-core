# Website RAG 链路说明

这份文档说明当前 `http://localhost:8002/` 页面从“输入网址”到“RAG 问答”的完整链路，也补充这次新增的三项能力：

1. 真实 embedding 的独立配置能力
2. 多轮问答记忆
3. 更像 AI 产品的回答区与引用区交互

适用范围：
- 前端页面：`services/ai-service/frontend/index.html`
- 后端服务：`services/ai-service`

## 1. 当前整体链路

现在这条链路已经是标准的 `RAG` 流程：

`网站抓取 -> 文本清洗 -> 切片 -> embedding -> 检索 -> 组装上下文 -> 大模型回答`

页面入口是：

`http://localhost:8002/`

用户在页面上主要做两件事：

1. 输入网站地址，点击“抓取并入库”
2. 在问答区提问，或者连续追问

对应的后端接口是：

- `POST /api/v1/rag/ingest-website`
- `POST /api/v1/rag/ask`
- `GET /api/v1/system/rag-status`

## 2. 页面侧现在支持什么

当前前端页面已经支持：

- 网站地址可以直接输入 `example.com`，不必手动补 `http://` 或 `https://`
- 站点导入后左侧展示知识库信息、页面列表和原文链接
- 右侧问答区支持连续多轮追问
- 引用默认折叠，点击后再展开
- 会话内容会暂存在浏览器 `sessionStorage`
- 页面会显示当前 `generation provider`、`embedding mode`、`generation model`

## 3. 第一步：输入网站地址并导入

### 3.1 前端请求

用户点击“抓取并入库”后，前端会先做一次 URL 规范化：

- 如果已经带协议，直接使用
- 如果没带协议，自动补 `https://`

例如：

- `frank5337.github.io` -> `https://frank5337.github.io/`
- `example.com` -> `https://example.com/`

前端提交的数据结构是：

```json
{
  "url": "https://example.com/",
  "knowledge_base_name": "example.com",
  "max_pages": 5,
  "same_domain_only": true
}
```

### 3.2 后端入口

请求先进入：

- `app/api/routes/rag.py`

随后转给：

- `rag_service.ingest_website(db, payload)`

### 3.3 后端 URL 兜底

后端不会依赖前端必须传完整 URL。

`WebsiteIngestRequest.url` 现在是普通字符串，真正的规范化逻辑在：

- `app/services/website_service.py`

也就是说，就算前端没补协议，后端也会补一次，避免因为页面绕过或接口直调导致失败。

## 4. 第二步：抓取网站内容

抓取逻辑在：

- `app/services/website_service.py`

核心流程：

1. 从起始 URL 开始做 BFS 抓取
2. 每抓一个页面，提取：
   - 页面标题
   - 可见正文
   - 链接
3. 过滤脚本、样式、导航噪音和重复文本
4. 如果 `same_domain_only=true`，只继续抓同域页面
5. 抓到 `max_pages` 或没有可继续的链接时结束

输出结构是 `WebsiteContent` 列表，每一项包含：

- `url`
- `title`
- `text`
- `links`

## 5. 第三步：写入知识库与文档

编排逻辑在：

- `app/services/rag_service.py`

导入时会做几件事：

1. 根据 URL 或手工名称找到知识库，若不存在则创建
2. 重置该知识库已有文档和 chunk
3. 将每个抓到的页面写成一条 `document`
4. 立刻为 document 切片
5. 为切片生成 embedding

当前重建策略是“重新导入时清掉旧内容再重建”，优点是简单、稳定，不容易把旧页面和新页面混在一起。

## 6. 第四步：切片

切片逻辑在：

- `app/services/document_service.py`

当前切片策略是“固定窗口 + overlap”：

- `chunk_size`
- `chunk_overlap`

每个 chunk 会保存：

- `chunk_index`
- `content`
- `token_count`
- `embedding_json`
- `embedding_model`
- `embedding_status`

## 7. 什么是 embedding

`Embedding` 可以理解为“把一段文本变成一组向量数字”，让系统可以比较“语义上像不像”，而不只是比较字面是否完全相同。

### 7.1 为什么 RAG 需要 embedding

如果没有 embedding，系统通常只能做关键词匹配：

- 问题里写了“Java”
- 页面里也刚好写了“Java”

这样还能匹配到。

但如果用户问的是：

- “这个网站里有哪些后端技术内容？”

页面可能写的是：

- JVM
- Spring
- 并发
- 面试题

这时候单纯靠关键词就不够稳了。

Embedding 的作用就是把：

- 问题
- 文档 chunk

都映射到同一个向量空间里。这样即便措辞不同，只要语义接近，也能通过向量相似度把相关 chunk 找出来。

### 7.2 在这套系统里，embedding 用在什么地方

当前系统里，embedding 用在两处：

1. 文档入库后，为每个 chunk 生成 embedding
2. 用户提问时，为 query 生成 embedding

随后系统会计算：

- `query embedding`
- `chunk embedding`

之间的余弦相似度 `cosine similarity`，据此挑出最相关的 `top K` chunk。

### 7.3 现在支持哪两类 embedding

当前代码支持两种模式：

#### 模式 A：真实远程 embedding

当你配置了独立的 embedding provider 时，系统会请求真实接口：

- `POST {embedding_base_url}/embeddings`

这时 `embedding_json` 保存的就是远程模型返回的语义向量。

#### 模式 B：本地 hash embedding

如果没有可用的远程 embedding，系统会回退到本地 hash 向量。

它的特点是：

- 不需要额外服务
- 足够把 RAG 链路跑通
- 但语义效果弱于真实 embedding

### 7.4 现在为什么默认还是 local-hash

你现在这套环境里，回答模型用的是 `DeepSeek`。

我们这次把 embedding 配置和 generation 配置拆开了，但如果你没有另外配置一个真实 embedding 提供方，系统还是会显示：

- `embedding_mode = local-hash`

也就是：

- 检索：本地向量
- 回答：DeepSeek

这已经是可运行的 RAG，但不是效果最强的版本。

## 8. 第五步：真实 embedding 怎么启用

这次代码已经支持“embedding 独立配置”，也就是：

- generation 继续走 DeepSeek
- embedding 单独走另一个兼容 OpenAI Embeddings 的服务

新增配置项在：

- `services/ai-service/.env.example`

主要是这些：

```env
AIMP_EMBEDDING_API_KEY=
AIMP_EMBEDDING_BASE_URL=
AIMP_GENERATION_API_KEY=
AIMP_GENERATION_BASE_URL=
AIMP_RAG_EMBEDDING_MODEL=text-embedding-3-small
AIMP_RAG_GENERATION_MODEL=gpt-4.1-mini
```

### 8.1 推荐配置方式

如果你想保持：

- 回答走 DeepSeek
- embedding 走真实语义向量

可以这样配：

```env
AIMP_OPENAI_API_KEY=你的DeepSeekKey
AIMP_OPENAI_BASE_URL=https://api.deepseek.com

AIMP_EMBEDDING_API_KEY=你的Embedding服务Key
AIMP_EMBEDDING_BASE_URL=https://api.openai.com/v1
AIMP_RAG_EMBEDDING_MODEL=text-embedding-3-small

AIMP_GENERATION_API_KEY=你的DeepSeekKey
AIMP_GENERATION_BASE_URL=https://api.deepseek.com
AIMP_RAG_GENERATION_MODEL=deepseek-v4-flash
```

这样运行后：

- `generation_provider = deepseek`
- `embedding_mode = openai`

### 8.2 运行时如何查看是否生效

调用：

`GET /api/v1/system/rag-status`

如果你看到：

```json
{
  "generation_provider": "deepseek",
  "embedding_mode": "openai",
  "embedding_model": "text-embedding-3-small"
}
```

说明真实 embedding 已经启用。

## 9. 第六步：提问与多轮记忆

用户点击“开始提问”后，前端会提交：

```json
{
  "knowledge_base_id": "...",
  "question": "这个网站主要介绍什么？",
  "top_k": 4,
  "history": [
    {
      "role": "user",
      "content": "先总结一下这个网站"
    },
    {
      "role": "assistant",
      "content": "这个网站主要分享技术与生活内容"
    }
  ]
}
```

这次新增的重点是 `history`。

### 9.1 记忆是怎么工作的

前端会把最近几轮消息保存在：

- `state.chatMessages`
- `sessionStorage`

每次新提问时，会把最近几轮的：

- `user`
- `assistant`

消息一起带到后端。

### 9.2 后端怎么使用 history

后端在：

- `app/services/generation_service.py`

里把最近几轮历史消息和当前检索到的上下文一起拼进 prompt。

这样模型回答时，不是只看到“当前问题”，而是能同时看到：

1. 用户之前问过什么
2. 系统之前怎么回答
3. 当前检索出来的相关 chunk

这就是现在支持多轮追问的原因。

## 10. 第七步：检索

检索逻辑在：

- `app/services/retrieval_service.py`

当前流程：

1. 确保目标知识库的 chunk 已经有 embedding
2. 对 query 生成 query embedding
3. 读出知识库中所有 chunk
4. 计算 query 和每个 chunk 的向量相似度
5. 再加一点词法得分和标题得分
6. 按最终 score 排序
7. 取 `top_k`

返回的 `RetrievalResult` 包含：

- `document_name`
- `source_url`
- `chunk_index`
- `snippet`
- `score`
- `content`

其中：

- `content` 用于喂给模型
- `snippet` 用于前端显示引用

## 11. 第八步：回答生成

生成逻辑在：

- `app/services/generation_service.py`

现在支持：

- OpenAI `responses`
- OpenAI 兼容 `chat/completions`
- DeepSeek `chat/completions`

生成时会把三类信息一起组装进 prompt：

1. 最近几轮对话历史
2. 命中的 `top K` 上下文
3. 当前用户问题

这就让系统既有：

- 检索增强能力
- 多轮对话连续性

## 12. 第九步：回答区和引用区怎么改了

这次前端交互也升级了：

### 12.1 回答区

- 回答区改成更像聊天产品的气泡式布局
- 用户和助手消息分开显示
- 助手消息支持基础富文本展示
- 多轮会话会保存在当前浏览器会话里

### 12.2 引用区

- 默认折叠
- 先显示“查看引用（N）”
- 展开后按引用卡片展示
- 每条引用内部再用 `details` 打开 snippet
- 可以直接点“打开原文”

这比之前“回答后直接把大段引用灌出来”更适合真实使用。

## 13. 当前运行模式怎么判断

查看：

`GET /api/v1/system/rag-status`

返回里重点看：

- `generation_provider`
- `embedding_provider`
- `embedding_mode`
- `generation_model`
- `embedding_model`

当前如果你只配置了 DeepSeek 回答而没配独立 embedding，典型状态会是：

```json
{
  "generation_provider": "deepseek",
  "embedding_provider": "local-hash",
  "embedding_mode": "local-hash"
}
```

## 14. 当前版本的优点

- 已经是完整的 RAG 链路，不是简单规则拼接
- 支持网站多页抓取
- 支持文档切片和 embedding 持久化
- 支持 generation 和 embedding 分离配置
- 支持多轮会话记忆
- 前端交互已经更接近产品化

## 15. 当前版本仍然的边界

- 如果没有独立 embedding provider，检索仍是 `local-hash`
- 切片仍然是固定窗口，不是语义切片
- 还没有 rerank
- 还没有真正的向量数据库，如 `pgvector` / `Milvus`
- 抓取流程还没有异步任务和进度状态

## 16. 下一步建议

建议按这个顺序继续升级：

1. 给 embedding 接一个真实提供方，先把 `embedding_mode` 从 `local-hash` 变成 `openai`
2. 把当前 SQLite 文本向量存储升级到 `pgvector`
3. 增加 rerank
4. 做异步抓取与进度条
5. 做知识库重抓、删除和增量更新

做到这一步之后，这套网站问答能力就会从“能跑的 RAG Demo”升级到“效果更稳定的产品化 RAG”。
