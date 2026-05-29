package com.example.platform.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.platform.model.ApplicationChatResponse;
import com.example.platform.model.ApplicationResponse;
import com.example.platform.service.ApplicationService;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(ApplicationController.class)
class ApplicationControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ApplicationService applicationService;

    @Test
    void listApplicationsSupportsFilters() throws Exception {
        UUID tenantId = UUID.randomUUID();

        when(applicationService.listApplications(tenantId, "ops", "published")).thenReturn(
            List.of(
                new ApplicationResponse(
                    UUID.randomUUID(),
                    tenantId,
                    "team-a",
                    "ops-assistant",
                    "for operations",
                    "chatbot",
                    "be concise",
                    null,
                    null,
                    null,
                    null,
                    "published",
                    Instant.now(),
                    Instant.now()
                )
            )
        );

        mockMvc.perform(
                get("/api/v1/applications")
                    .param("tenantId", tenantId.toString())
                    .param("q", "ops")
                    .param("status", "published")
            )
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].name").value("ops-assistant"))
            .andExpect(jsonPath("$[0].status").value("published"));
    }

    @Test
    void getApplicationReturnsDetail() throws Exception {
        UUID tenantId = UUID.randomUUID();
        UUID applicationId = UUID.randomUUID();

        when(applicationService.getApplication(applicationId)).thenReturn(
            new ApplicationResponse(
                applicationId,
                tenantId,
                "team-a",
                "ops-assistant",
                "for operations",
                "chatbot",
                "be concise",
                null,
                null,
                null,
                null,
                "draft",
                null,
                Instant.now()
            )
        );

        mockMvc.perform(get("/api/v1/applications/{applicationId}", applicationId))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(applicationId.toString()))
            .andExpect(jsonPath("$.name").value("ops-assistant"));
    }

    @Test
    void createApplicationReturnsCreated() throws Exception {
        UUID tenantId = UUID.randomUUID();
        UUID applicationId = UUID.randomUUID();

        when(applicationService.createApplication(any())).thenReturn(
            new ApplicationResponse(
                applicationId,
                tenantId,
                "team-a",
                "ops-assistant",
                "for operations",
                "chatbot",
                "be concise",
                null,
                null,
                null,
                null,
                "draft",
                null,
                Instant.now()
            )
        );

        mockMvc.perform(
                post("/api/v1/applications")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("""
                        {
                          "name": "ops-assistant",
                          "description": "for operations",
                          "appType": "chatbot",
                          "tenantId": "%s",
                          "systemPrompt": "be concise"
                        }
                        """.formatted(tenantId))
            )
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.name").value("ops-assistant"))
            .andExpect(jsonPath("$.tenantId").value(tenantId.toString()))
            .andExpect(jsonPath("$.status").value("draft"));
    }

    @Test
    void publishApplicationReturnsPublishedStatus() throws Exception {
        UUID tenantId = UUID.randomUUID();
        UUID applicationId = UUID.randomUUID();

        when(applicationService.publishApplication(any(), any())).thenReturn(
            new ApplicationResponse(
                applicationId,
                tenantId,
                "team-a",
                "ops-assistant",
                "for operations",
                "chatbot",
                "be concise",
                null,
                null,
                null,
                null,
                "published",
                Instant.now(),
                Instant.now()
            )
        );

        mockMvc.perform(
                post("/api/v1/applications/{applicationId}/publish", applicationId)
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("""
                        {
                          "note": "ready for release"
                        }
                        """)
            )
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("published"));
    }

    @Test
    void chatReturnsGatewayResponse() throws Exception {
        UUID applicationId = UUID.randomUUID();

        when(applicationService.chat(any(), any())).thenReturn(
            new ApplicationChatResponse(
                "default-provider",
                "gpt-4o-mini",
                "ok",
                Map.of("total_tokens", 42)
            )
        );

        mockMvc.perform(
                post("/api/v1/applications/{applicationId}/chat", applicationId)
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("""
                        {
                          "messages": [
                            {
                              "role": "user",
                              "content": "hello"
                            }
                          ]
                        }
                        """)
            )
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.provider").value("default-provider"))
            .andExpect(jsonPath("$.usage.total_tokens").value(42));
    }
}
