package com.example.platform.model;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.util.UUID;

// 创建应用时同时接住默认 provider / knowledge base 配置，后续对话可直接复用。
public record ApplicationCreateRequest(
    @NotBlank @Size(min = 2, max = 100) String name,
    @Size(max = 500) String description,
    @NotBlank String appType,
    @NotNull UUID tenantId,
    @Size(max = 4000) String systemPrompt,
    UUID defaultProviderId,
    UUID defaultKnowledgeBaseId
) {
}
