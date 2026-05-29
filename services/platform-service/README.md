# Platform Service

`platform-service` is the Java platform layer for the AI middle platform.

Current MVP capabilities:

- tenant management
- platform user management
- role catalog
- application management
- application publish / move-to-draft flow
- audit log query
- platform-facing chat entrypoint
- built-in web console on `/`

The service uses `Spring Boot + Spring Data JPA + H2`.

Usage guide:

- [docs/platform-console-guide.md](/d:/Users/hzito02/IdeaProjects/codex/agent-core/docs/platform-console-guide.md)

## Prerequisites

- Java `17`
- Maven `3.9+`

## Run

Make sure `ai-service` is already running.

The default local target is now:

- `http://localhost:8002`

Start the service:

```bash
mvn spring-boot:run
```

Then open:

- `http://localhost:8080`

## Test

```bash
mvn test
```

## API

- `GET /health`
- `GET /actuator/health`
- `GET /api/v1/tenants`
- `GET /api/v1/tenants/{tenantId}`
- `POST /api/v1/tenants`
- `GET /api/v1/users`
- `GET /api/v1/users/{userId}`
- `POST /api/v1/users`
- `GET /api/v1/roles`
- `GET /api/v1/catalog/providers`
- `GET /api/v1/catalog/knowledge-bases`
- `GET /api/v1/applications`
- `GET /api/v1/applications/{applicationId}`
- `POST /api/v1/applications`
- `POST /api/v1/applications/{applicationId}/publish`
- `POST /api/v1/applications/{applicationId}/draft`
- `POST /api/v1/applications/{applicationId}/chat`
- `GET /api/v1/audit-logs`
