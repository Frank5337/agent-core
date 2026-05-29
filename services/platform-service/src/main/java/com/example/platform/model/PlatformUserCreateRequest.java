package com.example.platform.model;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.util.UUID;

public record PlatformUserCreateRequest(
    @NotNull UUID tenantId,
    @NotBlank @Email @Size(max = 120) String email,
    @NotBlank @Size(min = 2, max = 100) String displayName,
    @NotBlank @Pattern(regexp = "^[A-Z_]+$") String roleCode,
    @Pattern(regexp = "^(active|disabled)$") String status
) {
}
