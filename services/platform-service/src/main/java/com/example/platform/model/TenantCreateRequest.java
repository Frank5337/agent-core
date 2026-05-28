package com.example.platform.model;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record TenantCreateRequest(
    @NotBlank @Size(min = 2, max = 100) String name,
    @Size(max = 255) String description
) {
}
