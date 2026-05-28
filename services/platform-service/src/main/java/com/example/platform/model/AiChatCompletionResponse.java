package com.example.platform.model;

import java.util.Map;

public record AiChatCompletionResponse(
    String provider,
    String model,
    String reply,
    Map<String, Integer> usage
) {
}

