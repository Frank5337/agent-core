# AI 中台混合架构 MVP 设计文档

## 1. 目标

建设一个面向企业内部的 AI 中台，采用 `Java + Python` 混合架构：

- `Java` 承载平台型能力
- `Python` 承载 AI 算法与模型能力
- 两者通过内部 HTTP/异步任务解耦

这样既兼顾企业级治理能力，也保留 AI 迭代效率。

## 2. 为什么采用混合架构

### 2.1 Java 适合承载的平台能力

- 多租户
- 用户与角色权限
- 审计日志
- 应用配置中心
- 开放 API
- 稳定性治理
- 企业系统集成

### 2.2 Python 适合承载的 AI 能力

- 模型接入与快速适配
- RAG
- 文档解析和切片
- Embedding / Rerank
- Agent 编排试验
- 评测和 Prompt 调优

### 2.3 架构决策

不做“全 Java”或“全 Python”的极端方案，采用职责分离：

- Java 管平台
- Python 管 AI

## 3. MVP 功能范围

### 3.1 Java platform-service

- 租户管理
- 用户与角色权限
- 应用管理
- 应用配置发布
- 平台审计入口
- 对外 API 编排入口

### 3.2 Python ai-service

- 模型提供商管理
- 模型统一调用接口
- 知识库管理
- 文档处理任务入口
- 对话补全接口
- AI 能力扩展入口

## 4. 系统架构图

```text
                        +-----------------------------------+
                        |            Frontend UI            |
                        |   Console / Admin / Operations    |
                        +-----------------+-----------------+
                                          |
                        +-----------------+-----------------+
                        |       API Gateway / BFF           |
                        | Auth / RateLimit / Routing / Audit|
                        +-----------------+-----------------+
                                          |
              +---------------------------+---------------------------+
              |                                                          
  +-----------+-----------+                                +------------+------------+
  |    platform-service   |                                |        ai-service       |
  |        Java           |                                |         Python          |
  +-----------+-----------+                                +------------+------------+
              |                                                         |
              |                                                         |
  +-----------+-----------+                                +------------+------------+
  | Tenant / User / RBAC  |                                | Provider Gateway        |
  | Application Config    |                                | Chat Completion         |
  | Audit / Open API      |                                | Knowledge Base / RAG    |
  +-----------+-----------+                                +------------+------------+
              |                                                         |
              +---------------------------+-----------------------------+
                                          |
                        +-----------------+-----------------+
                        | Shared Infrastructure             |
                        | PostgreSQL / Redis / MinIO / MQ   |
                        | pgvector / Milvus / Monitoring    |
                        +-----------------------------------+
```

## 5. 服务边界

### 5.1 platform-service 职责

- 统一对外 API
- 管理租户、组织、用户、角色
- 管理 AI 应用元数据
- 控制应用发布
- 记录审计日志
- 管理内部服务调用权限

### 5.2 ai-service 职责

- 统一管理模型提供商
- 统一模型调用协议
- 管理知识库和检索配置
- 承载对话和后续 Agent 能力
- 向平台返回结构化 AI 结果

### 5.3 服务交互原则

- 外部客户端优先调用 Java 平台服务
- Java 平台服务再调用 Python AI 服务
- Python AI 服务不直接暴露复杂平台语义

## 6. API 规划

### 6.1 platform-service

- `GET /health`
- `GET /api/v1/tenants`
- `POST /api/v1/tenants`
- `GET /api/v1/applications`
- `POST /api/v1/applications`

### 6.2 ai-service

- `GET /health`
- `GET /api/v1/providers`
- `POST /api/v1/providers`
- `GET /api/v1/knowledge-bases`
- `POST /api/v1/knowledge-bases`
- `POST /api/v1/chat/completions`

## 7. 技术选型

### 7.1 platform-service

- Java 17
- Spring Boot 3
- Maven
- Spring Web
- Validation
- 后续可接入 Spring Security / JPA / MyBatis

### 7.2 ai-service

- Python 3.13
- FastAPI
- Pydantic
- 后续可接入 SQLAlchemy / Celery / LangChain 或自研编排

### 7.3 基础设施

- PostgreSQL
- Redis
- MinIO
- RabbitMQ 或 Kafka
- pgvector 或 Milvus
- Prometheus + Grafana

## 8. 仓库结构建议

```text
docs/
services/
  platform-service/
  ai-service/
```

## 9. 研发顺序

### 阶段一

- 固化服务边界
- 初始化 Java 平台服务
- 初始化 Python AI 服务
- 对齐内部调用协议

### 阶段二

- Java 落租户、应用、权限
- Python 落模型、知识库、对话
- 打通平台到 AI 的内部调用

### 阶段三

- 接数据库和对象存储
- 接真实模型
- 增加文档处理与检索
- 增加审计、监控、成本统计

## 10. 当前仓库实现范围

本轮代码已完成：

- 输出混合架构方案
- Java 平台服务接入 `JPA + H2`
- Python AI 服务接入 `SQLAlchemy + SQLite`
- 打通平台服务到 AI 服务的内部对话调用边界
- 调整仓库说明以匹配当前实现
