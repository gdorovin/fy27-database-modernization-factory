---
applyTo: "docs/**,README.md,*.md"
---

# Documentation

## Audience

A competent stranger, under time pressure, who has not read the rest. Assume intelligence,
assume no context.

## Structure

- Lead with what the reader needs to decide or do.
- Tables for anything comparative. Prose for reasoning.
- Headings a reader can scan and land in the right place from.
- Short sentences. One idea each.

## Say why, not just what

The implementation shows what. Documentation earns its place by explaining why — the
constraint that made the obvious approach wrong, the failure that motivated a rule.

Prefer *"A pilot that large de-risks nothing"* over *"Pilot waves are limited to two
workloads."* The second is already in the code; the first is why.

## Claims that expire

Product support, service limits, preview status, pricing, funding, and eligibility all
change. Any page stating one carries a `verified_on` date, and repository validation
enforces this for `docs/guidance/`.

Better: do not state it. Point at the account team or the current product documentation.

## Diagrams

- Mermaid, in the Markdown, source-controlled.
- A diagram earns its place by showing a relationship prose cannot: a cycle, a fan-out, a
  gate.
- Keep them small. A diagram with thirty nodes is a wall, not an explanation.
- Update the diagram in the same change as the implementation. A stale diagram is worse
  than none, because it is believed.

## Commands

- Every command shown must work. Repository validation checks that every
  `dbmodernize <command>` in a README code span is real.
- Show the command and what it prints, not a claim about what it does.
- Prefer `make` targets so documentation and CI cannot drift apart.

## Links

- Relative links within the repository.
- No invented URLs. If a link target does not exist yet, say so in the text rather than
  linking to a hopeful path.

## Words to avoid

"Seamless", "simply", "just", "easy", "straightforward", "of course". They add confidence
without adding information, and they are usually written by someone who already knows the
answer.

## Tone on limitations

State them plainly and early. An accelerator that is vague about its limits is more
dangerous than one with fewer features, because the limits are discovered at the worst
moment.
