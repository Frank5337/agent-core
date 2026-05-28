package com.example.platform.config;

import com.example.platform.entity.TenantEntity;
import com.example.platform.repository.TenantRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DataInitializer {

    @Bean
    CommandLineRunner seedDefaultTenant(TenantRepository tenantRepository) {
        return args -> {
            if (tenantRepository.count() == 0) {
                TenantEntity tenant = new TenantEntity();
                tenant.setName("default-tenant");
                tenant.setDescription("Default tenant for local development");
                tenantRepository.save(tenant);
            }
        };
    }
}

