# Incident response

Two kinds of incident, with very different urgency.

## Kind one: the toolkit misbehaves

Low stakes. Nothing is running in production, nothing holds a credential, and the worst case
is a wrong document.

1. Capture the exact command, the exit code, and the finding — rule id and artifact path.
2. Reduce it to a synthetic reproduction. Never attach a customer export; use
   `scripts/redact_fixture.py`.
3. Open a bug using the template.
4. If a *generated artifact* is wrong, check whether any engagement has acted on it.

That last step is the one people skip. A scoring bug that produced three wrong target
recommendations is a documentation-and-communication problem before it is a code problem.

## Kind two: a real migration went wrong

High stakes, and this toolkit is not the responder. The rollback plan is.

What the toolkit contributes, in order:

1. **`rollback-plan-<n>.md`** — triggers, decision window, method, evidence preservation,
   data reconciliation obligation. Read it before the window, not during.
2. **Preserve evidence first.** Logs, metrics, failed test output, replication state.
   Rolling back without evidence guarantees the next attempt fails identically.
3. **Record honestly.** A validation report with a `no-go` outcome, the rollback reason, and
   corrective issue ids.
4. **Never describe it as a success.**

## The data question

Rollback is not complete when the application is serving again. It is complete when writes
accepted by the target during the window have been identified and either replayed or formally
written off with the business owner.

The gap between those two moments is where quiet data loss lives, and it is usually
discovered by a customer weeks later.

## If a boundary was crossed

Someone deployed, cut over, or deleted something using output from this repository, without
the required approvals.

That is a governance incident, not a tooling one. It needs the security owner and the
delivery lead, and it needs an honest answer to: was the boundary unclear, or was it clear
and inconvenient? Those have different fixes, and only one of them is a documentation change.

## If customer data was committed

1. Do not open a public issue.
2. Notify the security owner immediately, per [SECURITY.md](../../SECURITY.md).
3. Treat the history as compromised. Removing the file does not remove it from Git.
4. Rotate anything credential-like, on the assumption it is public.
5. Afterwards: which control should have caught this, and why did it not?

The layers are `.gitignore`, the pre-commit hook, repository validation, and GitHub push
protection. If all four missed it, one of them has a gap worth closing.

## Prompt injection found in a real import

1. Do not act on the text. The finding exists precisely so nobody does.
2. Establish provenance: who produced the export, and on what system.
3. If it was not introduced accidentally, this is a security incident for the customer, not
   just a data-quality note.
4. Keep the evidence record with its finding attached; do not clean it up.

## Blameless review

For anything above the first category, hold one. The useful questions:

- What did the person doing the work believe at the time?
- Which control was supposed to catch this?
- Why did the control not fire, or not get noticed?
- What is the smallest change that would have made the outcome different?

"Be more careful" is not an answer. If it were, the control would not have been needed.
