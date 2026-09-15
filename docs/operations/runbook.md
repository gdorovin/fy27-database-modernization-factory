# Runbook

Day-to-day operation of the toolkit. Everything here is local and offline.

## Setup

```bash
make install-dev
pre-commit install
make gate
```

Or open the folder in VS Code and choose **Reopen in Container**.

## A full engagement

```bash
# 1. Scaffold
dbmodernize init --engagement-id acme-fy27 --out engagements

# 2. Fill in engagements/acme-fy27/input/engagement.yaml, then add exports to input/

# 3. Normalize, and read the summary line
dbmodernize normalize-evidence \
  --engagement engagements/acme-fy27/input/engagement.yaml \
  --input engagements/acme-fy27/input \
  --out engagements/acme-fy27/out

# 4. Assess
dbmodernize assess \
  --engagement engagements/acme-fy27/input/engagement.yaml \
  --input engagements/acme-fy27/input \
  --out engagements/acme-fy27/out --force

# 5. Compare targets
dbmodernize recommend-targets ...

# 6. Plan waves
dbmodernize plan-waves ...

# 7. Render every document
dbmodernize render-plan ...

# 8. Generate issue definitions
dbmodernize generate-issues ...
```

`engagements/` and `out/` are in `.gitignore`. Engagement artifacts do not belong in this
repository.

## Exit codes

Contractual, and asserted in tests. Script against them.

| Code | Means | Usual cause |
| --- | --- | --- |
| 0 | Success | |
| 1 | Validation failed | A finding, or a no-go outcome |
| 2 | Usage error | Bad arguments |
| 3 | Input not found | Wrong path |
| 4 | Output exists | Re-run with `--force` |
| 5 | Policy violation | Path traversal, archive limit |
| 6 | Safety refusal | A documented boundary was crossed |
| 70 | Internal error | A bug; please report it |

## Common situations

**"Output exists."** Deliberate. Add `--force`, or choose a different `--out`.

**"No supported evidence files found."** Nothing in the input directory matched an adapter.
Check file extensions, and for JSON check the document shape — three adapters read `.json`
and discriminate on content.

**Unresolved conflicts reported.** Two sources disagree on a decision-critical attribute.
This is not a bug. The database owner reconciles them and the decision gets recorded.

**A workload got no destination.** It has a blocking finding. Read the assessment summary;
the blocking issues section is the discovery backlog.

**Records flagged for directive-like content.** An import contains text shaped like an
instruction. It was treated as data. Review where the export came from before trusting it.

**`render-report` exited 1.** The outcome is `no-go`. That is the command working.

## Regenerating scenario expectations

```bash
dbmodernize validate-scenario scenarios --update
```

Then read every line of the diff. Regenerating to silence a failure defeats the purpose, and
the acceptance criteria will usually still fail if the behaviour genuinely regressed.

## Verifying the repository

```bash
make gate                 # everything CI enforces
make validate             # the deterministic validators only
dbmodernize validate-repo --json    # machine-readable
```

## Adding an adapter

1. Subclass `EvidenceAdapter` in `src/dbmodernize/adapters/`.
2. Build records through `self._record` so injection scanning happens automatically.
3. Override `supports()` to discriminate on document shape if the extension is shared.
4. Register it in `default_registry()`.
5. Add a synthetic fixture and a test.

## Adding a playbook

Copy `playbooks/default/`, change what the customer's context demands, bump the version,
validate. See [playbooks/README.md](../../playbooks/README.md).

## What this toolkit will not do

Migrate, deploy, cut over, roll back, delete anything, create live GitHub issues, or invent a
number. If you need one of those, a human does it with the plan in hand.
