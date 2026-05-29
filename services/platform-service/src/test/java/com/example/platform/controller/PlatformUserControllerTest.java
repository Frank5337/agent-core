package com.example.platform.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.platform.model.PlatformUserResponse;
import com.example.platform.service.PlatformUserService;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(PlatformUserController.class)
class PlatformUserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private PlatformUserService platformUserService;

    @Test
    void listUsersReturnsUserList() throws Exception {
        UUID tenantId = UUID.randomUUID();

        when(platformUserService.listUsers(tenantId, "alice", "APP_OPERATOR", "active")).thenReturn(
            List.of(
                new PlatformUserResponse(
                    UUID.randomUUID(),
                    tenantId,
                    "team-a",
                    "alice@example.com",
                    "Alice",
                    "APP_OPERATOR",
                    "App Operator",
                    "active",
                    Instant.now()
                )
            )
        );

        mockMvc.perform(
                get("/api/v1/users")
                    .param("tenantId", tenantId.toString())
                    .param("q", "alice")
                    .param("roleCode", "APP_OPERATOR")
                    .param("status", "active")
            )
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].displayName").value("Alice"));
    }

    @Test
    void createUserReturnsCreated() throws Exception {
        UUID tenantId = UUID.randomUUID();
        UUID userId = UUID.randomUUID();

        when(platformUserService.createUser(any())).thenReturn(
            new PlatformUserResponse(
                userId,
                tenantId,
                "team-a",
                "alice@example.com",
                "Alice",
                "APP_OPERATOR",
                "App Operator",
                "active",
                Instant.now()
            )
        );

        mockMvc.perform(
                post("/api/v1/users")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("""
                        {
                          "tenantId": "%s",
                          "email": "alice@example.com",
                          "displayName": "Alice",
                          "roleCode": "APP_OPERATOR",
                          "status": "active"
                        }
                        """.formatted(tenantId))
            )
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").value(userId.toString()))
            .andExpect(jsonPath("$.roleCode").value("APP_OPERATOR"));
    }
}
