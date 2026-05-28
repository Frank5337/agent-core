package com.example.platform.model;

import java.util.List;
import java.util.Map;
import java.util.UUID;

public record AiChatCompletionRequest(
    String providerId,
    UUID knowledgeBaseId,
    String systemPrompt,
    UUID tenantId,
    UUID applicationId,
    List<ChatMessageRequest> messages,
    Map<String, Object> metadata
) {
}

