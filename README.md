# TimeOff

Employee leave management. Built to demonstrate **spec-driven delivery**: a business requirements
document in, specifications and working software out.

| | |
|---|---|
| Requirements | [BRD.md](BRD.md) — the only input |
| Plan | [PHASES.md](PHASES.md) |
| Stack | React · Spring Boot (Java 21) · MongoDB |
| Dev server | `http://109.199.118.175:8700` |

---

## What is here, and what is not

**Phase 0 only.** This repository currently contains the requirements, the plan, and the delivery
path — a minimal React page and a Spring Boot application that report their own health. There is no
leave management code, and that is deliberate: Phases 1 to 5 are generated from `BRD.md` during the
demo.

The frontend skeleton is **not** the TimeOff interface. The application shell — header, navigation,
footer, design tokens — is Phase 4, derived from BRD §8, and replaces `frontend/src/App.tsx`.

## Layout

```
BRD.md                     business requirements — the input
PHASES.md                  delivery phases, and which are live in the demo
Dockerfile                 three stages: React build, Maven build, JRE runtime
deploy/deploy.sh           run on the server by CI; never builds anything
.github/workflows/         build, publish, deploy, verify
backend/                   Spring Boot — Phase 0 health endpoint only
frontend/                  React + Vite — Phase 0 placeholder only
```

## The delivery path

```
push to main
   │
   ├─ validate   React build + typecheck, frontend tests, `mvn verify`
   ├─ build      one image, tagged by commit SHA, pushed to GHCR
   ├─ deploy     SSH to the server, pull by digest, restart the container
   └─ verify     running digest == built digest, and the app answers 200
```

Three properties, each carried over from the delivery rules this demo is built on:

- **Nothing is built on the server.** The image is built once in CI and deployed by reference.
- **The gates can fail.** No `continue-on-error`; a failing test stops the deploy.
- **A deploy is verified by the running system.** The final two steps compare the digest actually
  running against the one this run built, and check the app answers from outside. An exit code is
  not evidence.

## Local development

```bash
# MongoDB
docker run -d --name timeoff-mongo-local -p 27017:27017 mongo:8.2

# Backend, on :8080
cd backend && mvn spring-boot:run

# Frontend, on :5173, proxying /api to :8080
cd frontend && npm install && npm run dev
```

Requires **Java 21** and Node 22. Java 8 will not compile this.

## Server runtime

The dev server is **shared** — it runs seven unrelated containers, Certbot-managed nginx serving
other subdomains, and another team's MongoDB on port 27018. Everything here is therefore additive
and prefixed `timeoff-`:

| Resource | Note |
|---|---|
| `timeoff-app` | the application, published on port 8700 |
| `timeoff-mongo` | our own MongoDB, **no published port** — reachable only on the app network |
| `timeoff-net` | dedicated Docker network |
| `timeoff-mongo-data` | named volume |
| `timeoff` user | service account that runs the deploy, in the `docker` group |
| `/opt/timeoff/` | deploy script lives here |

**nginx is not modified.** The app is served on a port directly. Fronting it with
`timeoff-dev.pocapi.in` would need a DNS record and a certificate, and editing a Certbot-managed
config that serves two live subdomains is not worth the risk for a demo.

> Membership of the `docker` group is effectively root on the host. The service account is better
> practice than a root key and much better than a password, but it is not a security boundary.

## First-time setup

### 1. Create the repository

```bash
gh auth login
gh repo create vicatech/timeoff --private --source=. --remote=origin --push
```

### 2. Add repository secrets

| Secret | Value |
|---|---|
| `SSH_HOST` | `109.199.118.175` |
| `SSH_USER` | `timeoff` |
| `SSH_KEY` | the private key generated during Phase 0a, whole file including header and footer lines |

```bash
gh secret set SSH_HOST --body "109.199.118.175"
gh secret set SSH_USER --body "timeoff"
gh secret set SSH_KEY < /path/to/timeoff_deploy
```

The deploy uses a **dedicated key, not a password**. SSH password authentication in CI secrets is a
long-lived reusable credential with no rotation path, so demonstrating this delivery method with one
would break the very rule the method publishes.

### 3. Allow the server to pull the image

The workflow logs the server into GHCR with the job's own short-lived token, piped over stdin so it
never appears in the server's process list. Nothing persistent is stored on the server.

If the organisation blocks that, the alternative is to make the GHCR package public:
**Repository → Packages → timeoff → Package settings → Change visibility → Public.** The deploy
then pulls anonymously and the `docker login` step can be dropped.

### 4. Push and watch

```bash
git push origin main
gh run watch
curl -s http://109.199.118.175:8700/api/health
```

A successful first run is what makes the demo safe: the one step that cannot be improvised in front
of a customer is proven before anyone is watching.

## Requirement traceability

Every downstream document and task cites the identifiers in `BRD.md` — `BR-nn` functional,
`BRL-nn` business rules, `NFR-nn` non-functional, `SCR-nn` screens, `OQ-n` open questions. Those
identifiers are stable, so a test or a task can be traced back to the business need that caused it.

**The BRD leaves six questions open (OQ-1 to OQ-6).** A specification that invents answers to them
is the failure this approach exists to prevent. They should appear in the generated `PRD.md` as open
decisions with owners — not quietly resolved.
