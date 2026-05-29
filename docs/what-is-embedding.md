# 什么是 Embedding

这份文档专门解释 `embedding` 是什么、为什么 RAG 需要它、它和关键词检索有什么区别，以及它在我们当前项目里扮演什么角色。

## 1. 一句话理解

`Embedding` 可以理解成：

“把一段文本转换成一组可以计算相似度的数字向量。”

人类看文字时，能靠语义理解“这两句话是不是在讲差不多的事”。  
机器本身不懂语义，所以需要先把文本映射成向量，再通过向量之间的距离或夹角来判断“语义是不是接近”。

## 2. 为什么需要 Embedding

如果没有 embedding，系统通常只能做“关键词匹配”。

例如：

- 用户问：`这个网站有哪些后端技术内容？`
- 页面里写的是：`JVM`、`Spring`、`并发`、`面试题`

这时用户的问题里并没有直接写出 `JVM` 或 `Spring`，如果只靠关键词检索，结果就可能不稳定。

Embedding 的作用是：

- 把“后端技术内容”
- 把“JVM / Spring / 并发 / 面试题”

都映射到一个向量空间里。  
这样即使字面不完全一致，只要语义接近，系统也能把相关内容找出来。

## 3. Embedding 到底长什么样

从概念上说，embedding 就是一串浮点数，例如：

```text
[0.018, -0.127, 0.442, ..., 0.091]
```

这串数字本身对人没有直观意义，但对机器来说，它能表示一段文本在“语义空间”中的位置。

常见做法是：

1. 把一句话输入 embedding 模型
2. 模型输出一个固定维度的向量
3. 再用数学方法比较两个向量的相似度

最常见的相似度算法是：

- `Cosine Similarity`，余弦相似度

它会告诉我们：

- `1` 附近：很相似
- `0` 附近：关系不大
- `-1` 附近：方向相反

## 4. Embedding 和关键词检索的区别

### 关键词检索

优点：

- 简单
- 快
- 容易解释

缺点：

- 依赖字面匹配
- 同义表达、上下位概念、改写问法时效果差

### Embedding 检索

优点：

- 更擅长找“语义相关”的内容
- 对问法改写更稳
- 更适合自然语言问答

缺点：

- 需要额外的 embedding 模型
- 成本更高
- 结果解释性比纯关键词稍弱

实际工程里，很多系统会把两者结合：

- 关键词检索负责“精确”
- embedding 检索负责“语义召回”

这也是我们现在项目里正在做的方向。

## 5. 在 RAG 里，Embedding 用在哪

RAG 是：

`Retrieve -> Augment -> Generate`

也就是：

1. 先检索
2. 再把检索结果作为上下文
3. 最后交给大模型生成答案

Embedding 主要发生在 “Retrieve” 这一步。

具体来说有两处：

### 文档入库时

系统会把知识库里的每个文本切片 `chunk` 转成 embedding。

也就是：

- 一段网页正文
- 一段文档片段
- 一段知识库内容

都会先被编码成向量并保存下来。

### 用户提问时

系统会把用户问题也转成 embedding。

然后做比较：

- `问题向量`
- `chunk 向量`

比较谁更接近，就把哪些 chunk 召回出来。

## 6. 为什么 Embedding 对 RAG 很关键

没有 embedding 的 RAG，通常只能做到：

- 问题和原文词面很接近时效果还可以

但只要用户换一种说法，就容易召回失败。

有 embedding 后，RAG 的好处是：

- 用户用自然语言提问更稳
- 不必每次都用原文里的关键词
- 对总结类、解释类、归纳类问题更友好

例如：

- 原文写：`Java 并发、JVM、集合、面试题`
- 用户问：`这个网站提到了哪些后端面试知识？`

embedding 更容易把这类语义相关内容召回出来。

## 7. 我们当前项目里怎么用 Embedding

在当前项目里，embedding 主要对应这几个文件：

- [embedding_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/embedding_service.py:1)
- [retrieval_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/retrieval_service.py:1)
- [generation_service.py](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/app/services/generation_service.py:1)

当前流程是：

1. 抓网页
2. 清洗正文
3. 按固定窗口切成 chunk
4. 为每个 chunk 生成 embedding
5. 用户提问时为 query 生成 embedding
6. 用相似度找到 top K chunk
7. 把 top K chunk 交给大模型生成回答

## 8. 我们现在支持哪两种 Embedding 模式

### 模式 A：真实远程 Embedding

如果配置了独立的 embedding 服务，系统会调用远程接口：

- `POST {embedding_base_url}/embeddings`

这时拿到的就是“真实语义向量”。

优点：

- 检索质量更高
- 更接近生产级 RAG

适合：

- 正式 Demo
- 真实业务问答

### 模式 B：本地 Hash Embedding

如果没有配置远程 embedding，系统会回退到本地 hash 向量。

它的特点是：

- 不依赖外部 embedding 服务
- 成本低
- 可以把整条 RAG 链路跑通

但缺点也很明显：

- 语义能力弱
- 检索效果不如真实 embedding

适合：

- 本地开发
- 功能联调
- 演示链路是否打通

## 9. 为什么我们现在默认还是 Local Hash

当前这套环境里：

- 回答模型走的是 `DeepSeek`
- embedding 还没有单独接一个正式的 embedding provider

所以系统状态通常会是：

- `generation_provider = deepseek`
- `embedding_mode = local-hash`

这意味着：

- 回答是大模型生成的
- 检索是本地向量模拟的

这种模式已经是完整的 RAG，但还不是效果最强的版本。

## 10. 真实 Embedding 怎么接入

我们已经把 embedding 和 generation 的配置拆开了。

也就是说，现在可以做到：

- `DeepSeek` 负责回答
- 另一个兼容 OpenAI Embeddings 的服务负责向量化

配置项在：

- [services/ai-service/.env.example](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/ai-service/.env.example:1)

关键变量：

```env
AIMP_EMBEDDING_API_KEY=
AIMP_EMBEDDING_BASE_URL=
AIMP_RAG_EMBEDDING_MODEL=text-embedding-3-small

AIMP_GENERATION_API_KEY=
AIMP_GENERATION_BASE_URL=
AIMP_RAG_GENERATION_MODEL=deepseek-v4-flash
```

这样就能实现：

- embedding 用一个真正的语义向量模型
- generation 继续走 DeepSeek

## 11. 如何判断当前是不是“真实 Embedding”

可以查看：

- `GET /api/v1/system/rag-status`

重点看这些字段：

- `embedding_mode`
- `embedding_provider`
- `embedding_model`

如果你看到：

```json
{
  "embedding_mode": "openai",
  "embedding_provider": "openai-compatible",
  "embedding_model": "text-embedding-3-small"
}
```

说明现在已经不是本地 hash，而是真实 embedding 了。

如果看到：

```json
{
  "embedding_mode": "local-hash",
  "embedding_model": "local-hash-v1"
}
```

说明仍然在走本地 fallback。

## 12. Embedding 不是“大模型回答”

这个点很容易混淆。

Embedding 模型和生成模型不是一回事：

### Embedding 模型

职责：

- 把文本变成向量
- 让系统能做语义检索

输出：

- 一串数字向量

### 生成模型

职责：

- 根据问题和检索到的上下文生成自然语言答案

输出：

- 一段人能读懂的话

所以在一套 RAG 系统里，常常会同时有两种模型：

1. embedding 模型
2. generation 模型

## 13. 用一个通俗类比

可以把 embedding 想成“图书馆里的坐标系统”。

- 每本书都先根据内容被放到某个区域
- 你的问题也会被转换成一个“查询坐标”
- 系统先找到坐标最接近的书架
- 再把这些书交给“大模型”去阅读和回答

也就是说：

- embedding 负责“找资料”
- 大模型负责“看资料并回答”

## 14. 在项目推进上，为什么 Embedding 值得优先做

对 RAG 来说，效果通常不只取决于模型回答得多漂亮，更取决于“召回是不是对的”。

如果召回错了：

- 模型再强也容易答偏
- 会看起来像“胡说”

如果召回对了：

- 即使模型一般，回答通常也会更靠谱

所以很多 RAG 项目里，最优先值得投入的不是花哨界面，而是：

1. 正确切片
2. 正确 embedding
3. 正确检索

## 15. 对我们当前项目的建议

从当前状态看，最值得继续推进的是：

1. 把 `local-hash` 升级成真实 embedding
2. 再补 `rerank`
3. 最后再接 `pgvector` 这样的真正向量库

这样整套网站问答能力会从：

“能跑的 RAG Demo”

逐步升级成：

“效果更稳定的产品化 RAG”
