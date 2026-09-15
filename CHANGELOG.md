# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
