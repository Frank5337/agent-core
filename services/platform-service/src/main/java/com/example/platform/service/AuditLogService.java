package com.example.platform.service;

import com.example.platform.entity.AuditLogEntity;
import com.example.platform.model.AuditLogResponse;
import com.example.platform.repository.AuditLogRepository;
import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuditLogService {

    private final AuditLogRepository auditLogRepository;

    public AuditLogService(AuditLogRepository auditLogRepository) {
        this.auditLogRepository = auditLogRepository;
    }

    @Transactional
    public void record(
        UUID tenantId,
        UUID actorUserId,
        String actorDisplayName,
        String action,
        String resourceType,
        UUID resourceId,
        String resourceName,
        String detail
    ) {
        AuditLogEntity entity = new AuditLogEntity();
        entity.setTenantId(tenantId);
        entity.setActorUserId(actorUserId);
        entity.setActorDisplayName(actorDisplayName == null ? "" : actorDisplayName);
        entity.setAction(action);
        entity.setResourceType(resourceType);
        entity.setResourceId(resourceId == null ? "" : resourceId.toString());
        entity.setResourceName(resourceName == null ? "" : resourceName);
        entity.setDetail(detail == null ? "" : detail);
        auditLogRepository.save(entity);
    }

    @Transactional(readOnly = true)
    public List<AuditLogResponse> listLogs(UUID tenantId, UUID actorUserId, String resourceType, String action) {
        return auditLogRepository.findAllByOrderByCreatedAtDesc().stream()
            .filter(item -> tenantId == null || tenantId.equals(item.getTenantId()))
            .filter(item -> actorUserId == null || actorUserId.equals(item.getActorUserId()))
            .filter(item -> resourceType == null || resourceType.isBlank() || resourceType.equalsIgnoreCase(item.getResourceType()))
            .filter(item -> action == null || action.isBlank() || action.equalsIgnoreCase(item.getAction()))
            .map(this::toResponse)
            .toList();
    }

    private AuditLogResponse toResponse(AuditLogEntity entity) {
        return new AuditLogResponse(
            entity.getId(),
            entity.getTenantId(),
            entity.getActorUserId(),
            entity.getActorDisplayName(),
            entity.getAction(),
            entity.getResourceType(),
            entity.getResourceId(),
            entity.getResourceName(),
            entity.getDetail(),
            entity.getCreatedAt()
        );
    }
}
