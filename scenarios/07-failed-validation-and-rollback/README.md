# Scenario 07 — Failed validation and rollback

**Prevents:** describing a rolled-back attempt as a partial success.

This is the most important scenario in the repository. Everything else proves the factory
can produce good work. This one proves it will report bad news accurately, in a room that
would rather hear something else.

## The situation

A billing platform on hardware past warranty. The overnight run is the binding constraint:
if it does not finish before the business day, invoices are late and the finance close slips.

The migration ran. Technically, it completed. Then:

| Check | Result | Detail |
| --- | --- | --- |
| Schema reconciliation | pass | 1,412 objects, zero differences |
| Connectivity | pass | 6 of 6 consumers connected |
| Security configuration | pass | Zero deviations |
| Backup restore | pass | Completed in 38 minutes |
| **Billing run performance** | **fail** | 5 h 25 m against a 3 h 40 m baseline, finishing at 06:25 past a 06:00 constraint |
| **Invoice dispatch integration** | **fail** | 13 of 14; the acknowledgement callback timed out |
| **Billing history reconciliation** | **not run** | 22 of 38 tables compared when the decision window closed |
| Generated procedure suite | pass | 412 of 412 matched |
| Business acceptance | not run | Never reached |

## What the factory does, and why

**The outcome is `no-go`.** A blocking failure forces it. The model refuses to serialize a
report claiming otherwise, so this is not a matter of discipline on the night.

**Partial reconciliation is `not-run`, not a partial pass.** Twenty-two of thirty-eight
tables is not reconciliation. The report lists it under blocking checks that did not run, and
states that a check which did not run is not a pass.

**The generated suite does not carry the verdict.** Four hundred and twelve auto-generated
comparisons passed cleanly. They appear in the report marked as a generated test, described
as supporting evidence only, and marked non-blocking. This is the most tempting number in
the whole report — it is large, it is green, and it is not proof.

**Rollback is explained, not just recorded.** The report names the reason. The rollback plan
requires evidence to be captured *first*, so the next attempt starts from data rather than
from recollection, and requires the in-window writes to be reconciled before rollback is
considered complete.

**Three corrective issues exist, each with an owner.** A failure with no follow-up work is
not a result.

**Success language is forbidden.** The report may not contain "successfully" or "migration
succeeded", and it must contain the sentence stating that nothing in it should be read as a
partial success. Those are acceptance criteria, not style guidance: the phrase "completed
successfully with some issues" is how a rolled-back migration enters a status report.

**`render-report` exits non-zero.** A pipeline cannot walk past this by accident.

## What would break this

- Any outcome other than `no-go`.
- Counting the un-run reconciliation as a pass.
- Letting the generated suite justify a `go`.
- Success language anywhere in the report.
- A no-go with no corrective issues.
