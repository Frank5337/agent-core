package com.example.platform.model;

import java.time.Instant;
import java.util.UUID;

// 返回给前端的应用视图对象，尽量带上可直接展示的名称字段。
public record ApplicationResponse(
    UUID id,
    UUID tenantId,
    String tenantName,
    String name,
    String description,
    String appType,
    String systemPrompt,
    UUID defaultProviderId,
    String defaultProviderName,
    UUID defaultKnowledgeBaseId,
    String defaultKnowledgeBaseName,
    Instant createdAt
) {
}
