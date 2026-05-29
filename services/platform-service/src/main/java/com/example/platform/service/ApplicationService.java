package com.example.platform.service;

import com.example.platform.entity.ApplicationEntity;
import com.example.platform.entity.PlatformUserEntity;
import com.example.platform.entity.TenantEntity;
import com.example.platform.exception.ResourceNotFoundException;
import com.example.platform.model.AiChatCompletionRequest;
import com.example.platform.model.AiChatCompletionResponse;
import com.example.platform.model.AiKnowledgeBaseResponse;
import com.example.platform.model.AiProviderResponse;
import com.example.platform.model.ApplicationChatRequest;
import com.example.platform.model.ApplicationChatResponse;
import com.example.platform.model.ApplicationCreateRequest;
import com.example.platform.model.ApplicationPublishRequest;
import com.example.platform.model.ApplicationResponse;
import com.example.platform.repository.ApplicationRepository;
import java.time.Instant;
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
    private final AuditLogService auditLogService;
    private final PlatformUserService platformUserService;

    public ApplicationService(
        ApplicationRepository applicationRepository,
        TenantService tenantService,
        AiGatewayClient aiGatewayClient,
        AuditLogService auditLogService,
        PlatformUserService platformUserService
    ) {
        this.applicationRepository = applicationRepository;
        this.tenantService = tenantService;
        this.aiGatewayClient = aiGatewayClient;
        this.auditLogService = auditLogService;
        this.platformUserService = platformUserService;
    }

    @Transactional(readOnly = true)
    public List<ApplicationResponse> listApplications(UUID tenantId, String query, String status) {
        List<ApplicationEntity> applications;

        // 原型阶段先覆盖列表页最常见的租户、关键字、发布态过滤。
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

        return applications.stream()
            .filter(application -> status == null || status.isBlank() || status.equalsIgnoreCase(application.getStatus()))
            .map(this::toResponse)
            .toList();
    }

    @Transactional(readOnly = true)
    public ApplicationResponse getApplication(UUID applicationId) {
        return toResponse(requireApplication(applicationId));
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
        application.setStatus("draft");

        ApplicationEntity saved = applicationRepository.save(application);
        auditLogService.record(
            tenant.getId(),
            null,
            "system",
            "APPLICATION_CREATED",
            "application",
            saved.getId(),
            saved.getName(),
            "Created application in draft status"
        );
        return toResponse(saved);
    }

    @Transactional
    public ApplicationResponse publishApplication(UUID applicationId, ApplicationPublishRequest request) {
        ApplicationEntity application = requireApplication(applicationId);
        PlatformUserEntity actor = resolveActor(request == null ? null : request.actorUserId());

        application.setStatus("published");
        application.setPublishedAt(Instant.now());
        ApplicationEntity saved = applicationRepository.save(application);
        auditLogService.record(
            application.getTenant().getId(),
            actor == null ? null : actor.getId(),
            actor == null ? "system" : actor.getDisplayName(),
            "APPLICATION_PUBLISHED",
            "application",
            saved.getId(),
            saved.getName(),
            normalizeNote(request, "Published application")
        );
        return toResponse(saved);
    }

    @Transactional
    public ApplicationResponse moveApplicationToDraft(UUID applicationId, ApplicationPublishRequest request) {
        ApplicationEntity application = requireApplication(applicationId);
        PlatformUserEntity actor = resolveActor(request == null ? null : request.actorUserId());

        application.setStatus("draft");
        application.setPublishedAt(null);
        ApplicationEntity saved = applicationRepository.save(application);
        auditLogService.record(
            application.getTenant().getId(),
            actor == null ? null : actor.getId(),
            actor == null ? "system" : actor.getDisplayName(),
            "APPLICATION_MOVED_TO_DRAFT",
            "application",
            saved.getId(),
            saved.getName(),
            normalizeNote(request, "Moved application back to draft")
        );
        return toResponse(saved);
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

    private PlatformUserEntity resolveActor(UUID actorUserId) {
        if (actorUserId == null) {
            return null;
        }
        return platformUserService.requireUser(actorUserId);
    }

    private String normalizeNote(ApplicationPublishRequest request, String fallback) {
        if (request == null || request.note() == null || request.note().isBlank()) {
            return fallback;
        }
        return request.note().trim();
    }

    private ApplicationEntity requireApplication(UUID applicationId) {
        return applicationRepository.findById(applicationId)
            .orElseThrow(() -> new ResourceNotFoundException("application not found"));
    }

    private ApplicationResponse toResponse(ApplicationEntity application) {
        String providerName = null;
        String knowledgeBaseName = null;

        // 尽量补齐可读名称，降低前端联调复杂度。
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
            application.getStatus(),
            application.getPublishedAt(),
            application.getCreatedAt()
        );
    }
}
