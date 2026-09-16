# Snapshots

Snapshot expectations for generated documents live with the scenario that produces them, in
`scenarios/<nn>-<name>/expected/`, not here.

That is deliberate. A snapshot separated from its input is hard to reason about: you can see
that something changed, but not what produced it. Keeping the two together means a reviewer
reads the diff alongside the fixture that caused it.

## Regenerating

```bash
dbmodernize validate-scenario scenarios --update
```

Then read every line of the diff. The CLI emits a warning when you do this, because
regenerating to make a failure disappear defeats the purpose of having a snapshot at all.

The scenario acceptance criteria are the backstop: they assert the behaviour the snapshot is
supposed to encode, so a silently regenerated snapshot still fails.

## Why this directory exists

For comparisons that are not tied to a single scenario. Everything under `scenarios/` holds
the playbook constant and varies the estate; `test_cross_playbook.py` is the other axis —
one estate, four playbooks.

It exists because "configuration-driven" was a claim the repository made about itself in
several places and proved nowhere. Validating the example playbooks showed only that they
parse. It did not show that swapping one changes a single decision, which is the entire
premise.

Writing it found something worth knowing: the *set* of targets considered is identical
across playbooks, because `targets.md` promises a prohibited target is still compared and
rejected with a citation rather than dropped. A playbook's effect shows up in the verdicts,
never in the membership. The obvious assertion — that a narrower playbook considers fewer
options — looks stronger and is simply wrong.
