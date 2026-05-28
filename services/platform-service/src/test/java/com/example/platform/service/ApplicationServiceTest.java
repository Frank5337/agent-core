package com.example.platform.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.example.platform.entity.ApplicationEntity;
import com.example.platform.entity.TenantEntity;
import com.example.platform.model.AiChatCompletionResponse;
import com.example.platform.model.ApplicationChatRequest;
import com.example.platform.model.ApplicationChatResponse;
import com.example.platform.model.ApplicationCreateRequest;
import com.example.platform.model.ChatMessageRequest;
import com.example.platform.repository.ApplicationRepository;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class ApplicationServiceTest {

    @Mock
    private ApplicationRepository applicationRepository;

    @Mock
    private TenantService tenantService;

    @Mock
    private AiGatewayClient aiGatewayClient;

    @InjectMocks
    private ApplicationService applicationService;

    @Test
    void createApplicationPersistsTenantRelationship() {
        // 重点验证创建时是否把租户关系和系统提示词带进持久化结果。
        UUID tenantId = UUID.randomUUID();
        TenantEntity tenant = new TenantEntity();
        tenant.setId(tenantId);
        tenant.setName("team-a");
        tenant.setDescription("tenant");
        tenant.setCreatedAt(Instant.now());

        when(tenantService.requireTenant(tenantId)).thenReturn(tenant);
        when(applicationRepository.save(any(ApplicationEntity.class))).thenAnswer(invocation -> {
            ApplicationEntity entity = invocation.getArgument(0);
            entity.setId(UUID.randomUUID());
            entity.setCreatedAt(Instant.now());
            return entity;
        });

        var response = applicationService.createApplication(
            new ApplicationCreateRequest(
                "ops-assistant",
                "for operations",
                "chatbot",
                tenantId,
                "be concise",
                null,
                null
            )
        );

        assertEquals("ops-assistant", response.name());
        assertEquals("be concise", response.systemPrompt());
        assertEquals(tenantId, response.tenantId());
        assertEquals("team-a", response.tenantName());
        assertNotNull(response.id());
    }

    @Test
    void chatDelegatesToAiGateway() {
        // 平台对话测试关注“是否正确组装并转发 ai 请求”。
        UUID tenantId = UUID.randomUUID();
        UUID applicationId = UUID.randomUUID();
        UUID providerId = UUID.randomUUID();
        UUID knowledgeBaseId = UUID.randomUUID();

        TenantEntity tenant = new TenantEntity();
        tenant.setId(tenantId);
        tenant.setName("team-a");
        tenant.setDescription("tenant");
        tenant.setCreatedAt(Instant.now());

        ApplicationEntity application = new ApplicationEntity();
        application.setId(applicationId);
        application.setTenant(tenant);
        application.setName("ops-assistant");
        application.setDescription("for operations");
        application.setAppType("chatbot");
        application.setSystemPrompt("be concise");
        application.setDefaultProviderId(providerId);
        application.setDefaultKnowledgeBaseId(knowledgeBaseId);
        application.setCreatedAt(Instant.now());

        when(applicationRepository.findById(applicationId)).thenReturn(Optional.of(application));
        when(aiGatewayClient.complete(any())).thenReturn(
            new AiChatCompletionResponse("default-provider", "gpt-4o-mini", "ok", Map.of("total_tokens", 42))
        );

        ApplicationChatResponse response = applicationService.chat(
            applicationId,
            new ApplicationChatRequest(
                List.of(new ChatMessageRequest("user", "hello")),
                null
            )
        );

        ArgumentCaptor<com.example.platform.model.AiChatCompletionRequest> requestCaptor =
            ArgumentCaptor.forClass(com.example.platform.model.AiChatCompletionRequest.class);
        verify(aiGatewayClient).complete(requestCaptor.capture());

        assertEquals("default-provider", response.provider());
        assertTrue(requestCaptor.getValue().metadata().isEmpty());
        assertEquals("be concise", requestCaptor.getValue().systemPrompt());
        assertEquals(applicationId, requestCaptor.getValue().applicationId());
    }
}
