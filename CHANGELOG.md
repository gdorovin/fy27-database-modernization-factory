# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Unrecognised input is reported instead of dropped, in every adapter.** Each adapter
  records fields it does not read as `unmapped_fields`, and a `r-unmapped-input`
  assessment finding surfaces them. Discarding `Recovery Point Objective (min)` in silence
  made the assessment state that no recovery objective was given — a claim about the
  customer's estate that was really a fact about our column map, and indistinguishable
  from the real thing downstream. The CSV adapter also normalizes headers before lookup,
  so `Data Size (GB)`, `data-size-gb`, and `DATA_SIZE_GB` now reach the same attribute.
  JSON adapters name the nesting level (`performance.queueDepth`) so the field can be
  found in the source document. A parametrized test over the registry means a sixth
  adapter cannot skip the behaviour.
- **Cross-playbook tests** (`tests/snapshots/test_cross_playbook.py`). One estate, four
  playbooks. "Configuration-driven" was asserted in several documents and proved nowhere;
  validating the example playbooks showed only that they parse.
- **Executable infrastructure tests** (`tests/infra/`). Three security properties that
  `infra/tests/README.md` listed as enforced by "Review" — no credential parameter, no
  defaulted region, public access decided and decided closed — are now assertions, along
  with TLS floor, GUID literals, `main.bicep` composing rather than declaring, and module
  reachability.
- **CODEOWNERS validation.** Placeholder teams raise a warning on every `validate-repo`
  run rather than sitting in a document nobody re-reads, and the two-owner rule on
  governance paths is now an error rather than a convention.
- **`PLAYBOOK-EXCEPTION-HORIZON`.** Warns on an exception granted for more than 90 days,
  measured grant-to-expiry rather than against today, so the judgement does not change
  with the calendar.
- **Scale tests** (`tests/scale/`, marked `slow`). `MAX_RECORDS_PER_FILE` and
  `MAX_IMPORT_BYTES` were stated in comments and exercised nowhere. An estate just under
  the limit works; one above it is refused with a message that says what to do next.
- **`.gitattributes`.** LF is enforced for every text file. Generated documents are
  compared byte for byte, so a CRLF checkout would have passed on Linux and failed on
  Windows — a failure that depends on who ran it.

### Changed

- **The default playbook grants no exceptions.** An exception names a system, an owner,
  and an end date, none of which exist until an engagement does. Shipping one forced a
  choice between modelling a five-year horizon and having the baseline expire on a fixed
  date. The format is now documented in a fenced block, which is not parsed and so cannot
  be in force by accident.
- The pattern-bearing file allowlist is defined once in `validators/repository.py` and
  imported by `scripts/check_no_secrets.py`. The two lists had already drifted: the script
  exempted two test files that do not exist.

## [0.1.0] - 2026-09-15

Initial reference implementation of the guided modernization factory.

### Added

- **Contracts.** Ten JSON Schemas under `contracts/` covering engagement, workload,
  evidence, target decision, risk, migration wave, migration plan, approval, validation
  report, and GitHub issue, with matching Pydantic v2 models.
- **Playbook layer.** `playbooks/default/` with `charter.md`, `targets.md`, and
  `policies.md`, plus three example playbooks (regulated enterprise, renewal-led SQL,
  AI-ready data) and a validator that fails on duplicate or conflicting policy IDs,
  missing exception fields, and expired exceptions.
- **Deterministic pipeline.** Evidence normalization, rule-based workload assessment,
  configurable target scoring, wave planning, Jinja2 rendering, and GitHub issue
  generation. Identical inputs produce byte-identical outputs.
- **CLI.** `dbmodernize` with `init`, `validate-repo`, `validate-playbook`,
  `validate-skill`, `validate-agent`, `normalize-evidence`, `assess`,
  `recommend-targets`, `plan-waves`, `render-plan`, `generate-issues`,
  `validate-scenario`, and `render-report`. Read-only and dry-run by default, with
  overwrite protection and documented exit codes.
- **Agent Skills.** Seventeen skills under `.github/skills/`, each with the required
  eleven-section body and an invoke / do-not-invoke contract.
- **Agents.** Eight agents under `.github/agents/` with least-privilege tool allowlists,
  artifact-based handoffs, and no self-approval.
- **Scenarios.** Seven executable scenarios with committed expected artifacts, including
  a failed-validation-and-rollback scenario that must produce a no-go.
- **Adapters.** CSV, Azure Migrate, Arc-enabled SQL, DMS, and SSMA evidence adapters
  behind a common interface, with size, entry-count, and path-traversal protections.
- **CI.** Lint, format check, strict typing, tests, schema validation, skill and agent
  validation, playbook validation, and scenario tests as merge gates; CodeQL, dependency
  review, and secret scanning in a separate security workflow; model-based evaluations in
  a manual and scheduled workflow that is explicitly not a merge gate.
- **Documentation.** Architecture, guidance, operations, Copilot usage, governance, and
  an FY27 field-readiness appendix, with source-controlled Mermaid diagrams.
- **Optional infrastructure.** Bicep reference modules under `infra/`, what-if only, with
  no production defaults.

### Security

- Synthetic fixtures only; repository validation rejects tracked evidence classified
  above `internal`.
- Imported documents are treated as untrusted data; directive-like content is reported as
  a prompt-injection finding rather than acted on.
- No long-lived cloud credentials; optional Azure access is designed for GitHub OIDC.
- Archive and CSV ingestion enforce entry-count, per-entry size, and total-size limits.
- Log redaction for connection strings, tokens, and key-like values.

[Unreleased]: https://github.com/REPLACE-ME-ORG/fy27-database-modernization-factory/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/REPLACE-ME-ORG/fy27-database-modernization-factory/releases/tag/v0.1.0
