package com.example.platform.model;

import java.time.Instant;
import java.util.UUID;

public record PlatformUserResponse(
    UUID id,
    UUID tenantId,
    String tenantName,
    String email,
    String displayName,
    String roleCode,
    String roleName,
    String status,
    Instant createdAt
) {
}
