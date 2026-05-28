package com.example.platform.model;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record ChatMessageRequest(
    @NotBlank @Pattern(regexp = "system|user|assistant") String role,
    @NotBlank @Size(max = 8000) String content
) {
}
