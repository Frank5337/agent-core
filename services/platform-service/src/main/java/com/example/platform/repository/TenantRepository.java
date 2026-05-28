package com.example.platform.repository;

import com.example.platform.entity.TenantEntity;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

// Repository 先只保留管理台实际会用到的查询组合。
public interface TenantRepository extends JpaRepository<TenantEntity, UUID> {

    List<TenantEntity> findAllByOrderByCreatedAtDesc();

    List<TenantEntity> findByNameContainingIgnoreCaseOrderByCreatedAtDesc(String name);
}
