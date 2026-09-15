# Observability

Two different things are worth observing, and conflating them causes confusion: the
**toolkit**, and the **engagement**.

## Observing the toolkit

There is very little to watch. The CLI is a local, offline process with no network calls, no
background work, and no state beyond the files it writes.

| Signal | Where | Use |
| --- | --- | --- |
| Exit code | Process | The primary signal; script against it |
| Findings | stderr, or `--json` | Rule id, artifact path, message |
| Debug log | stderr with `--verbose` | Adapter selection, skipped files |

```bash
dbmodernize validate-repo --json | jq '.findings[] | select(.severity=="error")'
```

Logging goes through a redacting handler, installed at the handler rather than the call site,
so a caller cannot forget to redact. Connection strings, tokens, and key-like values are
masked before anything is written.

There is no telemetry. Nothing phones home.

## Observing an engagement

This is the part that matters, and it is mostly about noticing when a number stops moving.

| Signal | Read from | What a bad value looks like |
| --- | --- | --- |
| Inventory completeness | `workloads.json` | `low`, and unchanged for weeks |
| Blocked workloads | Assessment summary | Rising, or static |
| Unresolved conflicts | `evidence.json` | Any that are older than a fortnight |
| Workloads without a destination | `target-decisions.json` | Should fall over time |
| Open high risks | `risks.json` | Any without a due date |
| Deferred workloads | `waves.json` | Growing faster than waves complete |
| Blocking checks not run | Validation report | Any, at a go decision |

A weekly check of the first three is usually enough to tell whether an engagement is
progressing or quietly stalling. A stalled engagement looks identical to a progressing one
in a status meeting; it looks obviously different in these numbers.

## The metric that predicts failure

**Blocked workloads that are not falling.**

Every blocked workload has an owner and a specific piece of missing evidence. If the count
holds steady for three weeks, the evidence gathering is not funded, not owned, or not
believed to matter — and the programme will hit its date with an estate it cannot describe.

This is what killed the previous attempt in Scenario 05.

## Observing the target after migration

Not this toolkit's job, but the plan must require it. A wave cannot exit until monitoring
and alerting are **live, routed to a named owner, and tested with a real alert**.

"Monitoring is configured" and "an alert reached a human" are different claims. The
validation plan checks the second one.

## Traces, for a future runtime

When this is wired into an agent runtime, a correlation id should flow through every step and
appear in every artifact. The artifact chain already provides most of what a trace would:
each artifact records its author, its timestamp, and the ids it derived from.

The gap a real trace would close is timing — how long a step took, and where a long-running
engagement actually spends its time.

## What is deliberately not observable

No usage analytics, no error reporting service, no crash telemetry. This runs on machines
holding customer engagement data, and the safest telemetry pipeline is the one that does not
exist.
