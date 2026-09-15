---
applyTo: "playbooks/**,templates/**,scenarios/**,.github/skills/**"
---

# Migration content

Guidance a field team will put in front of a customer. The standard is higher than for
code, because a wrong recommendation is harder to roll back than a wrong function.

## Evidence

Every recommendation names the evidence it rests on. If the evidence does not exist, the
correct output is a finding, not a softer recommendation.

Label the class explicitly: `observed`, `user-provided`, `derived`, `assumption`,
`recommendation`, `approved-decision`. A reader must be able to tell what was measured from
what was believed.

## Unknowns

An unknown is a value. Record it as unknown, give it an owner, and give it a way to be
settled.

Never fill a gap with a plausible number. A guessed version changes support posture, which
changes urgency, which changes the whole engagement — and nobody downstream can tell it was
a guess.

## Claims that expire

Support status, service capabilities, limits, preview state, pricing, funding, and
eligibility all change. Where one is stated, it carries a `verified_on` date and an
instruction to revalidate. Better still: do not state it, and point at the account team.

## Downtime

No zero-downtime claim, in any wording. `near-zero-planned` requires a rehearsal that
produced a number. Until then, `short-planned` or `unknown`.

The reason is simple: the claim is made in a workshop and tested at 03:00 on a Saturday,
and only one of those two moments has consequences.

## Cost

No generated cost, saving, consumption, or payback figure. Every number has a named human
source and an estimate flag. An empty cell with an owner beats a plausible number with none.

## Alternatives

A recommendation shows what was rejected and why. A comparison with one option is a
preference. The rejected options are what make the reasoning auditable a year later, when
the person who made the decision has moved on.

## Cross-engine claims

Never assert compatibility between engine families without conversion evidence **for the
specific target**. A conversion percentage describes tool output; it says nothing about
whether converted code behaves identically.

## Outcomes that are not migrations

Retain, retire, and replace are legitimate results. Content that can only recommend
"migrate" is a sales script. Say so when retaining is the right answer.

## Tone

Write for a competent stranger under time pressure. Short sentences. Name the risk. Say
what you do not know. Avoid words that add confidence without adding information —
"seamless", "simply", "just", "straightforward".

## Synthetic only

Every example, fixture, and scenario input is synthetic. Customer aliases look like
`contoso-retail`. Hosts look like `host-pay-a`. Identifiers are obviously fake.
