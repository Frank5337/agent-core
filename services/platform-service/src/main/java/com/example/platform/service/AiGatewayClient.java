package com.example.platform.service;

import com.example.platform.model.AiKnowledgeBaseResponse;
import com.example.platform.model.AiProviderResponse;
import com.example.platform.model.AiChatCompletionRequest;
import com.example.platform.model.AiChatCompletionResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class AiGatewayClient {

    private final RestClient restClient;

    public AiGatewayClient(RestClient aiRestClient) {
        this.restClient = aiRestClient;
    }

    public AiChatCompletionResponse complete(AiChatCompletionRequest request) {
        // 这里收敛平台到 AI 的内部 HTTP 调用，后续切鉴权或重试时只需要改这一层。
        return restClient.post()
            .uri("/api/v1/chat/completions")
            .body(request)
            .retrieve()
            .body(AiChatCompletionResponse.class);
    }

    public AiProviderResponse getProvider(String providerId) {
        return restClient.get()
            .uri("/api/v1/providers/{providerId}", providerId)
            .retrieve()
            .body(AiProviderResponse.class);
    }

    public AiKnowledgeBaseResponse getKnowledgeBase(String knowledgeBaseId) {
        return restClient.get()
            .uri("/api/v1/knowledge-bases/{knowledgeBaseId}", knowledgeBaseId)
            .retrieve()
            .body(AiKnowledgeBaseResponse.class);
    }
}
