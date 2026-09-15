# Scenario 02 — SQL Server to Azure SQL Database

**Prevents:** reaching for the high-scale tier when neither size nor growth asks for it.

## The situation

A software product company. The application was written in the last three years, holds no
instance-scoped database dependencies, and the team releases weekly. Growth is uneven and
the current fixed provisioning is sized for the worst week of the year.

| Workload | Size | Growth | Notable |
| --- | --- | --- | --- |
| Tenant metadata | 45 GB | 15% | Small, read by every request |
| Product core | 260 GB | 25% | Depends on Tenant metadata |
| Product events | 2,400 GB | 65% | High-growth event store, measured over a full cycle |
| Product staging | 60 GB | 10% | Pre-production rehearsal copy |

## What the factory does, and why

**Three workloads go to database scope, one goes to the high-scale tier.** The difference is
evidence, not preference. Product events is 2.4 TB growing at 65% per year; the others are
not close.

**The high-scale tier is explicitly rejected for the small workloads.** The rationale says
that neither size nor growth justifies it, and that choosing it would add capability nobody
asked for. Over-provisioning is a quieter failure than under-provisioning — nothing breaks,
so nobody investigates — which is why it needs an explicit rejection rather than silence.

**Instance scope is rejected too.** No instance-scoped dependency exists, so instance scope
is more surface area than these workloads need. The comparison scores it below database
scope and says why.

**Infrastructure is rejected for the same reason in reverse.** No operating-system
dependency exists, so choosing infrastructure would retain patching and availability
responsibility without a reason the evidence supports.

**Application testing is not optional.** The validation plan carries functional, regression,
integration, performance, and concurrency checks per workload. A modern application is
easier to move, not exempt from proof.

**Infrastructure work is what-if first.** The provisioning task carries a what-if command,
an approval requirement, and a rollback note — even in non-production.

## Wave plan

| # | Wave | Contents | Why |
| --- | --- | --- | --- |
| 1 | Pilot | Product staging | Independent, pre-production, small |
| 2 | Business critical | Tenant metadata, Product core, Product events | A connected dependency chain; they move together |

## What would break this

- Recommending the high-scale tier for a 45 GB database.
- Recommending instance scope where no instance-scoped feature is in use.
- A migration plan with no what-if step before provisioning.
- Any zero-downtime claim, in any wording, without a measured rehearsal behind it.
