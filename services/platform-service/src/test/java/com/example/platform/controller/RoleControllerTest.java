package com.example.platform.controller;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.platform.model.RoleDefinitionResponse;
import com.example.platform.service.RoleCatalogService;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(RoleController.class)
class RoleControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private RoleCatalogService roleCatalogService;

    @Test
    void listRolesReturnsCatalog() throws Exception {
        when(roleCatalogService.listRoles()).thenReturn(
            List.of(new RoleDefinitionResponse("PLATFORM_ADMIN", "Platform Admin", "owns all", List.of("tenant:write")))
        );

        mockMvc.perform(get("/api/v1/roles"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].code").value("PLATFORM_ADMIN"));
    }
}
