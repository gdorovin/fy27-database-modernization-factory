# Playbooks

A playbook is the enterprise decision and governance contract. It records **decisions** —
what is approved, what is prohibited, what must hold — and nothing else.

Procedures live in Agent Skills. That split matters: copying a procedure into a playbook
makes it impossible to improve the procedure without a governance review, which is the
wrong trade and quietly stops people improving it at all.

## Structure

Exactly three files. Not two, not four.

| File | Records | Example content |
| --- | --- | --- |
| `charter.md` | Scope, outcomes, principles, stakeholders, decision rights | "No self-approval. Cutover needs all five owner roles." |
| `targets.md` | Approved, conditional, and prohibited targets | "Hyperscale is conditional on measured size or growth." |
| `policies.md` | Policies and exceptions | "`SEC-001` prohibits public database endpoints." |

`charter.md` must declare `version: x.y.z`. Generated artifacts record the playbook path,
version, and applied policy ids, so an unversioned playbook breaks traceability.

## Available playbooks

| Playbook | Use when |
| --- | --- |
| `default/` | The baseline. Start here and copy it. |
| `examples/regulated-enterprise/` | An estate under external supervision. Narrower target set, stricter evidence retention, residency as a hard block. |
| `examples/renewal-led-sql/` | A fixed external date. Wider target set, explicit rules about what may and may not move under time pressure. |
| `examples/ai-ready-data/` | An intelligent scenario is the stated destination. Adds data ownership, quality, and deletion-propagation controls. |

The examples are working playbooks, not illustrations. They validate in CI, and the
differences between them are the interesting part — each shows what a real constraint does
to a governance contract.

## Policy format

```markdown
| ID | Category | Subject | Directive | Requirement | Applies to |
| --- | --- | --- | --- | --- | --- |
| SEC-001 | security | network.public-endpoint | prohibited | Database endpoints are not reachable from the public internet. | all |
```

| Column | Rules |
| --- | --- |
| `ID` | Two to four uppercase letters, a hyphen, three digits. Unique within the playbook. |
| `Category` | One of the categories in `policies/models.py`. |
| `Subject` | A stable dotted key, for example `network.public-endpoint`. |
| `Directive` | `required`, `prohibited`, `recommended`, or `discouraged`. |
| `Requirement` | What must hold, in a sentence someone can check. |
| `Applies to` | Scope key: `all`, an environment, a platform, or a target code. |

Two policies sharing a subject **and** scope with `required` and `prohibited` are a
conflict, and a conflict fails validation. The repository will not choose between two rules
the organisation has not reconciled.

## Exceptions

```markdown
| ID | Policy ID | Scope | Justification | Owner role | Approver role | Approver principal | Compensating controls | Granted on | Expires on | Review on |
```

Every column is mandatory. An exception without an expiry becomes permanent by default, and
an expired exception **fails validation** rather than lapsing quietly. That is the control
working, not the build being awkward.

Keep them short. Ninety days is a reasonable ceiling. The requesting role may not be the
approving role.

## Unmapped content

Anything outside the tables is retained verbatim in an "Extended" section and reported as a
warning saying enforcement over it is best-effort. Nothing is dropped, and nobody is misled
into thinking prose is enforced.

Use a `## Notes` heading for deliberate free-text context, so the warning is expected rather
than alarming.

## Validating

```bash
dbmodernize validate-playbook playbooks/default
dbmodernize validate-playbook playbooks/examples/regulated-enterprise --as-of 2026-09-15
```

Validation fails on: a missing file, a missing version, a missing charter section,
duplicate policy ids, contradictory directives, a governance category with no policy at all,
every target prohibited, an incomplete exception, an exception for an unknown policy, and an
expired exception.

## Creating one

1. Copy `default/` to `playbooks/<name>/`.
2. Change what the customer's context actually demands. Resist changing more: a playbook
   that differs everywhere is a fork, and forks stop receiving improvements.
3. Bump the version in `charter.md`.
4. Run the validator.
5. Add it to the table above, saying when to use it.

Playbook changes need architect and security review per `CODEOWNERS`, a scenario test, and
a note in `CHANGELOG.md`.
