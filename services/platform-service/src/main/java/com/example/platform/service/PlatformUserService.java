package com.example.platform.service;

import com.example.platform.entity.PlatformUserEntity;
import com.example.platform.entity.TenantEntity;
import com.example.platform.exception.ResourceNotFoundException;
import com.example.platform.model.PlatformUserCreateRequest;
import com.example.platform.model.PlatformUserResponse;
import com.example.platform.model.RoleDefinitionResponse;
import com.example.platform.repository.PlatformUserRepository;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class PlatformUserService {

    private final PlatformUserRepository platformUserRepository;
    private final TenantService tenantService;
    private final RoleCatalogService roleCatalogService;
    private final AuditLogService auditLogService;

    public PlatformUserService(
        PlatformUserRepository platformUserRepository,
        TenantService tenantService,
        RoleCatalogService roleCatalogService,
        AuditLogService auditLogService
    ) {
        this.platformUserRepository = platformUserRepository;
        this.tenantService = tenantService;
        this.roleCatalogService = roleCatalogService;
        this.auditLogService = auditLogService;
    }

    @Transactional(readOnly = true)
    public List<PlatformUserResponse> listUsers(UUID tenantId, String query, String roleCode, String status) {
        List<PlatformUserEntity> users;
        if (tenantId != null) {
            users = platformUserRepository.findByTenant_IdOrderByCreatedAtDesc(tenantId);
        } else if (query != null && !query.isBlank()) {
            users = platformUserRepository.findByDisplayNameContainingIgnoreCaseOrEmailContainingIgnoreCaseOrderByCreatedAtDesc(
                query.trim(),
                query.trim()
            );
        } else {
            users = platformUserRepository.findAllByOrderByCreatedAtDesc();
        }

        return users.stream()
            .filter(user -> query == null || query.isBlank() || matchesQuery(user, query))
            .filter(user -> roleCode == null || roleCode.isBlank() || roleCode.equalsIgnoreCase(user.getRoleCode()))
            .filter(user -> status == null || status.isBlank() || status.equalsIgnoreCase(user.getStatus()))
            .map(this::toResponse)
            .toList();
    }

    @Transactional(readOnly = true)
    public PlatformUserResponse getUser(UUID userId) {
        return toResponse(requireUser(userId));
    }

    @Transactional
    public PlatformUserResponse createUser(PlatformUserCreateRequest request) {
        TenantEntity tenant = tenantService.requireTenant(request.tenantId());
        RoleDefinitionResponse role = roleCatalogService.requireRole(request.roleCode());

        platformUserRepository.findByEmailIgnoreCase(request.email().trim())
            .ifPresent(existing -> {
                throw new IllegalArgumentException("email already exists");
            });

        PlatformUserEntity user = new PlatformUserEntity();
        user.setTenant(tenant);
        user.setEmail(request.email().trim().toLowerCase(Locale.ROOT));
        user.setDisplayName(request.displayName().trim());
        user.setRoleCode(role.code());
        user.setStatus(request.status() == null || request.status().isBlank() ? "active" : request.status());

        PlatformUserEntity saved = platformUserRepository.save(user);
        auditLogService.record(
            tenant.getId(),
            saved.getId(),
            saved.getDisplayName(),
            "USER_CREATED",
            "platform_user",
            saved.getId(),
            saved.getEmail(),
            "Created platform user with role " + saved.getRoleCode()
        );
        return toResponse(saved);
    }

    @Transactional(readOnly = true)
    public PlatformUserEntity requireUser(UUID userId) {
        return platformUserRepository.findById(userId)
            .orElseThrow(() -> new ResourceNotFoundException("platform user not found"));
    }

    private boolean matchesQuery(PlatformUserEntity user, String query) {
        String lowered = query.trim().toLowerCase(Locale.ROOT);
        return user.getDisplayName().toLowerCase(Locale.ROOT).contains(lowered)
            || user.getEmail().toLowerCase(Locale.ROOT).contains(lowered);
    }

    private PlatformUserResponse toResponse(PlatformUserEntity user) {
        return new PlatformUserResponse(
            user.getId(),
            user.getTenant().getId(),
            user.getTenant().getName(),
            user.getEmail(),
            user.getDisplayName(),
            user.getRoleCode(),
            roleCatalogService.roleName(user.getRoleCode()),
            user.getStatus(),
            user.getCreatedAt()
        );
    }
}
