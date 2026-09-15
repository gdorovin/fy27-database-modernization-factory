---
name: oracle-heterogeneous-migration
description: Guide Oracle disposition, schema and PL/SQL conversion, data movement, application remediation, and business validation, and prevent any claim of automatic cross-engine compatibility.
---

# Oracle heterogeneous migration

A qualification exercise before it is a migration. Most of the risk is in code nobody has
read for a decade, and the failure mode is a conversion percentage being mistaken for a
compatibility verdict.

## Invoke when

- An Oracle workload is being considered for a different engine.
- Conversion evidence needs interpreting.
- A per-schema disposition is needed across an Oracle estate.
- Someone has quoted an automatic-conversion percentage as though it settled the question.

## Do not invoke when

- The source is SQL Server — use `sql-server-modernization` instead.
- The source is PostgreSQL, MySQL, or MariaDB — use `postgres-mysql-modernization` instead.
- The Oracle system is staying and only needs governing — defer to
  `governance-compliance`.

## Required inputs

| Input | Source | Required |
| --- | --- | --- |
| Version and edition | Instance query | Yes |
| Object counts per schema | Catalogue query | Yes |
| Conversion assessment against a **named** target | SSMA or equivalent | Yes, before any recommendation |
| PL/SQL complexity, by pattern | Conversion output | Yes |
| Application coupling to database code | Application owner | Yes |
| Licensing and support position | Account team | For the business case only |
| Business intent per system | Sponsor | Yes |

## Preconditions

1. A conversion assessment exists **for the specific target under consideration**. An
   assessment against one destination says nothing about another.
2. The application owner is engaged. Converted code is changed code, and changed code is
   an application problem before it is a database one.
3. The customer understands that retaining, replacing, or coexisting are legitimate
   outcomes for some schemas.

## Procedure

1. Treat each schema separately. An Oracle estate rarely has one answer, and forcing one
   is how the difficult schema sinks the whole programme.
2. Ask whether the system should move at all. Vendor-supported applications, safety-rated
   systems, and products with a SaaS equivalent may have better answers than conversion.
3. For each candidate, obtain a conversion assessment against the named target. Without
   one, every cross-engine target is blocked — by design.
4. Read the assessment for what did **not** convert. Manual and error counts are the
   signal; the automatic percentage is the distraction.
5. Categorise the manual work: package-level state, autonomous transactions, hierarchical
   queries, sequence semantics, implicit type conversion, date arithmetic, error handling.
6. Size the application remediation with the application owner, not from object counts.
7. Define business validation: named users exercising agreed scenarios and comparing
   results. This is the acceptance evidence, and nothing else substitutes for it.
8. Plan data movement separately from code conversion. They fail in different ways.

## Decision points

| Evidence | Disposition |
| --- | --- |
| No conversion assessment | No migration recommendation; retain and assess |
| Assessment exists for target A only | Only target A is comparable; others stay blocked |
| High manual and error counts | Conversion is a project; scope it honestly or reconsider |
| Vendor-supported application, terms unreviewed | Retain until the terms are known |
| A product covers the capability | Replace, with its own data and integration plan |
| Schema is small and mostly relational | Conversion is viable; still requires application testing |

## Output contract

A target decision per schema with `conversion_required: true`, a disposition of at least
`refactor`, the conversion evidence referenced, and an application-impact note that names
remediation and business validation as required work.

The rationale must state that automatic compatibility is not claimed.

## Validation

```bash
dbmodernize recommend-targets --engagement input/engagement.yaml --input input --out out
dbmodernize validate-scenario scenarios/04-oracle-heterogeneous-modernization
```

## Failure and fallback

- **Conversion tooling cannot process a schema.** That is evidence, not an obstacle to work
  around. Record it and treat the schema as a separate decision.
- **Application owner unavailable.** Stop before recommending. Converted code without an
  owner to test it is a liability transfer, not a migration.
- **Customer pressure to commit to a date.** Give the conversion and remediation scope, and
  name the unknowns. A date built on an unread PL/SQL package is a date that slips.

## Avoid

- Quoting an automatic-conversion percentage as a compatibility statement.
- Assuming a conversion result transfers between destinations.
- Treating conversion output as tested code.
- Estimating remediation from object counts alone.
- Presenting a single estate-wide Oracle answer.

## Example

A conversion assessment reports 84% automatic for one schema. The recorded finding does
not lead with that number. It leads with: *133 objects need manual work and 20 failed to
convert*, and it states that a conversion percentage is not a compatibility verdict.

A second schema, assessed against a different target, is not comparable — and the
comparison blocks every destination the assessment did not cover.
