---
name: executive-brief
description: Condense approved technical artifacts into a short outcome-focused summary for a sponsor, introducing no new fact and stating plainly what has not been measured.
---

# Executive brief

Compresses the engagement for someone with ten minutes and a budget decision. It adds
nothing. Every sentence traces to an artifact that already exists.

## Invoke when

- A sponsor or steering group needs the current position.
- A decision gate is approaching and the trade-offs need stating plainly.
- An engagement is being handed to a different sponsor.

## Do not invoke when

- The reasoning behind a target is wanted — defer to the target decision document, which
  already carries it.
- Cost detail is wanted — use `business-case` instead.
- The reader is technical and wants the findings — use the assessment summary instead.

## Required inputs

| Input | Source | Required |
| --- | --- | --- |
| Engagement artifact, with outcomes | `engagement-intake` | Yes |
| Workload inventory and completeness | `estate-discovery` | Yes |
| Target decisions | `azure-target-recommendation` | Yes |
| Wave plan | `migration-wave-planning` | Yes |
| Risk register | Assessment | Yes |
| Business case, if one exists | `business-case` | No |

## Preconditions

1. The underlying artifacts validate. A brief over invalid artifacts is a confident summary
   of something unreliable.
2. Every claim to be made exists in an artifact already.
3. Anything unmeasured is known to be unmeasured, so it can be said rather than smoothed
   over.

## Procedure

1. Open with the outcome in the customer's own words, taken verbatim from the engagement.
2. State where the work stands: workloads assessed, targets recommended, workloads awaiting
   evidence, waves planned, inventory completeness.
3. If workloads are awaiting evidence, say so early and explain that it is a deliberate
   stop rather than a delay. A sponsor who learns this late concludes the team was slow;
   one who learns it early concludes the team was careful.
4. Show the destination mix. Different destinations across an estate is a sign of care, not
   inconsistency — say that if the mix looks untidy.
5. Show the sequence, and which wave is the pilot.
6. Show the top open risks with owners and mitigations.
7. List the decisions needed from the sponsor. Be specific: naming approvers, agreeing a
   downtime budget, funding evidence gathering.
8. Close with what the brief does **not** claim, and why. Where a figure is absent, say it
   has not been measured.

## Decision points

| Question | Choose | Because |
| --- | --- | --- |
| Sponsor wants one headline number | Give the number with its assumptions attached | A number without assumptions travels badly |
| Progress looks slow | Show what was prevented | A blocked recommendation is work, not delay |
| A risk is politically awkward | Include it with its owner | The brief is where it can still be cheap |
| Estate mix looks inconsistent | Explain why per-workload differs | One-size-fits-all is the thing to avoid |
| Something has not been measured | Say so | Silence reads as confidence |

## Output contract

A document from `templates/executive-brief.md` containing the outcome, position, mix,
sequence, risks, decisions needed, and an explicit statement of what is not claimed.

It introduces no fact absent from the underlying artifacts. If a sentence cannot be traced,
it does not belong.

## Validation

```bash
dbmodernize render-plan --engagement input/engagement.yaml --input input --out out
dbmodernize validate-scenario scenarios
```

Cross-check every number in the brief against the artifact it came from.

## Failure and fallback

- **Underlying artifacts are incomplete.** Brief on what exists and state the gap. Do not
  interpolate across it.
- **Sponsor asks a question the artifacts cannot answer.** Say so, and name who would need
  to answer it. Guessing in a brief is how an invented figure becomes a commitment.
- **Pressure to remove a risk.** Keep it, and offer to move it lower with its mitigation
  visible.

## Avoid

- Introducing any fact not already in an artifact.
- Rounding an estimate into something that reads as measured.
- Claiming an AI, analytics, or Fabric outcome. Readiness is separate and conditional.
- Presenting a target as decided when its status is `recommended`.
- Omitting the workloads that are awaiting evidence.

## Example

Twelve workloads assessed, nine with recommendations, three awaiting evidence, two waves
planned, inventory completeness low.

The brief leads with the low completeness, because it is the fact that changes what the
sponsor should do next — fund the evidence gathering — and it is the one most likely to be
softened into invisibility if nobody insists on it.
