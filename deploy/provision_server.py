"""
Phase 0a — provision the TimeOff runtime slot on a SHARED server.

Strictly additive. Every resource is prefixed `timeoff-`. Nothing pre-existing is modified,
stopped or reconfigured, and nginx is not touched at all.

Pre-flight records the existing container list and root's authorized_keys line count; the
verification pass at the end asserts both are unchanged (Rulebook R-1: verify, do not assume).
"""
import os
import sys
import time

import paramiko

HOST = "109.199.118.175"
USER = "root"
PWD = os.environ.get("DEMO_SSH_PWD")
HERE = os.path.dirname(os.path.abspath(__file__))

if not PWD:
    sys.exit("DEMO_SSH_PWD not set")

with open(os.path.join(HERE, "timeoff_deploy.pub"), encoding="utf-8") as fh:
    DEPLOY_PUBKEY = fh.read().strip()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PWD, timeout=25)


def run(cmd, timeout=180, quiet=False):
    _, out, err = client.exec_command(cmd, timeout=timeout)
    rc = out.channel.recv_exit_status()
    body = (out.read().decode(errors="replace") + err.read().decode(errors="replace")).strip()
    if not quiet:
        print(body if body else "(no output)")
    return rc, body


def step(label):
    print(f"\n{'=' * 70}\n{label}\n{'=' * 70}")


# ---------------------------------------------------------------- pre-flight
step("PRE-FLIGHT — recording the state we must not disturb")

_, before_containers = run("docker ps -a --format '{{.Names}}|{{.Status}}' | sort", quiet=True)
before_names = sorted(l.split("|")[0] for l in before_containers.splitlines() if l.strip())
print(f"existing containers ({len(before_names)}):")
for n in before_names:
    print(f"  - {n}")

_, before_keys = run("wc -l < /root/.ssh/authorized_keys", quiet=True)
print(f"\nroot authorized_keys lines: {before_keys}")

rc, port_check = run("ss -tln | grep -q ':8700 ' && echo TAKEN || echo FREE", quiet=True)
print(f"port 8700: {port_check}")
if "TAKEN" in port_check:
    sys.exit("ABORT: port 8700 is in use. Nothing was changed.")

# ---------------------------------------------------------------- 0a.1 / 0a.2
step("0a.1 — service user `timeoff`")
run("id timeoff >/dev/null 2>&1 || useradd -m -s /bin/bash timeoff; id timeoff")

step("0a.2 — docker group + dedicated deploy key")
run("usermod -aG docker timeoff && echo 'added to docker group'")
run("install -d -m 700 -o timeoff -g timeoff /home/timeoff/.ssh && echo '.ssh ready'")
# Idempotent append: only add the key if it is not already present.
run(
    "touch /home/timeoff/.ssh/authorized_keys && "
    f"grep -qF '{DEPLOY_PUBKEY}' /home/timeoff/.ssh/authorized_keys "
    f"|| echo '{DEPLOY_PUBKEY}' >> /home/timeoff/.ssh/authorized_keys; "
    "chown timeoff:timeoff /home/timeoff/.ssh/authorized_keys && "
    "chmod 600 /home/timeoff/.ssh/authorized_keys && "
    "wc -l < /home/timeoff/.ssh/authorized_keys"
)

# ---------------------------------------------------------------- 0a.3 / 0a.5
step("0a.3 — dedicated docker network")
run("docker network inspect timeoff-net >/dev/null 2>&1 || docker network create timeoff-net; "
    "docker network ls --format '{{.Name}}' | grep timeoff")

step("0a.5 — /opt/timeoff")
run("install -d -m 755 -o timeoff -g timeoff /opt/timeoff /opt/timeoff/placeholder && ls -ld /opt/timeoff")

# ---------------------------------------------------------------- upload files
step("uploading deploy.sh and the placeholder page")
sftp = client.open_sftp()
for local, remote, mode in [
    ("deploy.sh", "/opt/timeoff/deploy.sh", 0o755),
    ("placeholder.html", "/opt/timeoff/placeholder/index.html", 0o644),
]:
    sftp.put(os.path.join(HERE, local), remote)
    sftp.chmod(remote, mode)
    print(f"  uploaded {remote}")
sftp.close()
run("chown -R timeoff:timeoff /opt/timeoff && ls -l /opt/timeoff /opt/timeoff/placeholder")

# ---------------------------------------------------------------- 0a.4 mongo
step("0a.4 — timeoff-mongo (no published port; reachable only on timeoff-net)")
run("docker volume inspect timeoff-mongo-data >/dev/null 2>&1 || docker volume create timeoff-mongo-data")
rc, _ = run("docker inspect timeoff-mongo >/dev/null 2>&1 && echo exists || echo absent", quiet=True)
run(
    "docker inspect timeoff-mongo >/dev/null 2>&1 || "
    "docker run -d --name timeoff-mongo --network timeoff-net --restart unless-stopped "
    "-v timeoff-mongo-data:/data/db mongo:8.2",
    timeout=300,
)
print("waiting for mongo to accept connections...")
for attempt in range(20):
    rc, body = run(
        "docker exec timeoff-mongo mongosh --quiet --eval 'db.runCommand({ping:1}).ok' 2>/dev/null",
        quiet=True,
    )
    if body.strip().endswith("1"):
        print(f"  mongo ping ok (attempt {attempt + 1})")
        break
    time.sleep(3)
else:
    print("  WARNING: mongo did not answer a ping in 60s")

# ---------------------------------------------------------------- 0a.6
step("0a.6 — placeholder app on 8700")
run(
    "docker rm -f timeoff-app >/dev/null 2>&1; "
    "docker run -d --name timeoff-app --network timeoff-net --restart unless-stopped "
    "-p 8700:80 -v /opt/timeoff/placeholder:/usr/share/nginx/html:ro nginx:alpine",
    timeout=300,
)
time.sleep(3)
run("curl -s -o /dev/null -w 'localhost:8700 -> %{http_code}\\n' http://localhost:8700")

# ---------------------------------------------------------------- verify
step("0a.7 — VERIFICATION")

_, after_containers = run("docker ps -a --format '{{.Names}}|{{.Status}}' | sort", quiet=True)
after = {l.split("|")[0]: l.split("|")[1] for l in after_containers.splitlines() if "|" in l}

print("pre-existing containers — must all still be Up:")
ok = True
for n in before_names:
    status = after.get(n, "MISSING")
    flag = "ok" if status.startswith("Up") else "PROBLEM"
    if flag == "PROBLEM":
        ok = False
    print(f"  [{flag:7}] {n}: {status}")

print("\nnew containers:")
for n in ("timeoff-mongo", "timeoff-app"):
    print(f"  {n}: {after.get(n, 'MISSING')}")

_, after_keys = run("wc -l < /root/.ssh/authorized_keys", quiet=True)
same = after_keys.strip() == before_keys.strip()
print(f"\nroot authorized_keys: {before_keys.strip()} -> {after_keys.strip()} "
      f"({'unchanged' if same else 'CHANGED — INVESTIGATE'})")
if not same:
    ok = False

_, nginx_state = run("systemctl is-active nginx", quiet=True)
print(f"host nginx: {nginx_state.strip()} (not reconfigured by this script)")

_, key_test = run(
    "sudo -u timeoff docker ps --format '{{.Names}}' | wc -l", quiet=True
)
print(f"timeoff user can run docker: sees {key_test.strip()} containers")

print(f"\n{'=' * 70}")
print("PHASE 0a: " + ("COMPLETE — nothing pre-existing was disturbed" if ok
                      else "COMPLETED WITH PROBLEMS — see flags above"))
print("=" * 70)

client.close()
