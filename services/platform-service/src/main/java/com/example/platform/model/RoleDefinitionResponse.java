package com.example.platform.model;

import java.util.List;

public record RoleDefinitionResponse(
    String code,
    String name,
    String description,
    List<String> permissions
) {
}
