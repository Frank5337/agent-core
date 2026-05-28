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

    public TenantService(TenantRepository tenantRepository) {
        this.tenantRepository = tenantRepository;
    }

    @Transactional(readOnly = true)
    public List<TenantResponse> listTenants(String query) {
        // 管理台列表默认按创建时间倒序，输入关键字时只做名字模糊搜索。
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
        return toResponse(tenantRepository.save(tenant));
    }

    @Transactional(readOnly = true)
    public TenantEntity requireTenant(UUID tenantId) {
        // 统一在服务层兜底 404，避免上层重复写不存在判断。
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
