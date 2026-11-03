# TimeOff — React + Spring Boot, built in CI and shipped as one image.
#
# Three stages so the runtime image carries a JRE and a jar, not a JDK, Maven and node_modules.
# The build happens here and in GitHub Actions — never on the server (spec/CICD.md P-1).

# ---------------------------------------------------------------- frontend
FROM node:22.11-alpine AS frontend
WORKDIR /app

# Dependencies first, so a source-only change reuses this layer.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ---------------------------------------------------------------- backend
FROM maven:3.9.9-eclipse-temurin-21 AS backend
WORKDIR /build

# Resolve dependencies against the POM alone, so they cache independently of the source.
COPY backend/pom.xml ./
RUN mvn -B -q dependency:go-offline

COPY backend/src ./src

# Spring Boot serves the built React bundle from the classpath.
COPY --from=frontend /app/dist ./src/main/resources/static

RUN mvn -B -q clean package -DskipTests

# ---------------------------------------------------------------- runtime
FROM eclipse-temurin:21.0.5_11-jre-alpine AS runtime

# A non-root user, because the restricted Pod Security Standard refuses root containers and
# because there is no reason for this process to be root (spec/Infrastructure.md 6.4).
RUN addgroup -S timeoff && adduser -S -G timeoff -u 10001 timeoff

WORKDIR /app
COPY --from=backend /build/target/*.jar app.jar
RUN chown -R timeoff:timeoff /app

USER timeoff
EXPOSE 8080

# Container memory limits are what the JVM sizes itself against; leave headroom so a limit does
# not produce an OOM kill that reads like an application fault.
ENV JAVA_OPTS="-XX:MaxRAMPercentage=70"

ENTRYPOINT ["sh", "-c", "exec java $JAVA_OPTS -jar /app/app.jar"]
