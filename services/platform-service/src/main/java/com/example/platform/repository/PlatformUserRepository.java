package com.example.platform.repository;

import com.example.platform.entity.PlatformUserEntity;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PlatformUserRepository extends JpaRepository<PlatformUserEntity, UUID> {

    List<PlatformUserEntity> findAllByOrderByCreatedAtDesc();

    List<PlatformUserEntity> findByTenant_IdOrderByCreatedAtDesc(UUID tenantId);

    List<PlatformUserEntity> findByDisplayNameContainingIgnoreCaseOrEmailContainingIgnoreCaseOrderByCreatedAtDesc(
        String displayName,
        String email
    );

    List<PlatformUserEntity> findByTenant_IdAndDisplayNameContainingIgnoreCaseOrderByCreatedAtDesc(
        UUID tenantId,
        String displayName
    );

    List<PlatformUserEntity> findByTenant_IdAndEmailContainingIgnoreCaseOrderByCreatedAtDesc(UUID tenantId, String email);

    Optional<PlatformUserEntity> findByEmailIgnoreCase(String email);
}
