package com.example.platform.service;

import com.example.platform.entity.TenantEntity;
import com.example.platform.exception.ResourceNotFoundException;
import com.example.platform.model.TenantCreateRequest;
import com.example.platform.model.TenantResponse;
import com.example.platform.repository.TenantRepository;
import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class TenantService {

    private final TenantRepository tenantRepository;
    private final AuditLogService auditLogService;

    public TenantService(TenantRepository tenantRepository, AuditLogService auditLogService) {
        this.tenantRepository = tenantRepository;
        this.auditLogService = auditLogService;
    }

    @Transactional(readOnly = true)
    public List<TenantResponse> listTenants(String query) {
        // 原型阶段先支持最常见的名称模糊搜索即可。
        if (query == null || query.isBlank()) {
            return tenantRepository.findAllByOrderByCreatedAtDesc().stream().map(this::toResponse).toList();
        }
        return tenantRepository.findByNameContainingIgnoreCaseOrderByCreatedAtDesc(query.trim()).stream()
            .map(this::toResponse)
            .toList();
    }

    @Transactional(readOnly = true)
    public TenantResponse getTenant(UUID tenantId) {
        return toResponse(requireTenant(tenantId));
    }

    @Transactional
    public TenantResponse createTenant(TenantCreateRequest request) {
        TenantEntity tenant = new TenantEntity();
        tenant.setName(request.name());
        tenant.setDescription(request.description());

        TenantEntity saved = tenantRepository.save(tenant);
        auditLogService.record(
            saved.getId(),
            null,
            "system",
            "TENANT_CREATED",
            "tenant",
            saved.getId(),
            saved.getName(),
            "Created tenant"
        );
        return toResponse(saved);
    }

    @Transactional(readOnly = true)
    public TenantEntity requireTenant(UUID tenantId) {
        return tenantRepository.findById(tenantId)
            .orElseThrow(() -> new ResourceNotFoundException("tenant not found"));
    }

    private TenantResponse toResponse(TenantEntity tenant) {
        return new TenantResponse(
            tenant.getId(),
            tenant.getName(),
            tenant.getDescription(),
            tenant.getCreatedAt()
        );
    }
}
