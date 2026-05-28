package com.example.platform.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "ai.service")
public record AiServiceProperties(String baseUrl) {
}

