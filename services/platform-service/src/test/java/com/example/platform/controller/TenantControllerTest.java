package com.example.platform.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.platform.model.TenantResponse;
import com.example.platform.service.TenantService;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(TenantController.class)
class TenantControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private TenantService tenantService;

    @Test
    void listTenantsSupportsQuery() throws Exception {
        when(tenantService.listTenants("team")).thenReturn(
            List.of(new TenantResponse(UUID.randomUUID(), "team-a", "tenant", Instant.now()))
        );

        mockMvc.perform(get("/api/v1/tenants").param("q", "team"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].name").value("team-a"));
    }

    @Test
    void getTenantReturnsDetail() throws Exception {
        UUID tenantId = UUID.randomUUID();
        when(tenantService.getTenant(tenantId)).thenReturn(
            new TenantResponse(tenantId, "team-a", "tenant", Instant.now())
        );

        mockMvc.perform(get("/api/v1/tenants/{tenantId}", tenantId))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(tenantId.toString()))
            .andExpect(jsonPath("$.name").value("team-a"));
    }

    @Test
    void createTenantReturnsCreated() throws Exception {
        UUID tenantId = UUID.randomUUID();
        when(tenantService.createTenant(any())).thenReturn(
            new TenantResponse(tenantId, "team-a", "tenant", Instant.now())
        );

        mockMvc.perform(
                post("/api/v1/tenants")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("""
                        {
                          "name": "team-a",
                          "description": "tenant"
                        }
                        """)
            )
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").value(tenantId.toString()))
            .andExpect(jsonPath("$.name").value("team-a"));
    }
}
