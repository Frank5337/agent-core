package com.example.platform.service;

import com.example.platform.model.RoleDefinitionResponse;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class RoleCatalogService {

    private static final Map<String, RoleDefinitionResponse> ROLE_DEFINITIONS = Map.of(
        "PLATFORM_ADMIN",
        new RoleDefinitionResponse(
            "PLATFORM_ADMIN",
            "Platform Admin",
            "Owns tenant, user, application, and audit management for the whole platform.",
            List.of("tenant:read", "tenant:write", "user:read", "user:write", "application:read", "application:write", "audit:read")
        ),
        "TENANT_ADMIN",
        new RoleDefinitionResponse(
            "TENANT_ADMIN",
            "Tenant Admin",
            "Manages users and applications inside one tenant.",
            List.of("tenant:read", "user:read", "user:write", "application:read", "application:write")
        ),
        "APP_OPERATOR",
        new RoleDefinitionResponse(
            "APP_OPERATOR",
            "App Operator",
            "Maintains prompts, provider bindings, and release status for applications.",
            List.of("application:read", "application:write", "application:publish")
        ),
        "AUDITOR",
        new RoleDefinitionResponse(
            "AUDITOR",
            "Auditor",
            "Reads operation history and release activity without changing platform data.",
            List.of("tenant:read", "application:read", "audit:read")
        )
    );

    public List<RoleDefinitionResponse> listRoles() {
        return ROLE_DEFINITIONS.values().stream().toList();
    }

    public RoleDefinitionResponse requireRole(String roleCode) {
        RoleDefinitionResponse role = ROLE_DEFINITIONS.get(roleCode);
        if (role == null) {
            throw new IllegalArgumentException("unsupported roleCode: " + roleCode);
        }
        return role;
    }

    public String roleName(String roleCode) {
        RoleDefinitionResponse role = ROLE_DEFINITIONS.get(roleCode);
        return role == null ? roleCode : role.name();
    }
}
