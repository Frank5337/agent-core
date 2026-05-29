# API 总览

这份文档汇总当前两个服务的主要接口，方便联调和排开发。

## 1. ai-service

- 服务定位：模型、知识库、网站 RAG、问答
- 推荐页面入口：`http://localhost:8002`

### 1.1 系统接口

- `GET /health`
- `GET /api/v1/system/rag-status`

### 1.2 Provider 接口

- `GET /api/v1/providers`
- `POST /api/v1/providers`

### 1.3 Knowledge Base 接口

- `GET /api/v1/knowledge-bases`
- `POST /api/v1/knowledge-bases`

### 1.4 Document 接口

- `GET /api/v1/knowledge-bases/{knowledgeBaseId}/documents`
- `POST /api/v1/knowledge-bases/{knowledgeBaseId}/documents`
- `GET /api/v1/knowledge-bases/{knowledgeBaseId}/documents/{documentId}`
- `PATCH /api/v1/knowledge-bases/{knowledgeBaseId}/documents/{documentId}/status`
- `POST /api/v1/knowledge-bases/{knowledgeBaseId}/documents/{documentId}/parse`

### 1.5 Chunk 接口

- `GET /api/v1/knowledge-bases/{knowledgeBaseId}/documents/{documentId}/chunks`
- `POST /api/v1/knowledge-bases/{knowledgeBaseId}/documents/{documentId}/chunks`

### 1.6 Chat 与 RAG 接口

- `POST /api/v1/chat/completions`
- `POST /api/v1/rag/ingest-website`
- `POST /api/v1/rag/ask`

## 2. platform-service

- 服务定位：租户、用户、角色、应用、发布和审计
- 默认端口：`http://localhost:8080`

### 2.1 系统接口

- `GET /health`
- `GET /actuator/health`

### 2.2 Tenant 接口

- `GET /api/v1/tenants`
- `GET /api/v1/tenants/{tenantId}`
- `POST /api/v1/tenants`

### 2.3 User 与 Role 接口

- `GET /api/v1/users`
- `GET /api/v1/users/{userId}`
- `POST /api/v1/users`
- `GET /api/v1/roles`
- `GET /api/v1/catalog/providers`
- `GET /api/v1/catalog/knowledge-bases`

### 2.4 Application 接口

- `GET /api/v1/applications`
- `GET /api/v1/applications/{applicationId}`
- `POST /api/v1/applications`
- `POST /api/v1/applications/{applicationId}/publish`
- `POST /api/v1/applications/{applicationId}/draft`
- `POST /api/v1/applications/{applicationId}/chat`

### 2.5 Audit 接口

- `GET /api/v1/audit-logs`

## 3. 当前调用关系

推荐方式：

1. 业务系统优先接入 `platform-service`
2. `platform-service` 在需要 AI 能力时再调用 `ai-service`
3. 网站 RAG Demo 页面仍然直接挂在 `ai-service`
