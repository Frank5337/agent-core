package com.example.platform.config;

import com.example.platform.entity.PlatformUserEntity;
import com.example.platform.entity.TenantEntity;
import com.example.platform.repository.PlatformUserRepository;
import com.example.platform.repository.TenantRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DataInitializer {

    @Bean
    CommandLineRunner seedDefaultTenant(TenantRepository tenantRepository, PlatformUserRepository platformUserRepository) {
        return args -> {
            TenantEntity tenant;
            if (tenantRepository.count() == 0) {
                tenant = new TenantEntity();
                tenant.setName("default-tenant");
                tenant.setDescription("Default tenant for local development");
                tenant = tenantRepository.save(tenant);
            } else {
                tenant = tenantRepository.findAllByOrderByCreatedAtDesc().get(0);
            }

            if (platformUserRepository.count() == 0) {
                PlatformUserEntity user = new PlatformUserEntity();
                user.setTenant(tenant);
                user.setEmail("admin@example.com");
                user.setDisplayName("Platform Admin");
                user.setRoleCode("PLATFORM_ADMIN");
                user.setStatus("active");
                platformUserRepository.save(user);
            }
        };
    }
}
