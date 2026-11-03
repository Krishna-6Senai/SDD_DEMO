# TimeOff — Delivery Phases

Demo plan for spec-driven delivery, end to end · 3 November 2026

> **Phase 0 is built before the demo. Phases 1 onward are generated live, in front of the customer,
> from [BRD.md](BRD.md).**
>
> The point of pre-building Phase 0 is that the delivery path is already proven, so the live portion
> of the demo is specification and code — not debugging a pipeline in front of a room.

---

## Target

| | |
|---|---|
| Stack | React · Java (Spring Boot) · MongoDB |
| Server | `109.199.118.175` — Ubuntu 24.04, 4 vCPU, 7.8 GB RAM, 57 GB free |
| App URL | `http://109.199.118.175:8700` |
| CI/CD | GitHub Actions → build → push image → SSH deploy |
| Repo | to be created (Phase 0b) |

### The server is shared, and that constrains everything

Recon found **seven containers already running other people's work** — `moovtelecom_ftth_api` and
its frontend, two `anuraga-*` dev containers, a `mongo:8.2` instance, a private registry, and a
Flask image handler. nginx is Certbot-managed and serves `registry.pocapi.in` and
`sailber-dev.pocapi.in`. Ports 22, 80, 443, 3000, 4000, 5000, 8083, 8602, 8655 and 27018 are taken.

Three rules follow, and Phase 0 obeys all three:

1. **Additive only.** Every resource is prefixed `timeoff-`. Nothing existing is modified, stopped
   or reconfigured.
2. **No nginx change.** The app is served on port 8700 directly. Touching a Certbot-managed
   `sites-enabled/default` that fronts two live subdomains is not worth the risk for a demo. A
   `timeoff-dev.pocapi.in` subdomain can be added later if wanted — it needs a DNS record and a
   certificate, which are your calls.
3. **Our own MongoDB.** The existing `apimongodb` container is left alone. Reusing it would couple
   the demo to a container somebody else may restart, and it binds a host path we have no claim on.

---

## Phase 0 — Foundation and delivery path ✅ *(pre-built)*

The only phase not generated live. Split because half of it needs your GitHub account.

### 0a — Server runtime slot

| | Task |
|---|---|
| 0a.1 | Dedicated `timeoff` service user, in the `docker` group |
| 0a.2 | Dedicated ed25519 deploy key — **not** the root password |
| 0a.3 | `timeoff-net` Docker network |
| 0a.4 | `timeoff-mongo` on that network, named volume, **no published port** |
| 0a.5 | `/opt/timeoff/` with an idempotent `deploy.sh` |
| 0a.6 | Placeholder app on 8700, proving the slot is publicly reachable |
| 0a.7 | Verification that all seven pre-existing containers are untouched |

### 0b — Repository and pipeline

| | Task |
|---|---|
| 0b.1 | GitHub repository |
| 0b.2 | `.github/workflows/deploy.yml` — build React and Java, publish an image, deploy over SSH |
| 0b.3 | Repository secrets: `SSH_HOST`, `SSH_USER`, `SSH_KEY` |
| 0b.4 | A placeholder commit proving push → Actions → server works |

**Why a key and not the root password:** SSH password authentication in CI secrets is a long-lived
reusable credential with no rotation path. Demonstrating spec-driven delivery with a pipeline that
breaks its own published rule would be a poor look. The deploy user holds a key scoped to this one
job.

> Honest note: membership of the `docker` group is effectively root on the host. The `timeoff` user
> is better practice than a root key and better than a password, but it is not a security boundary.
> On a shared box, say so rather than imply isolation.

---

## Phase 1 — Specifications 🔴 *live*

**This is the demo.** Input: `BRD.md`. Output: the governing documents, derived in front of the
customer.

| | Document | Derived from |
|---|---|---|
| 1.1 | `PRD.md` | §1–§4 objectives and scope, §5 roles, §9 functional requirements |
| 1.2 | `Architecture.md` | the stack decision, §11 data requirements, §12 non-functional |
| 1.3 | `Rulebook.md` | §10 business rules, §12 NFR-11 server-side authorisation |
| 1.4 | `Design.md` | §8 — brand colour, header, navigation, footer, state without colour alone |
| 1.5 | `ApiContract.md` | §7 screens and §9 requirements, resolved into endpoints |
| 1.6 | `Tasks.md` | everything above, phased |

**The moment worth pausing on:** the BRD carries **six open questions** (OQ-1 to OQ-6) that the
business has not answered. A specification that quietly invents answers to them is the failure mode
this whole approach exists to prevent. Expect them to appear in `PRD.md` as open decisions with
owners — particularly OQ-1, whether a submitted request reserves balance, because two employees can
each submit a request that individually fits and together does not.

## Phase 2 — Domain and data 🔴 *live*

| | Task | Source |
|---|---|---|
| 2.1 | MongoDB collections and indexes | §11 |
| 2.2 | Java domain model and request state machine | §6 |
| 2.3 | Working-day calculator — weekends and public holidays excluded | BRL-02 |
| 2.4 | Balance calculation | BR-11, BRL-01, BRL-12 |
| 2.5 | Validation: overlap, date order, half-day placement, notice period | BRL-03, 04, 05, 07 |
| 2.6 | Separation of duties — a manager cannot decide their own request | BRL-06 |
| 2.7 | Audit record on every state change | BR-17, NFR-09 |

## Phase 3 — API 🔴 *live*

| | Task | Source |
|---|---|---|
| 3.1 | Sign-in, password hashing that cannot be reversed | BR-18, NFR-10 |
| 3.2 | Endpoints per the Phase 1 contract | §9 |
| 3.3 | Role enforcement **server-side on the query** | NFR-11 |
| 3.4 | Consistent response envelope and field-level validation errors | §7 SCR-02 |
| 3.5 | Seed data: three leave types, holiday calendar, demo employees | §11, ASM-3 |

## Phase 4 — Screens 🔴 *live*

| | Task | Source |
|---|---|---|
| 4.1 | Application shell — header, navigation with active state, footer | §8 |
| 4.2 | Design tokens derived from `#0F7B6C` | §8 |
| 4.3 | SCR-01 My Leave — balance per type, request list, filters, cancel | §7 |
| 4.4 | SCR-02 Request Leave — **live working-day count before submission** | BR-03 |
| 4.5 | SCR-03 Approvals — queue, approve, reject with reason, notice-breach flag | §7 |
| 4.6 | Role-gated navigation, with the screen refusing independently | §7 |
| 4.7 | Responsive to 400px, WCAG AA, dates as `03 Nov 2026` | NFR-01 to NFR-05 |

## Phase 5 — Acceptance 🔴 *live*

The eleven criteria in BRD §17, as executable tests. Criteria 7 and 8 are the negatives and matter
most: a manager's own request absent from their own queue, and an employee refused the Approvals
screen rather than redirected away from it.

## Phase 6 — Reports ⬜ *stretch*

RPT-01 to RPT-03 with spreadsheet export. Out of the demo path unless time allows.

---

## Demo running order

| | Step | Who |
|---|---|---|
| 1 | Show `BRD.md` — a business document, no technology in it | You |
| 2 | "Write the specifications" → Phase 1 | Live |
| 3 | Walk the open decisions the spec surfaced | You |
| 4 | "Now the tasks" → `Tasks.md` | Live |
| 5 | "Now build it" → Phases 2–4 | Live |
| 6 | `git push` | You |
| 7 | GitHub Actions builds and deploys | Automatic |
| 8 | Open `http://109.199.118.175:8700` | You |

Step 7 is why Phase 0 exists. It is the one step that cannot be improvised.
