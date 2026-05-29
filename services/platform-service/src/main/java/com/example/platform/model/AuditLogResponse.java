package com.example.platform.model;

import java.time.Instant;
import java.util.UUID;

public record AuditLogResponse(
    UUID id,
    UUID tenantId,
    UUID actorUserId,
    String actorDisplayName,
    String action,
    String resourceType,
    String resourceId,
    String resourceName,
    String detail,
    Instant createdAt
) {
}
