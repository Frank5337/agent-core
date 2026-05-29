package com.example.platform.controller;

import com.example.platform.model.AiKnowledgeBaseResponse;
import com.example.platform.model.AiProviderResponse;
import com.example.platform.service.PlatformCatalogService;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/catalog")
public class PlatformCatalogController {

    private final PlatformCatalogService platformCatalogService;

    public PlatformCatalogController(PlatformCatalogService platformCatalogService) {
        this.platformCatalogService = platformCatalogService;
    }

    @GetMapping("/providers")
    public List<AiProviderResponse> listProviders() {
        return platformCatalogService.listProviders();
    }

    @GetMapping("/knowledge-bases")
    public List<AiKnowledgeBaseResponse> listKnowledgeBases() {
        return platformCatalogService.listKnowledgeBases();
    }
}
