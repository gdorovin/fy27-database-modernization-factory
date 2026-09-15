---
name: business-case
description: Assemble an outcome-oriented business case from supplied costs, risks, benefits, and timelines, with every figure attributed to a named source and every gap left visibly empty.
---

# Business case

Connects technical evidence to the decision a sponsor actually makes. Its integrity rests
on one rule: no number appears here unless a human supplied it and can be named as its
source.

## Invoke when

- Target decisions exist and a sponsor needs a funding or commitment decision.
- A renewal, refresh, or audit deadline needs a case behind it.
- An existing case needs updating because evidence changed.

## Do not invoke when

- Targets have not been recommended yet — use `azure-target-recommendation` instead.
- The audience is technical and wants the reasoning — defer to the target decision
  document, which already contains it.
- A short summary of approved artifacts is wanted — use `executive-brief` instead.

## Required inputs

| Input | Source | Required |
| --- | --- | --- |
| Current licensing, infrastructure, support, and operational costs | Customer finance | Yes, or left empty |
| Target consumption estimate | Account team, with a stated basis | No |
| Migration and remediation effort | Delivery lead | No |
| Risk exposure being bought down | Security and operations owners | Yes |
| Renewal or support-expiry date | Engagement artifact | Where applicable |
| Success measures and baselines | Engagement artifact | Yes |

## Preconditions

1. Target decisions exist, so the target-state shape is known.
2. Sizing evidence is marked measured or estimated. Estimated sizing cannot support a
   consumption commitment.
3. The sponsor understands that empty cells are deliberate.

## Procedure

1. Start from the outcome in the customer's words, taken verbatim from the engagement.
2. State why now: the trigger, and what changes if nothing happens before it lands.
3. Fill the current-state cost table from supplied figures. Name the source of each. Leave
   a row empty if nobody has supplied it, and record who owns getting it.
4. Fill the target-state table the same way. Where consumption rests on estimated sizing,
   say so next to the figure rather than in a footnote.
5. Record risk being bought down: unsupported-version exposure, audit findings, hardware
   failure, recovery time beyond tolerance. Quantified where the customer can quantify it,
   described where they cannot.
6. Record value that is not a cost line: delivery speed, operational hours returned,
   capability the estate cannot support today.
7. Record assumptions with owners and how each gets settled.
8. State plainly what the case does **not** claim.

## Decision points

| Question | Choose | Because |
| --- | --- | --- |
| No current-state cost supplied | Leave empty, assign an owner | An invented baseline becomes a fabricated saving |
| Sizing is estimated | Present a range with the basis, no commitment | An estimate cannot carry a commitment |
| Customer asks about funding or offers | Refer to the account team | These change; a repository cannot be current on them |
| Risk cannot be quantified | Describe exposure and likelihood | An unquantified risk is still a real one |
| Sponsor wants one number | Give the number and its assumptions together | A number without its assumptions travels badly |

## Output contract

A document from `templates/business-case.md` where every figure has a named source and an
estimate flag, every gap has an owner, and the "what this case does not claim" section is
present and specific.

Cost inputs that belong to a target decision are recorded as `cost_inputs` on that
artifact, so the figure and the decision it supports stay together.

## Validation

- Every populated cell names a source.
- Every empty cell names an owner.
- No funding programme, commercial offer, or eligibility is asserted.
- No saving is claimed against a baseline marked unknown.
- No downtime figure appears without a measured rehearsal behind it.

## Failure and fallback

- **Finance will not share costs.** Build the case on risk and capability alone, and say
  that the cost comparison is unavailable. That is a weaker case, honestly labelled.
- **Sponsor asks for a saving figure with no baseline.** Explain that the figure would be
  unverifiable in twelve months, and offer to help capture the baseline first.
- **Pressure to include a commercial offer.** Refer to the account team and record that
  the case excludes commercial terms.

## Avoid

- Generating any cost, saving, or consumption figure.
- Asserting funding eligibility or programme availability.
- Claiming a percentage improvement against an unmeasured baseline.
- Presenting a range as a forecast.
- Burying the assumptions that the headline number depends on.

## Example

The sponsor asks for the saving. Licensing and infrastructure costs have not been supplied.

The case ships with those rows empty, each carrying the finance owner's name, and a
headline built on risk avoided and operational hours returned. When the figures arrive the
case is updated. Nobody has to retract anything, because nothing was invented.
