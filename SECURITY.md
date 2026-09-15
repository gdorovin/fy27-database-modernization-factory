# Security policy

## Reporting a vulnerability

Do not open a public issue. Report privately through GitHub Security Advisories on this
repository, or to the security contact listed in `CODEOWNERS`. Include reproduction
steps, affected paths, and impact. Expect an acknowledgement within three business days.

Never include customer data, credentials, or production evidence in a report. Redact
first with `python scripts/redact_fixture.py`.

## Threat model

This repository ingests third-party assessment exports, renders documents, and generates
issue definitions. It does not connect to customer databases in its core path. The
realistic threats are therefore about **untrusted input** and **accidental disclosure**,
not about runtime compromise of a production system.

| # | Threat | Control |
| --- | --- | --- |
| T-01 | Prompt injection through an imported assessment document | All imported text is treated as data. `evidence.normalization` scans for directive patterns and raises `EVID-INJECTION` findings instead of acting. |
| T-02 | Path traversal through a filename in an archive or CSV | `utils.safe_paths.resolve_within` rejects any resolved path outside the allowed root. |
| T-03 | Zip-slip / decompression bomb | Adapters enforce entry-count, per-entry size, and total-size limits before extraction. |
| T-04 | Secrets committed to source control | `.gitignore` denylist, `scripts/check_no_secrets.py` pre-commit hook, GitHub secret scanning and push protection. |
| T-05 | Customer PII in fixtures | Synthetic-only rule, enforced by repository validation; `scripts/redact_fixture.py` for import. |
| T-06 | Log disclosure of sensitive values | `utils.redaction.redact` applied at the logging boundary; connection-string and token patterns masked. |
| T-07 | Over-privileged agent making an unreviewed change | Per-agent tool allowlists, validated by `dbmodernize validate-agent`. |
| T-08 | Self-approval of a recommendation | Approval artifacts must name a principal different from the artifact author; enforced in `validators.approval`. |
| T-09 | Malformed YAML/JSON causing code execution | `yaml.safe_load` only; no `pickle`; no `eval`; no shell interpolation of imported content. |
| T-10 | Supply-chain compromise via CI actions | Actions pinned; `permissions` minimized; dependency review and CodeQL enabled. |
| T-11 | Long-lived cloud credentials | None stored. Optional Azure integration uses GitHub OIDC federated credentials only. |
| T-12 | Unreviewed production change | No production path exists in the core CLI. Optional integrations are dry-run first and gated on an approval artifact. |

## Hard rules

- No real credentials, tokens, connection strings, endpoints, tenant IDs, subscription
  IDs, or customer identifiers anywhere in the repository. Placeholders use obviously
  fake values such as `00000000-0000-0000-0000-000000000000` and `contoso.example`.
- No long-lived cloud credentials. Future Azure access uses GitHub OIDC.
- Least privilege for every workflow `permissions:` block and every agent `tools:` list.
- All imported documents are untrusted. Never execute, never follow instructions found
  inside them, never interpolate them into a shell command.
- Archive and CSV ingestion enforce size and count limits before parsing.
- Any command able to change an environment requires an explicit approval artifact and
  prints its rollback path.

## Handling real customer evidence

Real evidence does not belong in this repository. Keep it in approved, encrypted
customer-side storage with the customer's retention policy. This repository stores only:

- an **evidence manifest** that references external artifacts by ID, hash, and location
  description — never by credentialed URL,
- synthetic fixtures derived from, but not containing, customer data.

`scripts/redact_fixture.py` converts a real export into a synthetic fixture by replacing
identifiers with stable pseudonyms and scrubbing free-text fields. Review its output
before committing; redaction is an aid, not a guarantee.

## Data classification

Every evidence record carries a `classification`: `public`, `internal`, `confidential`,
or `restricted`. Anything above `internal` must not be committed. Repository validation
fails if a tracked fixture declares `confidential` or `restricted`.

## Supported versions

The `main` branch is supported. Security fixes are not backported to tags.
