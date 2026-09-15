---
name: sql-server-modernization
description: Assess a SQL Server workload for its Azure options, covering version support, instance-scoped feature use, editions, availability design, and application coupling, without assuming a single destination.
---

# SQL Server modernization

SQL Server has more viable destinations than any other source platform here. That breadth
is the risk: it makes a default tempting, and a default is how workloads end up somewhere
the evidence never pointed.

## Invoke when

- A SQL Server workload needs assessing for its Azure options.
- Version, edition, or support posture needs establishing.
- Instance-scoped feature use needs inventorying.
- A hybrid or staged path is under discussion for a SQL Server estate.

## Do not invoke when

- The source is PostgreSQL, MySQL, or MariaDB — use `postgres-mysql-modernization` instead.
- The source is Oracle — use `oracle-heterogeneous-migration` instead.
- The comparison itself is being run — defer to `azure-target-recommendation`, which this
  skill feeds.

## Required inputs

| Input | Source | Required |
| --- | --- | --- |
| Engine version and edition | Instance query, Arc, or Azure Migrate | Yes |
| Features in use | Instance inspection, not configuration | Yes |
| Database and largest-table sizes | Measured, where possible | Yes |
| Availability configuration and tested recovery | Operations owner | Yes |
| Application connection and dependency map | Application owner | Yes |
| Compliance scope | Security owner | Where applicable |

## Preconditions

1. The version is known. An unknown version blocks the assessment, because support posture
   cannot be derived from a guess.
2. Feature use is evidenced by observation, not inferred from the fact that a feature is
   installed. Installed is not used.
3. Dependency discovery has run, or its absence is recorded as blocking.

## Procedure

1. Establish version and edition, and derive support posture from the dated reference
   table in `src/dbmodernize/scoring/reference.py`. Revalidate that table before quoting
   it to a customer.
2. Inventory instance-scoped features actually in use: scheduled jobs, cross-database
   queries, service broker, linked servers, CLR, filestream, replication, distributed
   transactions, server-level triggers.
3. Inventory operating-system dependencies: third-party agents, filesystem access,
   extended stored procedures. Any of these rules out every managed target.
4. Record sizing and growth, and mark whether they were measured.
5. Record the availability configuration, and whether failover has ever been tested. An
   untested failover is a design, not a capability.
6. Record the planned-downtime budget. Without one, no cutover method can be justified.
7. Hand the assessed workload to `azure-target-recommendation`.

## Decision points

| Evidence | Effect on the comparison |
| --- | --- |
| Instance-scoped features in use | Database-scoped targets are blocked, not penalised |
| Operating-system dependency in use | Every managed target is blocked |
| Large size or high growth | The high-scale tier enters the comparison |
| Neither size nor growth notable | The high-scale tier is rejected as unwarranted |
| Estate inventory unproven | A governed bridge becomes worth comparing |
| Version past support | Raises urgency; it does not select a target |

## Output contract

An assessed workload carrying: `source_version`, `edition`, derived `support_status`,
`instance_features`, `sizing` with a `measured` flag, `service_level`, `dependencies` with
confirmation status, and findings for every gap.

## Validation

```bash
dbmodernize assess --engagement input/engagement.yaml --input input --out out
dbmodernize validate-scenario scenarios/01-sql2016-to-managed-instance
dbmodernize validate-scenario scenarios/02-sql-to-azure-sql-database
```

## Failure and fallback

- **Version unobtainable.** Record it as unknown. The blocking finding is correct, and
  inventing a version would hide the real problem.
- **Feature use uncertain.** Treat the feature as in use and record an open question.
- **No downtime budget.** Record a high-severity finding and keep the downtime class
  `unknown`. A method cannot be selected against an unstated constraint.
- **Availability requirements unstated.** Record as an assumption owned by the business
  owner, and mark confidence low.

## Avoid

- Assuming every SQL Server workload goes to the same destination.
- Treating an installed feature as a used feature, or a used feature as a required one.
- Deriving support status from an edition rather than a version.
- Quoting a support date without revalidating the reference table.
- Describing a hybrid governance step as completed modernization.

## Example

Two databases on the same instance. One uses scheduled jobs and cross-database queries;
the other uses neither.

They receive different destinations — instance scope for the first, database scope for the
second — from the same evidence set. An estate-wide default would have moved both to the
same place, and one of them would have broken.
