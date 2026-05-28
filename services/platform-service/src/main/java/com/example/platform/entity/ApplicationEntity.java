package com.example.platform.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "applications")
public class ApplicationEntity {

    @Id
    private UUID id;

    // 应用归属到租户，后续权限和审计都会围绕这个关系展开。
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "tenant_id", nullable = false)
    private TenantEntity tenant;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(nullable = false, length = 500)
    private String description = "";

    @Column(nullable = false, length = 50)
    private String appType;

    @Column(length = 4000)
    private String systemPrompt = "";

    @Column
    private UUID defaultProviderId;

    @Column
    private UUID defaultKnowledgeBaseId;

    @Column(nullable = false)
    private Instant createdAt;

    @PrePersist
    void onCreate() {
        // 保持实体自身可落库，减少服务层样板代码。
        if (id == null) {
            id = UUID.randomUUID();
        }
        if (createdAt == null) {
            createdAt = Instant.now();
        }
        if (description == null) {
            description = "";
        }
        if (systemPrompt == null) {
            systemPrompt = "";
        }
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public TenantEntity getTenant() {
        return tenant;
    }

    public void setTenant(TenantEntity tenant) {
        this.tenant = tenant;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getAppType() {
        return appType;
    }

    public void setAppType(String appType) {
        this.appType = appType;
    }

    public String getSystemPrompt() {
        return systemPrompt;
    }

    public void setSystemPrompt(String systemPrompt) {
        this.systemPrompt = systemPrompt;
    }

    public UUID getDefaultProviderId() {
        return defaultProviderId;
    }

    public void setDefaultProviderId(UUID defaultProviderId) {
        this.defaultProviderId = defaultProviderId;
    }

    public UUID getDefaultKnowledgeBaseId() {
        return defaultKnowledgeBaseId;
    }

    public void setDefaultKnowledgeBaseId(UUID defaultKnowledgeBaseId) {
        this.defaultKnowledgeBaseId = defaultKnowledgeBaseId;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }
}
