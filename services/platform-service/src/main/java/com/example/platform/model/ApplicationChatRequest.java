package com.example.platform.model;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import java.util.List;
import java.util.Map;

public record ApplicationChatRequest(
    @Valid @NotEmpty List<ChatMessageRequest> messages,
    Map<String, Object> metadata
) {
}

