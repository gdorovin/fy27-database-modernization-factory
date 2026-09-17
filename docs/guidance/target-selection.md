# Target selection

> **verified_on: 2026-09-15.** Service capabilities, limits, and support status change.
> The thresholds in `src/dbmodernize/scoring/reference.py` were last checked on this date
> and must be revalidated before any of this reaches a customer.

## The principle

There is no estate-wide answer. Two databases on the same instance can legitimately land in
different places, and an assessment producing one answer for everything has usually stopped
looking.

## Blocked, not penalised

The distinction that matters most, and the one people get wrong:

- A **blocker** is a capability that does not exist at the target. Scoring it down implies
  the trade is merely expensive, when in fact it is unavailable.
- A **penalty** is a real cost the customer could choose to accept.

Instance-scoped features against database scope: blocked. Operating-system dependency
against any managed target: blocked. Data residency that a region cannot satisfy: blocked.

Retaining patching responsibility for no reason: penalised, heavily, but choosable.

## The candidates

| Source | Compared against |
| --- | --- |
| SQL Server | Managed Instance, SQL Database, Hyperscale, SQL Server on Azure VM, Arc, retain |
| PostgreSQL | PostgreSQL Flexible Server, self-managed on Azure VM, retain |
| MySQL, MariaDB | MySQL Flexible Server, self-managed on Azure VM, retain (MariaDB requires conversion evidence) |
| Oracle | Oracle Database@Azure, PostgreSQL Flexible Server, Managed Instance, SQL Database, self-managed on Azure VM, replace, retain |

Every candidate appears in the decision record, including prohibited ones — rejected with a
citation. Silently omitting an option hides that it was considered, and the rejected options
are the part that survives review.

## What moves the score

Reconstructable by hand from `scoring/targets.py`. Base is 50.

**Azure SQL Database**
`+15` no instance-scoped dependency · `+10` managed operations ·
`−20` size above the point where Hyperscale is the fairer comparison ·
`−10` growth that strains a fixed tier.

**Hyperscale**
`+20` size in the range it exists to serve · `+15` growth favouring elastic storage ·
`+5` managed operations ·
`−25` when neither applies, because it adds capability nobody asked for.

**Managed Instance**
`+25` instance-scoped features in use · `+12` broad engine compatibility ·
`+8` managed operations ·
`−5` when no instance-scoped dependency exists.
Blocked outright, like every managed target, when FILESTREAM, FileTable, or PolyBase is in
use: those have no managed home at any scope, so they never count as instance-scoped.

**Oracle Database@Azure** (Oracle sources only)
`+20` engine unchanged, no conversion · `+10` Oracle-managed infrastructure ·
`−10` commercial terms, region, and licence entitlement are unverified account-team inputs ·
`+5` engine-native availability for a critical workload. A relocation, not an engine
modernization, and the decision record says so.

**SQL Server on Azure VM**, and the source engine self-managed on an Azure VM
`+30` operating-system control, or a feature no managed target offers, required · `+10` full engine control ·
`−18` when no such dependency exists · `−5` for a business-critical workload, since
availability design stays with the customer.

**Arc-enabled SQL Server**
`+25` when evidence is incomplete · `+5` posture improvement ·
`−15` when the evidence is already sufficient to decide.

**Managed PostgreSQL or MySQL**
`+20` default for the engine family · `+10` built-in availability and backup ·
`−12` extensions requiring per-version verification.

**Retain**
`−20` because it leaves every current risk in place · `+15` when an operating-system
dependency must be removed first · `+10` when blocking findings mean any move would rest on
incomplete evidence.

## Heterogeneous moves

Crossing engine families is a conversion exercise, and the repository enforces two things
that people talk themselves out of:

**No conversion evidence, no recommendation.** Every cross-engine target is blocked until an
assessment exists.

**Evidence does not transfer between targets.** A schema assessed against PostgreSQL says
nothing about Managed Instance. Without this rule a tie-break can recommend a destination
nobody ever assessed — and the comparison looks exactly as confident.

Neither rule is negotiable by scoring.

## Downtime

| Class | Requires |
| --- | --- |
| `unknown` | No agreed downtime budget |
| `short-planned` | A budget exists, no rehearsal yet |
| `near-zero-planned` | **A measured rehearsal** |
| `zero` | Does not exist |

The model rejects "zero downtime" in any wording, and rejects `near-zero-planned` without a
measurement. The claim is made in a workshop and tested at 03:00 on a Saturday, and only one
of those two moments has consequences.

## Cost

The repository generates no cost figure. Ever.

Cost inputs are attached to a decision with a named source and an estimate flag. An empty
cell with an owner beats a plausible number with none, because the plausible number gets
quoted in a board pack and becomes a commitment nobody can reproduce.

## Reading a decision

Read the rejected options first. They contain the reasoning; the recommendation is just the
conclusion.

Then check `downtime_approach.measured`, `sizing.measured`, and `evidence_refs`. Those three
tell you how much weight the decision can carry.

## A worked example

Two databases, one instance, same evidence set.

*Payments core* uses scheduled jobs, cross-database queries, and service broker. Database
scope is **blocked** — the features are unavailable there. Managed Instance scores 95:
`+25` features available at instance scope, `+12` compatibility, `+8` managed operations.
Azure VM scores 37: no operating-system dependency, so it would keep patching for nothing.

*Customer portal* uses none of them. Azure SQL Database scores 75; Managed Instance scores
65 and is rejected as more surface area than the workload needs.

Same instance, same evidence, different answers. An estate-wide default would have moved
both to the same place, and one of them would have broken.

## Status

A recommendation is `recommended`. It becomes `approved` only when an approval artifact
exists, authored by a different principal, whose content hash still matches.

Edit the decision after approval and the approval becomes stale automatically.
