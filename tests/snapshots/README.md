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

Reserved for snapshots that are not tied to a single scenario — for example, a future
comparison of rendering across multiple playbooks, where the interesting variable is the
playbook rather than the estate.

Nothing needs it yet. It is kept so the convention has an obvious home when it does, rather
than being invented under time pressure.
