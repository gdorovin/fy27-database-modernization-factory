# FY27 context

> **verified_on: 2026-09-15.** Everything on this page about product support, service
> capability, commercial terms, or programme availability perishes. Revalidate against
> current product documentation and with the account team before using any of it with a
> customer.

## The framing that works

Database modernization is a customer-outcome motion, not an infrastructure project. The
difference shows up in the first meeting: an infrastructure project is sponsored by whoever
owns the servers, and a customer-outcome motion is sponsored by whoever owns the
consequence of the servers failing.

Lead with the outcome the customer would notice:

- Secure, governed, resilient operational data.
- Faster application and data change.
- Lower operational and support burden.
- Reduced end-of-support, cyber, compliance, and infrastructure risk.
- A practical path from a legacy estate to measurable business value.

A conversation that starts with a product name has already skipped the part that determines
whether the project survives its first setback.

## Entry points

All of these lead into the same journey. They differ in urgency, in who cares, and in what
evidence already exists — not in destination.

| Trigger | What it really means | Usual sponsor |
| --- | --- | --- |
| Licence or agreement renewal | A fixed external date that does not move | Commercial lead, CIO |
| End of support | Security fixes have stopped arriving | Security, risk |
| Aging hardware | Failure is scheduled, just not by you | Infrastructure |
| Security or compliance finding | Someone external is now asking | Security, compliance |
| Application modernization | The database is holding the application back | Application owner |
| Data-centre exit | A date set by a lease, not by IT | CIO, finance |
| Stalled migration | The last attempt failed, usually on inventory | Delivery |
| AI, analytics, or agent requirement | An ambition with unexamined prerequisites | Business unit |
| Oracle renewal, audit, or cost pressure | Commercial, with a technical consequence | CFO, CIO |
| Unsupported open-source version | Nobody owns the upgrade | Engineering |
| Competitive cloud pressure | A strategic conversation wearing a technical costume | Executive |
| Availability or disaster-recovery gap | An assumption nobody has tested | Operations |
| Operational scale | The team cannot grow as fast as the estate | Operations |

The trigger tells you who to talk to and how much time you have. It tells you nothing about
where a workload should go.

## Journeys

Twelve, and the repository supports all of them. Note how many are not "migrate to the
managed service":

1. SQL Server to Azure SQL, in its various forms.
2. A renewal converted into a modernization commitment.
3. SQL Server to Managed Instance, where instance scope is genuinely needed.
4. SQL Server to Azure SQL Database, where it is not.
5. SQL Server to Hyperscale, where size or growth justifies it.
6. SQL Server on Azure VMs, where operating-system or engine control is required.
7. Hybrid management and staged modernization through Azure Arc.
8. Self-managed PostgreSQL to a managed flexible server.
9. Self-managed MySQL or MariaDB to a managed flexible server.
10. Oracle to a different engine, after explicit suitability analysis.
11. Application-plus-database modernization, where the application is the blocker.
12. Modernization followed by analytics or AI attachment, where readiness supports it.

An estate rarely follows one. Two databases on the same instance can legitimately land in
different places, and an assessment that produces a single answer for everything has usually
stopped looking.

## Cadence

Configurable guidance anchored to a renewal or support-expiry date, not a fixed schedule.
Adjust it to the customer's calendar.

| Point | Objective | Question it answers |
| --- | --- | --- |
| T-12 | Discover, engage, establish the outcome | What does the customer actually want? |
| T-9 | Assess readiness, model target options | What is possible, and what is blocked? |
| T-6 | Agree architecture, secure sponsorship | Who is paying, and for what? |
| T-3 | Agree delivery model, waves, owners, acceptance | Who does what, and how will we know? |
| T-0 | Execute an approved cutover, or have the first workload live | Did it work? |
| T+0 to T+90 | Stabilize, optimize, retire legacy, activate the roadmap | What did we learn? |

Two rules keep this honest under pressure. **Work backwards from the date**, because a plan
that needs everything to go right has already failed. And **when the date is at risk, scope
moves, not the gate** — fewer workloads in the wave, never a shorter validation.

## Where engagements go wrong

Observed repeatedly, and each one has a control in this repository:

| Failure | Control |
| --- | --- |
| A target chosen before dependencies were known | A blocked workload gets no destination |
| An inventory that turned out to be wrong | Completeness is judged and stated, never assumed |
| A downtime figure quoted before anything was measured | Downtime claims require a rehearsal |
| A cutover approved by whoever was in the room | All five owner roles, counted |
| A "successful" migration that was quietly rolled back | A blocking failure forces no-go |
| An Oracle programme sunk by its hardest schema | Per-schema dispositions |
| An AI ambition built on unowned data | Readiness assessed separately, conditionally |
| Arc enablement reported as modernization | Arc classifies as retain |

## Tooling

Evidence can come from Azure Migrate, Arc-enabled SQL Server assessment, Azure Database
Migration Service (including the Azure SQL migration extension), SQL Server Migration
Assistant for Oracle-to-SQL conversion, an Oracle-to-PostgreSQL conversion tool, or a
spreadsheet. Data Migration Assistant is retired and is not an input.

The repository is deliberately not coupled to any one of them. Adapters normalize onto a
common evidence contract, so a customer who has only a CMDB extract is not blocked, and a
customer with three tools does not get three incompatible answers.

A tool's readiness verdict is recorded as evidence. It is an input to the decision, never
the decision — the tool cannot see the constraint the application owner mentioned in passing.

## What this page does not claim

No pricing, no funding programme, no eligibility, no preview status, no service limit. Those
change faster than any repository can track. Ask the account team, and record what they say
with a date.
