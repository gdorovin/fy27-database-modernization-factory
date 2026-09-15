# Scenario 01 — SQL Server 2016 to Azure SQL Managed Instance

**Prevents:** recommending a destination for a workload whose consumers nobody can name.

## The situation

A retail estate on an engine version that no longer receives security fixes, with a renewal
twelve months out and an open audit finding. Four workloads, two of which the team
understands well and one of which nobody can fully account for.

| Workload | Notable | Evidence state |
| --- | --- | --- |
| Payments core | Scheduled jobs, cross-database queries, service broker | Complete |
| Customer portal | No instance-scoped dependency; reads from Payments core | Complete |
| Store operations | Consumers unknown | **Incomplete** |
| Reporting sandbox | Development copy | Complete |

Arc reports 2 enrolled instances against a stated estate of 12.

## What the factory does, and why

**Store operations gets no destination.** Dependency discovery is incomplete, so the blast
radius of a cutover is unknown. Every migration target is *blocked*, and the rationale says
so explicitly. This is the scenario's central assertion: the pressure in a real engagement
is to recommend something, because a recommendation looks like progress.

**It is still governed.** Arc is offered as an interim posture — it improves inventory and
security posture without moving the workload, and the decision states that it must not be
recorded as completed modernization. The workload appears in `deferred_workload_ids`, not
in a wave, and an issue is generated to close the gap.

**Payments core goes to instance scope.** Three instance-scoped features are in use.
Database-scoped targets are blocked rather than scored down, because the features are
unavailable there — a scoring penalty would imply the trade was merely expensive.

**Customer portal goes to database scope.** Same estate, same instance, different answer.
An estate-wide default would have moved both to the same place, and one of them would have
broken.

**Downtime stays `short-planned`.** No rehearsal has run, so no stronger claim is
available. The class is upgraded when a rehearsal produces a number, not when someone feels
confident.

**Inventory completeness is `low`,** and the executive brief leads with it. Two of twelve
instances is not an estate.

## Wave plan

| # | Wave | Contents | Why |
| --- | --- | --- | --- |
| 1 | Pilot | Reporting sandbox | Small, non-production, safe to fail |
| 2 | Business critical | Payments core and Customer portal together | They reference each other; splitting them produces a cutover that half-works |

## What would break this

- Recommending a target for Store operations.
- Describing Arc enablement as modernization.
- Giving both SQL workloads the same destination.
- Any `near-zero` downtime claim without a measured rehearsal.
- A pilot containing a production workload.

Each of those is an acceptance criterion in `scenario.yaml`.
