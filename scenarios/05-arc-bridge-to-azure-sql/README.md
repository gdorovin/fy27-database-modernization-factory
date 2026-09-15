# Scenario 05 — Azure Arc as a governed bridge

**Prevents:** counting a governed-in-place workload as modernized.

## The situation

A group with databases across several business units and two acquisitions. A previous
migration attempt stalled when the inventory turned out to be wrong — the estate is
somewhere between forty and seventy instances, and the disagreement between those two
numbers is why the last programme died. Security has an open finding covering the estate as
a whole, which cannot be closed for systems nobody can enumerate.

| Workload | Evidence state |
| --- | --- |
| Group finance | Complete; linked servers in use |
| Shared services | Complete; no instance-scoped dependency |
| Acquired unit B sales | Consumers unknown |
| Legacy warehouse | Consumers unknown, **and sources disagree about its size** |

Arc reports 3 enrolled instances against a stated estate of 55.

## What the factory does, and why

**The size disagreement stops the line.** The CSV says 1,250 GB; Arc says 980 GB. That is a
28% gap, well outside measurement noise, so it is recorded as an unresolved conflict and
becomes a blocking finding. The repository does not take the newer figure, the more precise
figure, or the average. Picking one would hide the fact that two systems of record disagree
about a production database, which is itself the more interesting finding.

**Two workloads get a governed interim posture.** Neither Acquired unit B sales nor Legacy
warehouse can be moved — their consumers are unknown. Both receive Arc, and both decisions
say plainly that this is an interim posture, that the workload has not moved, and that it
must not be recorded as completed modernization.

That sentence is the whole scenario. An estate under audit pressure has every incentive to
report enrollment as progress, and enrollment changes the governance position without
changing the migration position at all.

**The programme still moves.** Group finance and Shared services have complete evidence and
get real destinations — instance scope and database scope respectively. A bridge for the
unknown parts is not an excuse to stall on the known ones.

**Inventory completeness is `low`, with the basis stated.** Three of fifty-five, and the
executive brief leads with it rather than burying it.

**The restart is small.** One pilot workload, not an estate-wide phase. The previous attempt
failed at scale; repeating the scale would repeat the failure.

## Wave plan

| # | Wave | Contents |
| --- | --- | --- |
| 1 | Pilot | Shared services |
| 2 | Business critical | Group finance |

Both Arc-governed workloads appear in `deferred_workload_ids`.

## What would break this

- Resolving the size conflict automatically.
- Describing Arc enablement as modernization, or counting it as wave progress.
- Scheduling a workload with unknown consumers.
- Reporting inventory as complete because the tool returned successfully.
