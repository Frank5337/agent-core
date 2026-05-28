package com.example.platform.controller;

import com.example.platform.model.TenantCreateRequest;
import com.example.platform.model.TenantResponse;
import com.example.platform.service.TenantService;
import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/tenants")
public class TenantController {

    private final TenantService tenantService;

    public TenantController(TenantService tenantService) {
        this.tenantService = tenantService;
    }

    // 提供租户列表和简单搜索，方便管理台先快速对接。
    @GetMapping
    public List<TenantResponse> listTenants(@RequestParam(name = "q", required = false) String query) {
        return tenantService.listTenants(query);
    }

    @GetMapping("/{tenantId}")
    public TenantResponse getTenant(@PathVariable UUID tenantId) {
        return tenantService.getTenant(tenantId);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public TenantResponse createTenant(@Valid @RequestBody TenantCreateRequest request) {
        return tenantService.createTenant(request);
    }
}
