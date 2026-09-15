---
name: engagement-intake
description: Capture the customer outcome, trigger, sponsor, timeline, renewal date, scope, constraints, stakeholders, and success measures into an engagement artifact. Use at the very start, before any estate data is gathered.
---

# Engagement intake

The first artifact of an engagement. Everything downstream references its `engagement_id`,
and everything downstream is judged against the outcomes recorded here.

## Invoke when

- A new modernization engagement is starting and no `engagement.yaml` exists yet.
- An existing engagement's outcomes, sponsor, scope, or timeline have materially changed.
- A previous attempt stalled and the outcome needs restating before work resumes.

## Do not invoke when

- Estate data needs collecting or normalizing — use `estate-discovery` instead.
- The engagement artifact already exists and only evidence is being added — defer to
  `evidence-normalization`.
- The customer is asking for a target recommendation — use `azure-target-recommendation`
  instead, and only after assessment.

## Required inputs

| Input | Source | Required |
| --- | --- | --- |
| Desired business outcomes | Sponsor conversation | Yes |
| Primary trigger | Sponsor or account team | Yes |
| Business context | Sponsor conversation | Yes |
| Scope, in and out | Sponsor and application owners | Yes |
| Renewal or support expiry date | Account team | When the trigger is a renewal |
| Stakeholders and decision rights | Engagement lead | Yes |
| Constraints | Security, operations, legal | Yes |
| Success measures and baselines | Sponsor | Yes, baselines may be unknown |

## Preconditions

1. A playbook exists at the path that will be recorded in `playbook`.
2. Pseudonyms are agreed for the customer and every stakeholder. Real names, real
   customer names, and email addresses never enter the artifact.
3. The `as_of` date is the date the state was captured, not today's date at render time.

## Procedure

1. Ask for outcomes in the customer's words. Write down what they said, not a product
   translation of it.
2. Record the primary trigger and any secondary triggers. All triggers lead into the same
   journey; they differ in urgency and in who cares.
3. Capture the renewal or support-expiry date if one exists. If the customer does not
   know it, record a blocking open question rather than an estimate.
4. Record scope in and out. Out-of-scope entries carry a reason.
5. Capture constraints with a source and a `hard` flag. A soft constraint is a preference;
   labelling a preference as hard removes a trade that might have been available.
6. Record stakeholders by role and pseudonym, with decision rights.
7. Record success measures. For each, state whether a baseline exists. If it does not,
   set `baseline_known: false` and say so out loud — a measure with no baseline cannot
   later prove improvement.
8. Configure the cadence milestones against the customer's own dates.
9. Validate against `contracts/engagement.schema.json`.

## Decision points

| Question | Choose | Because |
| --- | --- | --- |
| Customer names a product as the outcome | Record the business result behind it | Naming a product as an outcome pre-decides the target |
| Renewal date unknown | Blocking open question | The date anchors the whole cadence |
| Baseline for a measure unknown | `baseline_known: false` | An invented baseline manufactures a saving later |
| Stakeholder unwilling to own a decision | Record the gap as a risk | An unowned decision stalls the programme at the gate |
| Scope is "everything" | Push for a first slice, record the rest | An unbounded scope is how the last attempt stalled |

## Output contract

One artifact validating against `contracts/engagement.schema.json`, containing at
minimum: `engagement_id`, `as_of`, `customer_alias`, `primary_trigger`,
`desired_outcomes` (at least one), `business_context`, `scope`, and `playbook`.

Unknowns appear in `open_questions` with an owner. Gaps filled in to proceed appear in
`assumptions` with an owner and a validation step.

## Validation

```bash
dbmodernize validate-repo
python -c "from dbmodernize.pipeline import load_engagement; from pathlib import Path; load_engagement(Path('input/engagement.yaml'))"
```

The model rejects an outcome that starts with a product name, and rejects a renewal
trigger with no renewal date.

## Failure and fallback

- **Sponsor unavailable.** Capture what is known, mark every unverified field as an
  assumption with the sponsor as owner, and set `confidence: low`. Do not proceed to
  target selection on an unconfirmed intake.
- **Stakeholders disagree on scope.** Record both positions as an open question and stop.
  Do not average them.
- **Schema validation fails.** Fix the artifact. Do not relax the schema to accommodate a
  missing answer; the missing answer is the finding.

## Avoid

- Writing a product name into `desired_outcomes`.
- Guessing a renewal date, a workload count, or a baseline.
- Recording real customer names, personal names, or email addresses.
- Treating an estimated workload count as fact — set `estimated_count_is_assumption`.
- Promising an AI, analytics, or Fabric outcome at intake. Readiness for those is assessed
  separately and is conditional.

## Example

> Sponsor: "We need to be on Azure SQL by the renewal."

Recorded outcome: *"Remove unsupported database versions from the payment path before the
next audit cycle."* Trigger: `license-or-ea-renewal`. Renewal date: recorded.

The product the sponsor named is not written down as the outcome. It is a hypothesis that
`azure-target-recommendation` will test against evidence, and it may not survive.
