# Policy management

How playbook policies are written, changed, and excepted. Format details are in
[playbooks/README.md](../../playbooks/README.md); this page is about the process and the
reasoning.

## What belongs in a playbook

**Decisions.** What is approved, what is prohibited, what must hold.

Not procedures. Those live in Agent Skills, and the reason is practical: putting a procedure
in a playbook makes improving it a governance event, which in practice means it stops being
improved. The team routes around it instead, which is worse than either option.

## Writing a policy

```markdown
| SEC-001 | security | network.public-endpoint | prohibited | Database endpoints are not reachable from the public internet. Access is over private connectivity only. | all |
```

| Column | Guidance |
| --- | --- |
| ID | `XX-000` to `XXXX-000`. Unique. Artifacts cite it, so it is a permanent identifier. |
| Category | Must be one the model knows. |
| Subject | A stable dotted key. This is what conflict detection compares. |
| Directive | `required`, `prohibited`, `recommended`, `discouraged`. |
| Requirement | A sentence someone can check. Not an aspiration. |
| Applies to | `all`, an environment, a platform, or a target code. |

The subject key deserves care. It is how the repository knows that two policies are about the
same thing, so `network.public-endpoint` in one playbook and `networking.public_access` in
another are, as far as validation is concerned, unrelated.

## Conflicts

Two policies sharing a subject **and** scope, one `required` and one `prohibited`, fail
validation.

The repository will not choose. Choosing would mean silently preferring one part of the
organisation's stated position over another, and the disagreement is the finding. Different
scopes are fine — production and development can legitimately differ.

`recommended` against `discouraged` is a warning: less serious, but still a sign that two
people wrote policy without talking.

## Coverage

Seven categories must have at least one policy: security, identity, networking, data,
observability, availability, validation.

Silence is not a decision. "We have no additional requirement" is a perfectly good policy,
and writing it down means the next person knows it was considered rather than forgotten.

## Changing a policy

1. Open an issue explaining what goes wrong today.
2. Edit the playbook on a branch. Direct pushes to `main` are blocked for playbook files.
3. Bump the version in `charter.md`.
4. `dbmodernize validate-playbook playbooks/<name>`.
5. Run the scenarios — a policy change can alter generated plans.
6. Note it in `CHANGELOG.md`.
7. Architect **and** security review per `CODEOWNERS`.

Generated artifacts record the playbook version and the policy ids they applied, so a plan
produced under the old version remains explicable. Do not retrofit.

## Exceptions

An exception is a **time-boxed, compensated deviation**. Every field is mandatory:

scope, justification, owner role, approver role, approver principal, compensating controls,
granted date, expiry date, review date.

An exception without an expiry becomes permanent by default. An expired exception **fails
validation** rather than lapsing quietly — that is the control working, not the build being
awkward.

Ninety days is the ceiling, and it is enforced: an exception running longer than that from
its grant date raises `PLAYBOOK-EXCEPTION-HORIZON`. The check measures grant date to expiry
rather than expiry against today, so "is this too long?" has the same answer whenever it is
asked. It warns rather than fails, because some deviations genuinely outlast a quarter and
the useful thing is to make that visible rather than impossible. An exception long enough to
outlive the people who agreed to it is a policy change wearing an exception's clothes.

The requesting role may not be the approving role.

A compensating control is something that reduces the risk. "Accepted by the business" is not
a compensating control; it is a decision to carry the risk unchanged.

## Why the baseline playbook grants none

`playbooks/default/policies.md` has an empty exceptions table, and should stay that way. An
exception names a system, an owner, and an end date, none of which exist until an engagement
does. One shipped in a reusable baseline is either meaningless or silently inherited by
everyone who copies the file — and it forces a choice between modelling a bad horizon and
having the baseline expire on a fixed date. The format is documented there in a fenced
block, which is not parsed and therefore cannot be in force by accident.

## Requesting one

Use the `policy-exception` issue template. It asks for every mandatory field, including the
two people most often forget: compensating controls, and a review date before expiry.

## Creating a playbook

Copy `playbooks/default/`, change what the customer's context demands, and resist changing
more. A playbook that differs everywhere is a fork, and forks stop receiving improvements —
six months later the customer is running guidance that has quietly fallen behind.

The three examples show what a real constraint does to a governance contract:
regulated-enterprise narrows the target set and hardens residency; renewal-led-sql widens the
targets and hardens what may move under time pressure; ai-ready-data adds data ownership and
deletion-propagation controls.

## Extended content

Anything outside the tables is retained verbatim in an "Extended" section, with a warning
that enforcement over it is best-effort.

Nothing is dropped, and nobody is misled into thinking prose is enforced. Use a `## Notes`
heading for deliberate free-text context so the warning is expected.
