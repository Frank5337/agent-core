package com.example.platform.model;

import java.util.UUID;

public record ApplicationPublishRequest(
    UUID actorUserId,
    String note
) {
}
