package com.example.platform.model;

import java.time.Instant;
import java.util.UUID;

public record AiProviderResponse(
    UUID id,
    String name,
    String providerType,
    String modelName,
    String endpoint,
    String apiKeyMasked,
    boolean isDefault,
    Instant createdAt
) {
}

