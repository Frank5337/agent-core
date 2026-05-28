package com.example.platform.model;

import java.time.Instant;
import java.util.UUID;

// 租户响应保持轻量，先覆盖管理台列表和详情页需要的基础字段。
public record TenantResponse(
    UUID id,
    String name,
    String description,
    Instant createdAt
) {
}
