package com.example.platform.controller;

import com.example.platform.model.ApplicationChatRequest;
import com.example.platform.model.ApplicationChatResponse;
import com.example.platform.model.ApplicationCreateRequest;
import com.example.platform.model.ApplicationPublishRequest;
import com.example.platform.model.ApplicationResponse;
import com.example.platform.service.ApplicationService;
import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/applications")
public class ApplicationController {

    private final ApplicationService applicationService;

    public ApplicationController(ApplicationService applicationService) {
        this.applicationService = applicationService;
    }

    // 应用列表支持按租户、关键字和发布状态过滤。
    @GetMapping
    public List<ApplicationResponse> listApplications(
        @RequestParam(name = "tenantId", required = false) UUID tenantId,
        @RequestParam(name = "q", required = false) String query,
        @RequestParam(name = "status", required = false) String status
    ) {
        return applicationService.listApplications(tenantId, query, status);
    }

    @GetMapping("/{applicationId}")
    public ApplicationResponse getApplication(@PathVariable UUID applicationId) {
        return applicationService.getApplication(applicationId);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ApplicationResponse createApplication(@Valid @RequestBody ApplicationCreateRequest request) {
        return applicationService.createApplication(request);
    }

    @PostMapping("/{applicationId}/publish")
    public ApplicationResponse publishApplication(
        @PathVariable UUID applicationId,
        @RequestBody(required = false) ApplicationPublishRequest request
    ) {
        return applicationService.publishApplication(applicationId, request);
    }

    @PostMapping("/{applicationId}/draft")
    public ApplicationResponse moveApplicationToDraft(
        @PathVariable UUID applicationId,
        @RequestBody(required = false) ApplicationPublishRequest request
    ) {
        return applicationService.moveApplicationToDraft(applicationId, request);
    }

    // 对业务方暴露统一的应用对话入口，屏蔽底层 ai-service 细节。
    @PostMapping("/{applicationId}/chat")
    public ApplicationChatResponse chat(
        @PathVariable UUID applicationId,
        @Valid @RequestBody ApplicationChatRequest request
    ) {
        return applicationService.chat(applicationId, request);
    }
}
