package com.example.platform.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
@EnableConfigurationProperties(AiServiceProperties.class)
public class RestClientConfig {

    @Bean
    public RestClient aiRestClient(RestClient.Builder builder, AiServiceProperties properties) {
        return builder.baseUrl(properties.baseUrl()).build();
    }
}

