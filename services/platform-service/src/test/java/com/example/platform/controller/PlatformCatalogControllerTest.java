package com.example.platform.controller;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.platform.model.AiKnowledgeBaseResponse;
import com.example.platform.model.AiProviderResponse;
import com.example.platform.service.PlatformCatalogService;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(PlatformCatalogController.class)
class PlatformCatalogControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private PlatformCatalogService platformCatalogService;

    @Test
    void listProvidersReturnsCatalog() throws Exception {
        when(platformCatalogService.listProviders()).thenReturn(
            List.of(
                new AiProviderResponse(
                    UUID.randomUUID(),
                    "deepseek-prod",
                    "deepseek",
                    "deepseek-v4-flash",
                    "https://api.deepseek.com",
                    "sk-***",
                    true,
                    Instant.now()
                )
            )
        );

        mockMvc.perform(get("/api/v1/catalog/providers"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].name").value("deepseek-prod"));
    }

    @Test
    void listKnowledgeBasesReturnsCatalog() throws Exception {
        when(platformCatalogService.listKnowledgeBases()).thenReturn(
            List.of(
                new AiKnowledgeBaseResponse(
                    UUID.randomUUID(),
                    "website-rag",
                    "website knowledge base",
                    null,
                    3,
                    Instant.now()
                )
            )
        );

        mockMvc.perform(get("/api/v1/catalog/knowledge-bases"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].name").value("website-rag"));
    }
}
