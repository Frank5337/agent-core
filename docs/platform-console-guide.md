# Platform Console 使用说明

这份文档说明 `platform-service` 内置管理台的使用方式。

页面入口：

- `http://localhost:8080`

适用范围：

- 租户管理
- 平台用户管理
- 角色查看
- 应用创建与发布
- 审计日志查看
- 应用级聊天联调

## 1. 启动前准备

先启动 `ai-service`：

```bash
cd services/ai-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8002
```

再启动 `platform-service`：

```bash
cd services/platform-service
mvn spring-boot:run
```

说明：

- `platform-service` 默认会调用 `http://localhost:8002`
- 如果 `ai-service` 没启动，页面里 `Provider Catalog` 和 `Knowledge Base Catalog` 会加载失败

## 2. 打开页面后你会看到什么

首页分成几块：

1. 顶部状态区
   - 看 `platform-service` 是否存活
   - 看 provider 和 knowledge base 目录是否能从 `ai-service` 拉到
2. 左侧管理区
   - 租户
   - 角色与平台用户
3. 右侧工作区
   - 应用工作台
   - 应用级聊天联调
   - 审计日志

## 3. 推荐使用顺序

建议按下面顺序操作，这样最顺：

1. 创建租户
2. 创建平台用户
3. 确认 provider / knowledge base 已从 `ai-service` 拉到
4. 创建应用
5. 发布应用
6. 用聊天联调区发一条消息
7. 看审计日志是否记录成功

## 4. 租户管理

位置：

- 左侧第一个卡片 `租户`

可以做的事：

- 创建租户
- 搜索租户
- 查看已有租户列表

填写说明：

- `租户名称`
  - 必填
  - 建议直接写业务域或部门名
- `租户描述`
  - 选填
  - 用来说明这个租户负责什么业务

创建成功后：

- 租户会出现在下面列表里
- 也会自动出现在后面“创建用户”和“创建应用”的下拉框里

## 5. 角色与平台用户

位置：

- 左侧第二个卡片 `角色与平台用户`

### 5.1 角色目录

当前内置 4 个固定角色：

- `PLATFORM_ADMIN`
- `TENANT_ADMIN`
- `APP_OPERATOR`
- `AUDITOR`

页面会显示每个角色的：

- 名称
- 描述
- 权限清单

这版只是“展示角色目录”，还没有真正做权限拦截。

### 5.2 创建平台用户

需要填写：

- 所属租户
- 角色
- 姓名
- 邮箱

创建成功后：

- 用户会出现在用户列表
- 也会出现在“应用级聊天联调”的操作者下拉框里

当前用途：

- 在发布应用或聊天联调时，作为操作者身份传递
- 审计日志里会记录这个名字

## 6. 应用工作台

位置：

- 右侧第一个大卡片 `应用工作台`

### 6.1 创建应用

需要填写：

- 所属租户
- 默认 Provider
- 默认知识库
- 应用名称
- 应用类型
- 应用描述
- `System Prompt`

字段说明：

- `默认 Provider`
  - 来自 `ai-service` 的 provider 目录
  - 如果没拉到，说明 `ai-service` 没启动或接口异常
- `默认知识库`
  - 来自 `ai-service` 的 knowledge base 目录
- `System Prompt`
  - 这是平台层保存的应用默认提示词
  - 聊天联调时会一起转发给 `ai-service`

创建成功后：

- 应用状态默认为 `draft`
- 应用会出现在下方应用列表里

### 6.2 筛选应用

支持：

- 按名称搜索
- 按租户过滤
- 按状态过滤

状态目前有两种：

- `draft`
- `published`

### 6.3 发布和退回草稿

每条应用卡片上都有按钮：

- 草稿应用：`发布应用`
- 已发布应用：`退回草稿`

点击后会发生：

1. 更新应用状态
2. 写入审计日志
3. 页面刷新显示最新状态

## 7. 应用级聊天联调

位置：

- 右侧中间卡片 `应用级聊天联调`

这个区域的意义是：

- 不直接调 Python 服务
- 而是走 Java 平台入口
- 用来验证平台侧是否正确带上了应用配置再转发给 `ai-service`

使用步骤：

1. 选择一个应用
2. 可选选择一个操作者
3. 输入消息
4. 点击 `发送消息`

发送后：

- 左侧会记录会话消息
- 右侧会显示回答结果
- 结果里会展示：
  - `Provider`
  - `Model`
  - `reply`

适合验证的问题：

- “你是谁”
- “请总结一下你当前的角色”
- “你当前使用的知识库和模型是什么”

## 8. 审计日志

位置：

- 右下角卡片 `审计日志`

可以按这些条件过滤：

- 租户
- 动作
- 资源类型

当前已经记录的动作包括：

- `TENANT_CREATED`
- `USER_CREATED`
- `APPLICATION_CREATED`
- `APPLICATION_PUBLISHED`
- `APPLICATION_MOVED_TO_DRAFT`

每条日志会显示：

- 动作名
- 资源名
- 租户
- 操作者
- 细节说明

## 9. 常见问题

### 9.1 页面打开了，但 provider 和 knowledge base 是空的

先检查：

- `ai-service` 是否已经启动在 `8002`
- `platform-service` 的配置是否还是默认：
  - [application.yml](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/platform-service/src/main/resources/application.yml:1)

### 9.2 聊天联调时报错

先检查：

- 目标应用是否已经创建
- `ai-service` 是否正常
- 目标 provider / knowledge base 在 `ai-service` 中是否真实存在

### 9.3 审计日志没有数据

先做一次写操作再刷新：

- 创建租户
- 创建平台用户
- 创建应用
- 发布应用

## 10. 当前边界

这版控制台是最小原型，还没补这些能力：

- 登录与鉴权
- 真正的 RBAC 拦截
- 应用编辑
- 应用删除
- 用户禁用 / 启用
- 审计日志导出
- 知识库明细查看
- Provider 管理页

## 11. 推荐演示路径

如果你要给别人演示，建议按这个顺序：

1. 打开 `http://localhost:8080`
2. 创建一个租户
3. 创建一个 `APP_OPERATOR`
4. 选择已存在的 provider 和 knowledge base
5. 创建一个应用
6. 发布应用
7. 在聊天联调区发一条消息
8. 最后切到审计日志，展示平台侧有留痕
