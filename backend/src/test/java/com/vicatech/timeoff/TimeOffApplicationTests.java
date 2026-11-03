package com.vicatech.timeoff;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import com.vicatech.timeoff.web.PlatformController;

/**
 * Phase 0 gate. Proves the application context builds and that the Mongo auto-configuration does
 * not require a reachable database at startup — which is what lets CI run this without a Mongo
 * container, and lets the app start on the server before the database is up.
 */
@SpringBootTest
class TimeOffApplicationTests {

    @Autowired
    private PlatformController platformController;

    @Test
    void contextLoadsWithoutAReachableDatabase() {
        assertThat(platformController).isNotNull();
    }

    @Test
    void healthReportsTheApplicationAndSaysSomethingAboutMongo() {
        var body = platformController.health();

        assertThat(body.get("application")).isEqualTo("TimeOff");
        // Either answer is acceptable here; what matters is that the call returns rather than
        // throwing when the database is absent.
        assertThat(body.get("mongo")).asString().isNotEmpty();
    }
}
