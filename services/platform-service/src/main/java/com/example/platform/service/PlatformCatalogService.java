package com.example.platform.service;

import com.example.platform.model.AiKnowledgeBaseResponse;
import com.example.platform.model.AiProviderResponse;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class PlatformCatalogService {

    private final AiGatewayClient aiGatewayClient;

    public PlatformCatalogService(AiGatewayClient aiGatewayClient) {
        this.aiGatewayClient = aiGatewayClient;
    }

    @Transactional(readOnly = true)
    public List<AiProviderResponse> listProviders() {
        return aiGatewayClient.listProviders();
    }

    @Transactional(readOnly = true)
    public List<AiKnowledgeBaseResponse> listKnowledgeBases() {
        return aiGatewayClient.listKnowledgeBases();
    }
}
