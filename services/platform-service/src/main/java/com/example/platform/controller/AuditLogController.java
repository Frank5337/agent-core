package com.example.platform.controller;

import com.example.platform.model.AuditLogResponse;
import com.example.platform.service.AuditLogService;
import java.util.List;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/audit-logs")
public class AuditLogController {

    private final AuditLogService auditLogService;

    public AuditLogController(AuditLogService auditLogService) {
        this.auditLogService = auditLogService;
    }

    @GetMapping
    public List<AuditLogResponse> listLogs(
        @RequestParam(name = "tenantId", required = false) UUID tenantId,
        @RequestParam(name = "actorUserId", required = false) UUID actorUserId,
        @RequestParam(name = "resourceType", required = false) String resourceType,
        @RequestParam(name = "action", required = false) String action
    ) {
        return auditLogService.listLogs(tenantId, actorUserId, resourceType, action);
    }
}
