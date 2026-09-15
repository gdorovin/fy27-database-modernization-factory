# Scenario 03 — Self-managed PostgreSQL to Flexible Server

**Prevents:** waving extensions through as "compatible" without checking them per version.

## The situation

A logistics business running self-managed PostgreSQL on virtual machines, several versions
behind, with high availability implemented by in-house scripting that two people understand.
A security review flagged both the version and the absence of any tested recovery.

| Workload | Version | Extensions in use | Notable |
| --- | --- | --- | --- |
| Routing engine | 11.9 | `postgis`, `pg_cron`, `pg_stat_statements` | Geospatial extension is central to the routing algorithm |
| Tracking history | 11.9 | `pg_partman`, `pg_stat_statements` | 1.9 TB, 55% growth, depends on Routing engine |
| Partner integration | 12.4 | `pgcrypto`, `pg_stat_statements` | GDPR scope |

## What the factory does, and why

**The managed flexible server is recommended — conditionally.** It is the default candidate
for this engine family, and the comparison says so. But the recommendation carries a
high-severity finding on extensions, and the wave carries a verification prerequisite.

**Extensions are the story, not a detail.** The assessment names each one and records that
availability must be verified *per extension and per server version*. A general answer is
not an answer: availability differs by version, and the one that matters here is central to
the application's core algorithm. If it turns out to be unavailable, the decision is
revisited before any data moves rather than after.

**SQL Server targets never appear.** They are not candidates for a PostgreSQL workload
without conversion, so they are not in the comparison at all — as opposed to being listed
and rejected, which would imply they were plausible.

**Unsupported versions raise urgency, not a target.** Being past end of support makes the
conversation urgent. It does not select a destination.

**Availability is tested, not assumed.** The validation plan carries a controlled failover,
a real restore, and measured RPO and RTO. The customer has never tested recovery, so the
current design is a hypothesis; the plan treats it as one.

**Networking and identity are planned.** Private access, name resolution, and authentication
method are all validation checks rather than assumptions, because a connectivity surprise at
cutover is both avoidable and expensive.

## Wave plan

| # | Wave | Contents | Why |
| --- | --- | --- | --- |
| 1 | Pilot | Partner integration | Independent, smallest, still exercises extensions and compliance |
| 2 | Business critical | Routing engine and Tracking history | Coupled; they move together |

## What would break this

- Describing this as a lift and shift.
- Answering extension availability generally rather than per version.
- Omitting the failover or restore test because the design "looks right".
