package com.example.platform.controller;

import com.example.platform.model.RoleDefinitionResponse;
import com.example.platform.service.RoleCatalogService;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/roles")
public class RoleController {

    private final RoleCatalogService roleCatalogService;

    public RoleController(RoleCatalogService roleCatalogService) {
        this.roleCatalogService = roleCatalogService;
    }

    @GetMapping
    public List<RoleDefinitionResponse> listRoles() {
        return roleCatalogService.listRoles();
    }
}
