package com.example.platform.service;

import com.example.platform.entity.ApplicationEntity;
import com.example.platform.entity.TenantEntity;
import com.example.platform.exception.ResourceNotFoundException;
import com.example.platform.model.AiChatCompletionRequest;
import com.example.platform.model.AiChatCompletionResponse;
import com.example.platform.model.AiKnowledgeBaseResponse;
import com.example.platform.model.AiProviderResponse;
import com.example.platform.model.ApplicationChatRequest;
import com.example.platform.model.ApplicationChatResponse;
import com.example.platform.model.ApplicationCreateRequest;
import com.example.platform.model.ApplicationResponse;
import com.example.platform.repository.ApplicationRepository;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestClientException;

@Service
public class ApplicationService {

    private final ApplicationRepository applicationRepository;
    private final TenantService tenantService;
    private final AiGatewayClient aiGatewayClient;

    public ApplicationService(
        ApplicationRepository applicationRepository,
        TenantService tenantService,
        AiGatewayClient aiGatewayClient
    ) {
        this.applicationRepository = applicationRepository;
        this.tenantService = tenantService;
        this.aiGatewayClient = aiGatewayClient;
    }

    @Transactional(readOnly = true)
    public List<ApplicationResponse> listApplications(UUID tenantId, String query) {
        List<ApplicationEntity> applications;

        // 先按租户和关键字组合过滤，满足管理台最常见的查询场景。
        if (tenantId != null && query != null && !query.isBlank()) {
            applications = applicationRepository.findByTenant_IdAndNameContainingIgnoreCaseOrderByCreatedAtDesc(
                tenantId,
                query.trim()
            );
        } else if (tenantId != null) {
            applications = applicationRepository.findByTenant_IdOrderByCreatedAtDesc(tenantId);
        } else if (query != null && !query.isBlank()) {
            applications = applicationRepository.findByNameContainingIgnoreCaseOrderByCreatedAtDesc(query.trim());
        } else {
            applications = applicationRepository.findAllByOrderByCreatedAtDesc();
        }

        return applications.stream().map(this::toResponse).toList();
    }

    @Transactional(readOnly = true)
    public ApplicationResponse getApplication(UUID applicationId) {
        ApplicationEntity application = applicationRepository.findById(applicationId)
            .orElseThrow(() -> new ResourceNotFoundException("application not found"));
        return toResponse(application);
    }

    @Transactional
    public ApplicationResponse createApplication(ApplicationCreateRequest request) {
        TenantEntity tenant = tenantService.requireTenant(request.tenantId());

        ApplicationEntity application = new ApplicationEntity();
        application.setTenant(tenant);
        application.setName(request.name());
        application.setDescription(request.description());
        application.setAppType(request.appType());
        application.setSystemPrompt(request.systemPrompt());
        application.setDefaultProviderId(request.defaultProviderId());
        application.setDefaultKnowledgeBaseId(request.defaultKnowledgeBaseId());
        return toResponse(applicationRepository.save(application));
    }

    @Transactional(readOnly = true)
    public ApplicationChatResponse chat(UUID applicationId, ApplicationChatRequest request) {
        ApplicationEntity application = requireApplication(applicationId);

        // 平台服务负责补齐应用默认配置，再把请求转发给 ai-service。
        AiChatCompletionResponse aiResponse = aiGatewayClient.complete(
            new AiChatCompletionRequest(
                application.getDefaultProviderId() == null ? null : application.getDefaultProviderId().toString(),
                application.getDefaultKnowledgeBaseId(),
                application.getSystemPrompt(),
                application.getTenant().getId(),
                application.getId(),
                request.messages(),
                request.metadata() == null ? Map.of() : request.metadata()
            )
        );

        return new ApplicationChatResponse(
            aiResponse.provider(),
            aiResponse.model(),
            aiResponse.reply(),
            aiResponse.usage()
        );
    }

    private ApplicationEntity requireApplication(UUID applicationId) {
        return applicationRepository.findById(applicationId)
            .orElseThrow(() -> new ResourceNotFoundException("application not found"));
    }

    private ApplicationResponse toResponse(ApplicationEntity application) {
        String providerName = null;
        String knowledgeBaseName = null;

        // 详情接口尽量返回可读名称，方便前端直接展示。
        if (application.getDefaultProviderId() != null) {
            try {
                AiProviderResponse provider = aiGatewayClient.getProvider(application.getDefaultProviderId().toString());
                providerName = provider == null ? null : provider.name();
            } catch (RestClientException ignored) {
                providerName = null;
            }
        }

        if (application.getDefaultKnowledgeBaseId() != null) {
            try {
                AiKnowledgeBaseResponse knowledgeBase =
                    aiGatewayClient.getKnowledgeBase(application.getDefaultKnowledgeBaseId().toString());
                knowledgeBaseName = knowledgeBase == null ? null : knowledgeBase.name();
            } catch (RestClientException ignored) {
                knowledgeBaseName = null;
            }
        }

        return new ApplicationResponse(
            application.getId(),
            application.getTenant().getId(),
            application.getTenant().getName(),
            application.getName(),
            application.getDescription(),
            application.getAppType(),
            application.getSystemPrompt(),
            application.getDefaultProviderId(),
            providerName,
            application.getDefaultKnowledgeBaseId(),
            knowledgeBaseName,
            application.getCreatedAt()
        );
    }
}
