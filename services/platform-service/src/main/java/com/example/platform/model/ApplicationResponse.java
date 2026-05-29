package com.example.platform.model;

import java.time.Instant;
import java.util.UUID;

// 返回给前端的应用视图对象，带上可直接展示的关联名称和发布状态。
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
    String status,
    Instant publishedAt,
    Instant createdAt
) {
}
