package com.vicatech.timeoff.web;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;

import org.bson.Document;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Phase 0 only. Reports what is running and whether MongoDB can actually be reached, so a deploy
 * can be verified against the system rather than against an exit code.
 *
 * <p>This class is scaffolding. It carries no business requirement from the BRD and is expected to
 * be replaced once Phase 3 defines the real API.
 */
@RestController
@RequestMapping("/api")
public class PlatformController {

    private final MongoTemplate mongo;
    private final String version;

    public PlatformController(MongoTemplate mongo,
                              @Value("${timeoff.version:unknown}") String version) {
        this.mongo = mongo;
        this.version = version;
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("application", "TimeOff");
        body.put("phase", "0 — delivery path");
        body.put("version", version);
        body.put("time", Instant.now().toString());
        body.put("mongo", mongoStatus());
        return body;
    }

    /**
     * A ping rather than a client-object null check: holding a MongoClient proves nothing about
     * whether the database answers, because the driver connects lazily.
     */
    private String mongoStatus() {
        try {
            Document result = mongo.getDb().runCommand(new Document("ping", 1));
            return result.get("ok", Double.valueOf(0)).intValue() == 1 ? "reachable" : "unexpected response";
        } catch (RuntimeException ex) {
            return "unreachable: " + ex.getClass().getSimpleName();
        }
    }
}
