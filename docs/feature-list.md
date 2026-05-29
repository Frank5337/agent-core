# 当前功能总表

这份文档汇总当前仓库里已经落地的功能点，方便汇报、排期和交接。

## 1. 架构层

- 混合架构
  - `platform-service` 负责平台能力
  - `ai-service` 负责 AI 能力
- 服务间调用
  - `platform-service` 通过内部 HTTP 调用 `ai-service`
- 本地可运行 Demo
  - 网站抓取
  - 知识库构建
  - RAG 问答

## 2. platform-service 已有能力

### 2.1 租户

- 租户创建
- 租户列表查询
- 租户详情查询

### 2.2 平台用户与角色

- 平台用户创建
- 平台用户列表查询
- 平台用户详情查询
- 固定角色目录
  - `PLATFORM_ADMIN`
  - `TENANT_ADMIN`
  - `APP_OPERATOR`
  - `AUDITOR`
- 平台控制台首页
  - 内置在 `platform-service` 根路径
  - 覆盖租户、用户、角色、应用、审计和聊天联调

### 2.3 应用管理

- 应用创建
- 应用列表查询
- 应用详情查询
- 应用发布
- 应用转回草稿
- 应用详情补充可读字段
  - `tenantName`
  - `defaultProviderName`
  - `defaultKnowledgeBaseName`

### 2.4 审计

- 租户创建审计
- 用户创建审计
- 应用创建审计
- 应用发布审计
- 应用转草稿审计
- 审计日志查询

### 2.5 平台统一对话入口

- 对外暴露应用级聊天入口
- 平台侧补齐默认 provider、knowledge base、system prompt 后再转发到 `ai-service`
- 提供 provider / knowledge base 目录代理接口，便于前端页面直接下拉选择

## 3. ai-service 已有能力

### 3.1 Provider 管理

- Provider 列表
- Provider 创建
- 默认 Provider 逻辑

### 3.2 Knowledge Base 管理

- Knowledge Base 列表
- Knowledge Base 创建
- Knowledge Base 查询

### 3.3 Document 与 Chunk

- Document 创建
- Document 列表
- Document 详情
- Document 状态更新
- Document 解析入口
- Chunk 列表
- Chunk 创建
- Chunk embedding 持久化字段

### 3.4 问答接口

- `POST /api/v1/chat/completions`
- 网站 RAG 导入与提问接口

## 4. 网站 RAG Demo

- 输入网站地址导入
- 支持裸域名输入
- 自动补全 `https://`
- 同域多页抓取
- 抓取页数上限
- 正文清洗与切片
- 自动创建知识库
- 网站重抓时重建内容
- `TopK` 检索控制
- 多轮问答历史
- 引用折叠/展开
- 页面内展示当前模型与模式

## 5. 向量与生成

- 本地 `local-hash` embedding fallback
- 支持独立配置真实 embedding provider
- 支持 OpenAI 兼容生成接口
- 支持 DeepSeek 回答
- 支持检索结果增强回答

## 6. 仍待增强的能力

- 真正的向量库
  - `pgvector`
  - `Milvus`
- `rerank`
- 抓取任务异步化与进度条
- 更稳的中文编码识别
- 知识库管理后台页
