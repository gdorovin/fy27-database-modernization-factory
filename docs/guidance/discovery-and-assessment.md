# Discovery and assessment

> **verified_on: 2026-09-15.** Support-status thresholds and tool behaviour described here
> perish. Revalidate `src/dbmodernize/scoring/reference.py` against current product
> documentation before quoting any of it to a customer.

## The question discovery actually answers

Not "what databases are there". That is inventory, and every customer has a spreadsheet.

The question is **"how much of the estate does this inventory represent, and how would we
know"** — because the failure mode is not a missing database. It is a programme built on a
count that turned out to be wrong, which is what killed the previous attempt in Scenario 05.

## Coverage, not count

An inventory needs an independent comparison: a CMDB, a licence position, a network scan.
Record the comparison as the `completeness_basis`.

"The tool returned successfully" is not a coverage basis. A tool reports what it can see, and
what it cannot see is exactly the part you are worried about.

```text
inventory_completeness: low
completeness_basis: >-
  Compared enrolled instances (2) with the stated estate total (12). The CMDB figure was
  last reconciled 2025-11-30 and has not been verified since.
```

That is worth more than a confident list of two instances.

## What blocks a recommendation

Five findings are blocking. Everything else is a severity, not a stop.

| Finding | Why it blocks |
| --- | --- |
| Unknown engine version | Support posture, upgrade path, and compatibility all derive from it |
| Incomplete dependency discovery | The blast radius of a cutover is unknown |
| Unresolved evidence conflict | Two sources disagree and nobody has said which is right |
| Directive-like content in an import | The evidence source needs reviewing before it is trusted |
| A tool-reported blocking issue | A tool found something specific; read it |

A blocked workload gets no destination. It can still receive a governed interim posture —
Arc, or retain — because the missing evidence stops you *moving* it, not *governing* it.

## Evidence classes, and why the default matters

| Class | From |
| --- | --- |
| `observed` | A tool reading a system |
| `user-provided` | A human filling in a form |
| `derived` | Computed from other evidence |
| `assumption` | Supplied to let work continue |

A CSV row is `user-provided` unless it declares `measured`. This is the most frequently
disputed default in the repository, and it is correct: a spreadsheet records what somebody
believed at the time they filled it in, which is a different thing from what the system
reports.

The consequence is visible downstream — sizing marked estimated cannot support a capacity
commitment, and the target decision says so.

## Running it

```bash
dbmodernize normalize-evidence --engagement input/engagement.yaml --input input --out out
dbmodernize assess --engagement input/engagement.yaml --input input --out out
```

The first prints record count, unresolved conflicts, and records flagged for directive-like
content. The second produces the inventory, findings, and risk register.

## Adapters

| Adapter | Reads | Contributes |
| --- | --- | --- |
| `csv-inventory` | `.csv` | Whatever a human recorded; the common starting point |
| `azure-migrate` | JSON with `databases` | Readiness verdicts, blocking issues, measured performance |
| `arc-sql` | JSON with `instances` | Continuous inventory, patch level, security findings, **enrollment coverage** |
| `dms` | JSON with `results` | Per-target feature parity and compatibility issues |
| `ssma` | JSON with `schemas` | Conversion statistics, and the manual and error counts that matter |

Arc is the only one that reports coverage, which is why it is disproportionately useful on an
estate nobody has mapped.

If a real export does not match an adapter, change the adapter. Do not hand-edit the export:
an undocumented transformation is worse than an unparsed file, because nobody can tell later
what was changed.

## Conflicts

Two sources disagreeing on a decision-critical attribute produces a conflict, and the merged
view omits the attribute entirely. Numeric differences within 5% are noise.

Resolution is a human decision, and it usually reveals something: in Scenario 05, a 28% size
disagreement means two systems of record disagree about a production database. Taking the
newer number would have hidden that.

## Interviews are evidence too

Much of what matters is not in any export: whether a feature is genuinely required, what the
planned-downtime budget is, who actually consumes a database.

Record those as `user-provided` with the stating role. An RPO nobody stated is an assumption
with someone's name on it, and it should look like one in the artifact.

## Reading the output

Look at the blocked workloads first — that is the discovery backlog, and it is the most
useful page of the assessment. Then read `completeness_basis` and ask whether you would defend
it. Then check whether anything is flagged for directive-like content.

The workload table is the least interesting part. Everyone reads it first anyway.

## Common mistakes

- Reporting the workload count as the estate size.
- Treating tool silence as absence.
- Filling a missing version with a plausible one.
- Marking dependency discovery complete because nobody objected.
- Committing a real export instead of a redacted fixture.
