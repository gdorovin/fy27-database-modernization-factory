---
name: modernization-classification
description: Assign each workload a disposition of rehost, replatform, refactor, rearchitect, rebuild, retain, retire, or replace, with the evidence that justifies it. Use after assessment and before comparing Azure targets.
---

# Modernization classification

Decides what *kind* of change a workload needs. Target selection answers where it goes;
this answers how much of it has to change to get there.

## Invoke when

- A workload inventory with findings exists and each workload needs a disposition.
- A disposition is being challenged and the reasoning needs restating.
- New evidence changes what a workload would need — for example, a dependency turns out to
  be removable.

## Do not invoke when

- Findings have not been produced yet — use `estate-discovery` instead.
- The question is which Azure service to use — defer to `azure-target-recommendation`,
  which consumes this disposition.
- The question is when a workload moves — use `migration-wave-planning` instead.

## Required inputs

| Input | Source | Required |
| --- | --- | --- |
| Workload inventory with findings | `estate-discovery` | Yes |
| Instance features in use | Evidence | Yes |
| Dependency confirmation status | Evidence | Yes |
| Conversion evidence, for cross-engine moves | SSMA or equivalent | When engine families differ |
| Business intent for the workload | Sponsor | Yes for retire and replace |

## Preconditions

1. The workload has no open blocking finding, unless the disposition under consideration
   is `retain` or `retire`, which do not depend on the missing evidence.
2. Instance features and extensions have been inventoried.
3. The playbook's approved target list has been read.

## Procedure

1. Ask first whether the workload should exist. `retire` and `replace` are real answers,
   and asking last means never asking.
2. Check for operating-system dependencies. Their presence forces infrastructure, which
   makes the disposition `rehost` unless something else changes too.
3. Check whether engine families differ between source and target. If they do, the
   disposition is at least `refactor`, because code must change.
4. Check whether instance-scoped features are in use and whether the target offers them.
   If the target does not, either the application changes — `refactor` — or the target
   does.
5. Where none of the above applies and the engine family is preserved, the disposition is
   `replatform`.
6. Reserve `rearchitect` and `rebuild` for cases where the data model itself changes.
   Neither is a database decision alone, and both need the application owner in the room.
7. Record the disposition with the specific finding that drove it.

## Decision points

| Evidence | Disposition | Note |
| --- | --- | --- |
| No consumers, no business owner claims it | `retire` | Requires sponsor confirmation and a retention decision |
| A product covers the capability | `replace` | Needs a data migration and integration plan of its own |
| Operating-system dependency in use | `rehost` | Patching and availability stay with the customer |
| Same engine family, no instance-scoped blocker | `replatform` | The common case |
| Instance-scoped feature the target lacks | `refactor` | The application changes; get that agreed explicitly |
| Engine family differs | `refactor` at minimum | Conversion evidence required before any target |
| Data model must change | `rearchitect` or `rebuild` | Not a database-only decision |
| Blocking evidence still open | `retain` as interim | Governed in place; not modernization |

## Output contract

Each workload carries a `disposition` on its target decision, plus the finding ids that
justify it. `conversion_required` is true whenever the disposition is `refactor`,
`rearchitect`, or `rebuild` — the model enforces this, so a mismatch fails validation.

## Validation

```bash
dbmodernize recommend-targets --engagement input/engagement.yaml --input input --out out --dry-run
python -m pytest tests/unit/test_scoring.py -q -k "classif or disposition"
```

## Failure and fallback

- **Business intent unknown for a candidate retirement.** Do not retire on technical
  evidence alone. Record the candidate and the question, and leave the workload as is.
- **Cannot tell whether a feature is genuinely required.** Treat it as required and record
  an open question. Assuming a feature is unused is how a cutover discovers otherwise.
- **Disposition disputed.** Record both positions and escalate to the data platform
  architect. The repository does not arbitrate.

## Avoid

- Defaulting every workload to `replatform` because it is the easiest conversation.
- Classifying Arc enablement as anything other than `retain` — the workload has not moved.
- Inferring `rehost` purely from workload size. Size affects sizing, not disposition.
- Recording `retire` without a retention decision for the data.

## Example

A workload uses cross-database queries and scheduled jobs. The application owner confirms
both are load-bearing and cannot change this financial year.

Disposition: `replatform` to an instance-scoped target. Not `refactor`, because the
application does not change — the target was chosen to accommodate it. The alternative,
forcing database scope and rewriting the application, is recorded as the rejected option
with its reason, so the trade is visible later.
