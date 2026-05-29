# 当前运行状态

这份文档记录当前仓库的推荐启动方式、端口约定和已知注意事项。

## 1. 当前服务

- `services/ai-service`
  - Python `FastAPI`
  - 当前主要承载网站 RAG Demo
- `services/platform-service`
  - Java `Spring Boot`
  - 当前主要承载租户、用户、角色、应用、发布和审计

## 2. 推荐端口

### 2.1 网站 RAG Demo

- `ai-service`: `http://localhost:8002`

### 2.2 联调 platform-service

- `platform-service`: `http://localhost:8080`
- `ai-service`: `http://localhost:8002`

`platform-service` 默认配置已经指向 `8002`。

## 3. 当前数据层

### 3.1 platform-service

- 默认使用 H2 内存库
- 适合本地原型开发和接口联调

### 3.2 ai-service

- 当前主要使用 SQLite
- 当前环境里文件型 SQLite 曾出现过 `disk I/O error`
- 运行时更稳的方式是共享内存 SQLite 或独立可写目录

## 4. 已知注意事项

- 当前机器没有 `mvn`，所以 Java 测试和启动需要先安装 Maven
- 网站抓取依赖外网访问，若本机需要代理，需保证 `HTTP_PROXY/HTTPS_PROXY` 正常
- 网站 RAG 页面当前直接挂在 `ai-service`，还没有经过 `platform-service`
