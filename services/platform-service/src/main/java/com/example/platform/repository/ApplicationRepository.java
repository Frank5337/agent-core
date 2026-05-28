package com.example.platform.repository;

import com.example.platform.entity.ApplicationEntity;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

// 这里的派生查询方法直接对应应用列表页的筛选维度。
public interface ApplicationRepository extends JpaRepository<ApplicationEntity, UUID> {

    List<ApplicationEntity> findAllByOrderByCreatedAtDesc();

    List<ApplicationEntity> findByTenant_IdOrderByCreatedAtDesc(UUID tenantId);

    List<ApplicationEntity> findByNameContainingIgnoreCaseOrderByCreatedAtDesc(String name);

    List<ApplicationEntity> findByTenant_IdAndNameContainingIgnoreCaseOrderByCreatedAtDesc(UUID tenantId, String name);
}
