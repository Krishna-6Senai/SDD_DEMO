#!/usr/bin/env bash
#
# TimeOff deploy — run on the server by GitHub Actions over SSH.
#
#   ./deploy.sh <image-ref>
#
# The image is built and published by CI; this script never builds. A deploy's exit code is not
# evidence the new code is running, so the script asserts the container is actually serving and
# rolls nothing back silently.
#
# This server is SHARED. Only resources named `timeoff-*` are touched.

set -euo pipefail

IMAGE="${1:?usage: deploy.sh <image-ref>}"
APP_NAME="timeoff-app"
NETWORK="timeoff-net"
PORT="8700"
MONGO_URI="mongodb://timeoff-mongo:27017/timeoff"

echo "==> deploying ${IMAGE}"

# Record what is currently serving, so a failed deploy can be reported against it.
PREVIOUS="$(docker inspect --format '{{.Config.Image}}' "${APP_NAME}" 2>/dev/null || echo 'none')"
echo "    currently running: ${PREVIOUS}"

echo "==> pulling"
docker pull "${IMAGE}"

echo "==> replacing ${APP_NAME}"
docker rm -f "${APP_NAME}" >/dev/null 2>&1 || true

docker run -d \
  --name "${APP_NAME}" \
  --network "${NETWORK}" \
  --restart unless-stopped \
  -p "${PORT}:8080" \
  -e "SPRING_DATA_MONGODB_URI=${MONGO_URI}" \
  -e "TZ=Europe/London" \
  "${IMAGE}"

echo "==> waiting for the app to answer"
for attempt in $(seq 1 30); do
  code="$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:${PORT}/" || true)"
  if [ "${code}" = "200" ]; then
    echo "    answered 200 after ${attempt} attempt(s)"
    RUNNING="$(docker inspect --format '{{.Config.Image}}' "${APP_NAME}")"
    echo "==> deployed: ${RUNNING}"
    exit 0
  fi
  sleep 2
done

echo "!! the app did not answer 200 within 60s"
echo "--- last 40 log lines ---"
docker logs --tail 40 "${APP_NAME}" 2>&1 || true
echo "--- previous image was: ${PREVIOUS} ---"
exit 1
