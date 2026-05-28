package com.example.platform.model;

import java.time.Instant;
import java.util.UUID;

public record AiKnowledgeBaseResponse(
    UUID id,
    String name,
    String description,
    UUID embeddingProviderId,
    int documentCount,
    Instant createdAt
) {
}

