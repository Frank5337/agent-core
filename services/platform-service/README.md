# Platform Service

`platform-service` is the Java service for platform capabilities:

- tenant management
- application management
- platform-facing chat entrypoint

The service currently uses `Spring Boot + Spring Data JPA + H2`.
Application responses now include readable linked fields such as `tenantName`,
`defaultProviderName`, and `defaultKnowledgeBaseName` when they can be resolved
from `ai-service`.

## Prerequisites

- Java `17`
- Maven `3.9+`

## Run

Make sure `ai-service` is already running on `http://localhost:8000`.

```bash
mvn spring-boot:run
```

## Test

```bash
mvn test
```

## API

- `GET /health`
- `GET /api/v1/tenants`
- `GET /api/v1/tenants/{tenantId}`
- `POST /api/v1/tenants`
- `GET /api/v1/applications`
- `GET /api/v1/applications/{applicationId}`
- `POST /api/v1/applications`
- `POST /api/v1/applications/{applicationId}/chat`
