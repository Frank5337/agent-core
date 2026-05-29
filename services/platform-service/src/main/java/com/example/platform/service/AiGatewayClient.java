package com.example.platform.service;

import com.example.platform.model.AiChatCompletionRequest;
import com.example.platform.model.AiChatCompletionResponse;
import com.example.platform.model.AiKnowledgeBaseResponse;
import com.example.platform.model.AiProviderResponse;
import java.util.List;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class AiGatewayClient {

    private final RestClient restClient;

    public AiGatewayClient(RestClient aiRestClient) {
        this.restClient = aiRestClient;
    }

    public AiChatCompletionResponse complete(AiChatCompletionRequest request) {
        // 平台到 AI 的内部调用统一收口在这里，便于后续补鉴权和重试。
        return restClient.post()
            .uri("/api/v1/chat/completions")
            .body(request)
            .retrieve()
            .body(AiChatCompletionResponse.class);
    }

    public List<AiProviderResponse> listProviders() {
        return restClient.get()
            .uri("/api/v1/providers")
            .retrieve()
            .body(new ParameterizedTypeReference<>() {});
    }

    public AiProviderResponse getProvider(String providerId) {
        return restClient.get()
            .uri("/api/v1/providers/{providerId}", providerId)
            .retrieve()
            .body(AiProviderResponse.class);
    }

    public List<AiKnowledgeBaseResponse> listKnowledgeBases() {
        return restClient.get()
            .uri("/api/v1/knowledge-bases")
            .retrieve()
            .body(new ParameterizedTypeReference<>() {});
    }

    public AiKnowledgeBaseResponse getKnowledgeBase(String knowledgeBaseId) {
        return restClient.get()
            .uri("/api/v1/knowledge-bases/{knowledgeBaseId}", knowledgeBaseId)
            .retrieve()
            .body(AiKnowledgeBaseResponse.class);
    }
}
