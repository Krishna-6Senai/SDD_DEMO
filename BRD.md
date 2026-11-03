# Business Requirements Document

## TimeOff — Employee Leave Management

| | |
|---|---|
| **Document reference** | BRD-TO-001 |
| **Version** | 1.0 |
| **Status** | Approved for design |
| **Author** | Business Analysis, People Operations |
| **Date** | 3 November 2026 |
| **Business sponsor** | Head of People Operations |
| **Reviewed by** | HR Operations Manager · IT Delivery Manager |
| **Distribution** | Delivery team, HR Operations, IT Security |

---

## 1. Purpose

This document states what the business needs from a leave management application. It describes
business outcomes, rules and constraints. **It does not specify technology, data design or
implementation** — those are the delivery team's to propose, and this document is the input they
work from.

## 2. Background

Leave is currently requested by email to a line manager and recorded by HR in a shared spreadsheet.
Three problems follow from this:

1. **Employees cannot see their own balance.** Every balance question becomes an email to HR.
   HR Operations handles roughly 60 such enquiries a month.
2. **Approvals are not traceable.** An approval lives in a manager's mailbox. When a dispute arises
   there is no reliable record of who approved what, or when.
3. **The spreadsheet is a single point of failure.** It has been overwritten twice in the last year,
   and the recovered copy is reconciled by hand.

## 3. Business objectives

| # | Objective | How success is measured |
|---|---|---|
| OBJ-1 | Employees can see their entitlement and remaining balance without asking | Balance enquiries to HR reduced by 80% within two months of launch |
| OBJ-2 | Every leave decision is recorded with who, when and why | 100% of approved and rejected requests carry an attributable decision record |
| OBJ-3 | Managers can act on requests in one place | Median time from submission to decision under two working days |
| OBJ-4 | HR holds one authoritative record of leave | The spreadsheet is retired |

## 4. Scope

### In scope

- Employee self-service: view balance, request leave, cancel a request
- Manager approval of requests from their direct reports
- HR administration of leave types, entitlements and the public holiday calendar
- A record of every state change on a request
- Three screens, as defined in §7

### Out of scope for this release

Stated explicitly so the delivery team does not design for them:

- Payroll integration
- Sickness certification and occupational health
- Multi-level or delegated approval chains (see OQ-3)
- Single sign-on — email and password authentication is acceptable for this release
- Languages other than English
- A mobile application. The screens must work on a phone browser, which is not the same thing
- Accrual of entitlement month by month. Entitlement is granted in full at the start of the leave year

## 5. Stakeholders and roles

| Role | Who | What they can do |
|---|---|---|
| **Employee** | All staff | View own balance and history; create, submit and cancel own requests |
| **Manager** | Staff with direct reports | Everything an Employee can do, plus approve or reject requests from their direct reports |
| **HR Administrator** | People Operations team | View all requests across the organisation; maintain leave types, entitlements and the holiday calendar; adjust a balance with a recorded reason |

A Manager is also an Employee. Permission must be additive rather than exclusive.

## 6. Business process

### Proposed process

```
Employee                    Manager                     System
────────                    ───────                     ──────
creates request    ─────▶                               validates against balance,
                                                        overlap and notice rules
submits            ─────▶   appears in approval queue
                            approves or rejects  ─────▶  records decision, adjusts
                                                        balance, notifies employee
```

A request not yet submitted is a draft, visible only to its author and not counted against any
balance.

### Request states

| State | Meaning | Who sets it |
|---|---|---|
| `Draft` | Created, not submitted. Not counted against balance | Employee |
| `Submitted` | Awaiting a decision | Employee |
| `Approved` | Granted. Counted against balance | Manager, HR Administrator |
| `Rejected` | Refused, with a mandatory reason | Manager, HR Administrator |
| `Cancelled` | Withdrawn by the employee before the leave start date | Employee |

A request in `Approved` or `Rejected` is final and cannot be edited. Correcting a mistake means
cancelling and raising a new request — except after the start date, which is covered by OQ-4.

## 7. Screens required

Three screens. The delivery team decides how they are built; this section states what each must let
a user do.

### SCR-01 — My Leave *(landing screen)*

The screen an employee sees on signing in.

- Entitlement, taken and remaining days, **per leave type**, for the current leave year
- A list of the employee's own requests: dates, leave type, number of days, state, and who decided
- Filter by state and by leave year
- Cancel a request directly from the list, where the rules permit it
- A clear way to start a new request

### SCR-02 — Request Leave

- Leave type, start date, end date, optional reason
- Half-day support on the first and last day of a request
- **The number of working days must be shown and updated as the dates change, before submission.**
  An employee should not have to submit to learn the cost of a request
- Remaining balance shown alongside, so the effect of the request is visible
- Save as draft, or submit
- Validation messages appear against the field at fault and explain how to correct it

### SCR-03 — Approvals *(Manager and HR Administrator only)*

- Requests awaiting a decision, oldest first
- For each: employee name, leave type, dates, working days, the employee's remaining balance after
  approval, and any reason given
- Approve, or reject with a mandatory reason
- An indication where a request breaches the notice period (BRL-05) so the manager knows before deciding
- Requests already decided are reachable but not mixed in with those awaiting a decision

**Employees must not be able to reach SCR-03 at all.** Hiding the menu entry is not sufficient; the
screen itself must refuse.

## 8. Website design requirements

The application must look like a single, deliberately designed product rather than a set of forms.

### Layout

| Element | Requirement |
|---|---|
| **Header** | Present on every screen. Product name, primary navigation, and the signed-in user's name with a menu containing *My profile* and *Sign out* |
| **Navigation** | My Leave · Request Leave · Approvals · Administration. Entries the user's role does not permit are not shown, and the screens behind them refuse access independently |
| **Active state** | The navigation must show which screen the user is on |
| **Footer** | Present on every screen. Copyright, application version, a support contact, and a link to the leave policy |
| **Page heading** | Every screen states its name, so a bookmarked or shared page explains itself |

### Visual requirements

- **Brand colour** is Vicatech teal `#0F7B6C`, used for primary actions, active navigation and
  brand marks. The delivery team derives the full palette from it
- **Request states must be distinguishable without relying on colour alone** — a colour and a word
  together. Some staff have colour-vision deficiency, and HR prints these lists
- A deliberate type hierarchy. Headings, body text and tabular figures should not all be the same
  size and weight
- Dates are shown as `03 Nov 2026`, never numerically, to remove day/month ambiguity
- Day counts and balances are shown to one decimal place, because half days exist

### Responsiveness and accessibility

| # | Requirement |
|---|---|
| NFR-01 | Usable in a phone browser at 400px width with no horizontal scrolling |
| NFR-02 | Text contrast meets WCAG 2.1 AA |
| NFR-03 | Every action reachable by keyboard, with a visible focus indicator |
| NFR-04 | Form fields have associated labels; errors are announced, not only coloured |
| NFR-05 | Supported browsers: current Chrome, Edge, Safari and Firefox |

## 9. Functional requirements

| # | Requirement | Priority |
|---|---|---|
| BR-01 | An employee can view their entitlement, days taken and remaining balance per leave type for the current leave year | Must |
| BR-02 | An employee can create a leave request specifying type, start date, end date and an optional reason | Must |
| BR-03 | The system calculates and displays the working days a request consumes, before submission | Must |
| BR-04 | An employee can save a request as a draft and submit it later | Should |
| BR-05 | An employee can submit a request for a decision | Must |
| BR-06 | An employee can cancel their own request before its start date | Must |
| BR-07 | An employee can view the history and current state of all their own requests | Must |
| BR-08 | A manager can see all requests from their direct reports awaiting a decision | Must |
| BR-09 | A manager can approve a request | Must |
| BR-10 | A manager can reject a request, and must give a reason | Must |
| BR-11 | On approval, the employee's remaining balance reduces by the working days of the request | Must |
| BR-12 | The employee is notified by email when their request is approved or rejected | Should |
| BR-13 | An HR Administrator can view all requests across the organisation | Must |
| BR-14 | An HR Administrator can maintain leave types and annual entitlements | Must |
| BR-15 | An HR Administrator can maintain the public holiday calendar | Must |
| BR-16 | An HR Administrator can adjust an employee's balance, and must give a reason | Should |
| BR-17 | Every state change on a request is recorded with the actor, the timestamp and any reason given | Must |
| BR-18 | A user signs in with an email address and password | Must |

## 10. Business rules

| # | Rule | Rationale |
|---|---|---|
| BRL-01 | A request may not exceed the employee's remaining balance for that leave type | Entitlement is a contractual limit |
| BRL-02 | Weekends and public holidays do not count as leave days | Leave is measured in working days |
| BRL-03 | A request may not overlap another request by the same employee in `Submitted` or `Approved` state | A day cannot be taken twice |
| BRL-04 | The end date may not be earlier than the start date | — |
| BRL-05 | A request should be submitted at least **three working days** before its start date. A shorter request is permitted but must be flagged to the approver | Operational planning, without blocking genuine emergencies |
| BRL-06 | **A manager may not approve or reject their own request.** It is routed to the HR Administrator | Separation of duties |
| BRL-07 | Half days are permitted only on the first and last day of a request | A half day in the middle is an attendance matter, not leave |
| BRL-08 | A rejection must carry a reason of at least 10 characters | A bare rejection generates an immediate follow-up enquiry |
| BRL-09 | Leave may not be requested for a date in a closed leave year | The year is reconciled and reported |
| BRL-10 | The leave year runs 1 January to 31 December | Current HR policy |
| BRL-11 | Unused entitlement does not carry into the next leave year in this release | Simplifies the first release; see OQ-5 |
| BRL-12 | A balance may not go negative by any route, including an HR adjustment | — |

## 11. Data requirements

Business attributes only. The delivery team designs the data model.

**Employee** — name, work email, employee number, department, line manager, role, start date, active

**Leave type** — name, annual entitlement in days, whether a reason is mandatory, active.
Initial types: Annual Leave (25 days), Unpaid Leave (0 days, reason mandatory), Compassionate
Leave (5 days, reason mandatory)

**Leave request** — employee, leave type, start date, end date, half-day start, half-day end,
working days, reason, state, submitted at, decided by, decided at, decision reason

**Public holiday** — date, name, country

**Audit record** — request, previous state, new state, actor, timestamp, reason

## 12. Non-functional requirements

| # | Requirement |
|---|---|
| NFR-06 | A screen is usable within 2 seconds on an office connection |
| NFR-07 | 250 named users, up to 40 concurrent |
| NFR-08 | Available during UK office hours, 08:00–18:00 |
| NFR-09 | Audit records are retained for 7 years and cannot be edited or deleted |
| NFR-10 | Passwords are stored so that they cannot be recovered, only reset |
| NFR-11 | An employee can reach only their own data; a manager only their direct reports'. Enforced by the application, not by the interface hiding things |
| NFR-12 | A daily backup from which a restore has actually been performed |
| NFR-13 | Deployed to the Vicatech development server through the standard automated pipeline, with no manual file copying |

## 13. Reporting

| # | Report | Audience |
|---|---|---|
| RPT-01 | Leave taken and remaining by employee, for a chosen leave year | HR, Managers |
| RPT-02 | Requests awaiting a decision, with how long they have waited | HR |
| RPT-03 | Leave calendar for a department over a chosen month | Managers |

Exportable to a spreadsheet. Production of RPT-03 as a visual calendar is desirable but not required
for this release.

## 14. Assumptions

| # | Assumption |
|---|---|
| ASM-1 | Employee records, including the line-manager relationship, are loaded once at launch from an HR extract. Ongoing synchronisation is out of scope |
| ASM-2 | Every employee has exactly one line manager |
| ASM-3 | All employees are in the United Kingdom for this release, so one public holiday calendar is sufficient |
| ASM-4 | Email delivery uses existing corporate mail infrastructure |

## 15. Constraints

| # | Constraint |
|---|---|
| CON-1 | Launch before the start of the next leave year, 1 January 2027 |
| CON-2 | Must run on the existing Vicatech development and hosting infrastructure |
| CON-3 | No new third-party subscription may be introduced without procurement approval |

## 16. Open questions

**These are not oversights. They are decisions the business has not yet made, and the delivery team
must not invent an answer.**

| # | Question | Owner | What it affects |
|---|---|---|---|
| OQ-1 | When a request is `Submitted` but not yet decided, is the balance reserved, or only reduced on approval? Two employees could each submit a request that individually fits the balance but together does not | HR Operations | BRL-01, and what SCR-03 shows the approver |
| OQ-2 | Where does the public holiday calendar come from, and who confirms it each year? | People Operations | BRL-02, BR-15 |
| OQ-3 | Who approves when the line manager is themselves on leave? | Head of People Operations | BR-08, and whether delegation is really out of scope |
| OQ-4 | Can an approved request be cancelled *after* its start date — for example, leave cut short? If so, what happens to the balance? | HR Operations | BR-06, BRL-12 |
| OQ-5 | Is carry-over genuinely not required, or deferred? If deferred, the data must support it from the start | Head of People Operations | BRL-11 |
| OQ-6 | Should a manager be able to see a direct report's remaining balance for leave types they have not requested? | HR, with Legal | SCR-03 |

## 17. Acceptance criteria

The release is accepted when all of the following are demonstrated:

1. An employee signs in, sees their balance per leave type, and submits a request whose working-day
   count was visible before submission.
2. A request exceeding the remaining balance is refused, with a message naming the balance.
3. A request overlapping an existing submitted request is refused.
4. A request spanning a weekend and a public holiday counts only the working days.
5. A manager sees the request, approves it, and the employee's remaining balance reduces accordingly.
6. A rejection without a reason is refused; with a reason, it is recorded against the named manager.
7. A manager's own request does not appear in their own approval queue.
8. An employee navigating directly to the Approvals screen is refused, not merely redirected.
9. Every state change in the above is visible in the audit record with actor and timestamp.
10. All three screens are usable at 400px width, and state is legible in a black-and-white printout.
11. The application is deployed to the development server by the automated pipeline.

## 18. Glossary

| Term | Meaning |
|---|---|
| **Leave year** | The twelve-month period entitlement is counted against. Currently the calendar year |
| **Entitlement** | Days of a leave type an employee may take in a leave year |
| **Balance** | Entitlement less approved leave |
| **Working day** | A day that is not a weekend and not a public holiday |
| **Direct report** | An employee whose line manager is the user |
| **Draft** | A request created but not submitted; not counted against balance |

---

*End of document. Requirement identifiers in this document are stable and may be cited in
downstream specifications, tasks and tests.*
