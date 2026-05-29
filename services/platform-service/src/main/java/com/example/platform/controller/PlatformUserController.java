package com.example.platform.controller;

import com.example.platform.model.PlatformUserCreateRequest;
import com.example.platform.model.PlatformUserResponse;
import com.example.platform.service.PlatformUserService;
import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/users")
public class PlatformUserController {

    private final PlatformUserService platformUserService;

    public PlatformUserController(PlatformUserService platformUserService) {
        this.platformUserService = platformUserService;
    }

    @GetMapping
    public List<PlatformUserResponse> listUsers(
        @RequestParam(name = "tenantId", required = false) UUID tenantId,
        @RequestParam(name = "q", required = false) String query,
        @RequestParam(name = "roleCode", required = false) String roleCode,
        @RequestParam(name = "status", required = false) String status
    ) {
        return platformUserService.listUsers(tenantId, query, roleCode, status);
    }

    @GetMapping("/{userId}")
    public PlatformUserResponse getUser(@PathVariable UUID userId) {
        return platformUserService.getUser(userId);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public PlatformUserResponse createUser(@Valid @RequestBody PlatformUserCreateRequest request) {
        return platformUserService.createUser(request);
    }
}
