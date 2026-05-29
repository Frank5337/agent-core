package com.example.platform.controller;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.platform.model.AuditLogResponse;
import com.example.platform.service.AuditLogService;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(AuditLogController.class)
class AuditLogControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private AuditLogService auditLogService;

    @Test
    void listLogsSupportsFilters() throws Exception {
        UUID tenantId = UUID.randomUUID();

        when(auditLogService.listLogs(tenantId, null, "application", "APPLICATION_PUBLISHED")).thenReturn(
            List.of(
                new AuditLogResponse(
                    UUID.randomUUID(),
                    tenantId,
                    null,
                    "system",
                    "APPLICATION_PUBLISHED",
                    "application",
                    UUID.randomUUID().toString(),
                    "ops-assistant",
                    "Published application",
                    Instant.now()
                )
            )
        );

        mockMvc.perform(
                get("/api/v1/audit-logs")
                    .param("tenantId", tenantId.toString())
                    .param("resourceType", "application")
                    .param("action", "APPLICATION_PUBLISHED")
            )
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].action").value("APPLICATION_PUBLISHED"));
    }
}
