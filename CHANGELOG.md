# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **FILESTREAM, FileTable, and PolyBase no longer favour a managed instance.** They were
  listed as instance-scoped features, so a workload using FILESTREAM scored Managed
  Instance *up* by 25 for a feature Managed Instance cannot run — the exact wrong
  recommendation this repository exists to prevent. They now live in
  `MANAGED_TARGET_UNAVAILABLE_FEATURES`, block every managed target the way an
  operating-system dependency does, raise their own assessment finding
  (`r-managed-target-unavailable-features`), and a unit test keeps the two feature sets
  disjoint.
- **Support lifecycle table corrected against the Microsoft Lifecycle pages.** SQL Server
  2019 left mainstream support on 2025-02-28 and is now `extended-support`; SQL Server 2025
  (engine major 17) was missing, so a current-version estate was reported as
  `unknown` — a *blocking* finding. PostgreSQL floor raised to 14 (13 reached community end
  of life 2025-11-13); MySQL floor raised to 8.4 (8.0 reached end of life 2026-04-30).
  `VERIFIED_ON` moved to 2026-09-16.
- **PostgreSQL, MySQL, and MariaDB workloads are no longer compared with "SQL Server on
  Azure VM".** A new `self-managed-on-azure-vm` target stands for the source engine on an
  Azure virtual machine. `sql-server-on-azure-vm` is now offered to SQL Server sources only.
- **`assess`, `recommend-targets`, and `plan-waves` embed the same playbook reference as
  `render-plan`.** They pinned the playbook against the current working directory rather
  than the repository root, so identical evidence produced a different `workloads.json`
  depending on where the command was launched. All three gained `--repo`, and every command
  loads the playbook through one helper.
- **`--dry-run` no longer fails with exit code 4 when the output already exists.** The
  overwrite guard ran before the dry-run check, which made a second preview impossible
  without `--force`.
- **An unusable playbook exits 1 from every command.** `render-plan`, `generate-issues`,
  `render-report`, and `validate-scenario` returned 2 (usage error) for the same defect that
  `validate-playbook` reported as 1; the findings are now printed either way.
- **Migration plans carry their risks.** `TargetDecision.risk_ids` was never populated, so
  `MigrationPlan.risk_ids` was always empty and the risk register was a document nothing
  downstream read. The assessment's register is now threaded into `recommend_all`.
- **Printed score adjustments always sum to the score.** `Evaluation.adjust` clamped the
  score but recorded the unclamped delta; it now records the delta actually applied and
  notes the clamp.
- **A genuine 0% automatic conversion is reported as 0%, not omitted.**
- **Duplicate tool blocking codes produce one finding, not two findings with one id.**
- **The playbook parser is fence-aware and reports malformed rows.** Pipe-bearing lines
  inside a fenced block were parsed as table rows, so the default playbook's example
  exception was one column count away from being in force. A row whose cell count does not
  match the header now raises `PLAYBOOK-ROW-MALFORMED` instead of being skipped in silence.
- **CSV reading preserves quoted newlines and reports ragged rows.** Cells past the header
  width are surfaced as unmapped input; a non-UTF-8 export produces a usage error naming the
  byte, not a traceback.
- **JSON adapters tolerate malformed-but-valid JSON.** `"databases": null`,
  `"performance": []`, or `"automatic": "many"` no longer crash with an internal error, and
  every record in a file now reports the same `unmapped_fields` set.
- **A cross-source conflict with one distinct spelling no longer crashes evidence
  normalization** (`640.0` from a spreadsheet versus `"640.0"` from a JSON export).
- **Archive extraction counts decompressed bytes**, so a header that lies about its size is
  caught before the limit is exceeded rather than after.
- **`validate-scenario --update` exits non-zero** and reports how many artifacts differed;
  a command that regenerates its own expectations must never read as a passing check.
- **Scenarios must declare acceptance criteria** (`SCENARIO-NO-ACCEPTANCE`), because a
  snapshot alone can be laundered by regenerating it.
- **A "read-only" agent is held to it by its own body text**, not only by the curated
  `NON_EDITING_AGENTS` list, so a new agent cannot slip an editing tool past the validator by
  being new. `value-advisor`'s outputs are restated as drafts it returns, since it holds no
  editing tool.
- **The Bicep reference would now pass `what-if`.** Managed Instance SKU names use the
  resource-provider values (`GP_Gen5`, `GP_G8IM`, `GP_G8IH`, `BC_Gen5`, `BC_G8IM`,
  `BC_G8IH`; `GP_Gen8IM` was never valid); backup storage redundancy is an explicit
  parameter (`Geo` by default) instead of a side effect of `zoneRedundant` that silently set
  backups to `Local`; PostgreSQL geo-redundant backup — immutable after creation — is its
  own parameter; the PostgreSQL module names its subnet `delegatedSubnetId` and documents
  that virtual-network injection needs a `*.private.postgres.database.azure.com` zone, not a
  `privatelink.*` one; `restrictOutboundNetworkAccess` is a parameter defaulting to
  `Disabled`; the retired diagnostic `retentionPolicy` and the duplicate `audit` category
  group are gone; `Microsoft.Sql` resources use the stable `2023-08-01` API; PostgreSQL 17
  and 18 are selectable.
- **CI runs the whole test suite.** The enumerated paths silently excluded `tests/infra`,
  `tests/scale`, `tests/snapshots`, and `tests/evals` from every pull request.
- **The Bicep CLI in CI is pinned** (`v0.47.16`, installed through the Azure CLI) instead of
  fetched from `releases/latest` over curl with no version or checksum inside the merge gate.
- **`contents: write` is no longer exempt from the workflow permission check.** It is allowed
  only where a named file has a documented reason (`release.yml`).
- **Secret scanning covers `.bicepparam`, `.env`, `.ini`, `.xml`, `.sql`, and `.j2`**, and
  the endpoint pattern now matches `*.postgres.database.azure.com`,
  `*.mysql.database.azure.com`, and storage-account hosts. Private DNS zone labels are
  exempt.
- **Stale references corrected**: `SECURITY.md` named a `validators.approval` module that
  does not exist; `AGENTS.md` claimed `--json` on every command; the always-on instructions
  described a `--create` confirmation flag the CLI refuses unconditionally; a skill pointed
  at `tests/unit/test_classification.py`; an ADR cited `IAM-004`, which is not in the
  baseline; Data Migration Assistant, a retired product, was listed as an input; Scenario 04
  attributed an Oracle-to-PostgreSQL conversion to SSMA, which has no PostgreSQL path. All
  seven `scenario.yaml` files carried a UTF-8 byte-order mark in a repository that enforces
  byte-exact output.

### Added

- **`oracle-database-at-azure` target.** Oracle Database on Oracle-managed infrastructure
  inside Azure is compared for every Oracle workload. It is scored the way Arc is scored for
  SQL Server: the honest answer when no conversion has been assessed, and a recorded,
  rejected fallback when one has. Scenario 04's plant-maintenance schema now lands there
  rather than on retention, and its decision record states that this is a relocation and a
  licensing decision, not a modernization of the engine. Regional availability and commercial
  terms remain account-team inputs with a date.
- **MariaDB to MySQL Flexible Server requires conversion evidence.** The pair is now in
  `HETEROGENEOUS_PAIRS`; a fork crossing is an engine change, not a like-for-like move.
- **`.github/dependabot.yml`** for GitHub Actions, pip, and the dev container, so the SHA
  pins and version floors have an updater.
- **`PAAS_BLOCKING_FEATURES`** as the single set the comparison consults when deciding
  whether any managed target is possible.

### Changed

- **Scenario expectations must be regenerated** after this change set
  (`dbmodernize validate-scenario scenarios --update`, then review the diff): lifecycle
  postures, the two new targets, populated `risk_ids`, and the renamed VM target for
  open-source engines all change committed artifacts deliberately.

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
