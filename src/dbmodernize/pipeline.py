"""The deterministic pipeline.

One function runs the whole chain, because the chain *is* the product: evidence in,
auditable artifacts out, with nothing in the middle that a human cannot reconstruct.

Determinism rules that every step obeys:

* Time comes from ``engagement.as_of``, never from the clock.
* Collections are sorted before serialization.
* Nothing consults the network, the environment, or a model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dbmodernize.errors import InputNotFoundError, ValidationFailedError
from dbmodernize.evidence.normalize import normalize_directory
from dbmodernize.issue_generation.generator import generate_issues
from dbmodernize.models.base import PlaybookRef
from dbmodernize.models.decision import TargetDecisionSet
from dbmodernize.models.engagement import Engagement
from dbmodernize.models.evidence import EvidenceBundle
from dbmodernize.models.planning import MigrationPlan, WavePlan
from dbmodernize.models.risk import RiskRegister
from dbmodernize.models.validation import ValidationReport
from dbmodernize.models.workload import WorkloadInventory
from dbmodernize.policies.loader import playbook_reference
from dbmodernize.policies.models import Playbook
from dbmodernize.renderers import documents
from dbmodernize.scoring.assessment import assess
from dbmodernize.scoring.plan import build_plan
from dbmodernize.scoring.targets import recommend_all
from dbmodernize.scoring.validation_plan import build_validation_plan
from dbmodernize.scoring.waves import plan_waves
from dbmodernize.utils.io import read_structured
from dbmodernize.validators.playbook import validate_playbook

#: Output filenames, in dependency order. The scenario validator compares exactly these.
JSON_OUTPUTS = (
    "evidence.json",
    "workloads.json",
    "risks.json",
    "target-decisions.json",
    "waves.json",
)
YAML_OUTPUTS = ("issues.yaml",)
#: Rendered once per engagement.
MARKDOWN_OUTPUTS = (
    "assessment-summary.md",
    "target-decision.md",
    "migration-waves.md",
    "executive-brief.md",
)
#: Rendered once per wave, suffixed with the wave sequence. A three-wave programme needs
#: three plans; emitting only the first would quietly hide two thirds of the work.
PER_WAVE_OUTPUTS = (
    "migration-plan-{sequence}.md",
    "cutover-plan-{sequence}.md",
    "rollback-plan-{sequence}.md",
    "validation-plan-{sequence}.md",
)


@dataclass(slots=True)
class PipelineResult:
    """Everything the pipeline produced, in memory."""

    engagement: Engagement
    playbook: Playbook
    playbook_ref: PlaybookRef
    bundle: EvidenceBundle
    inventory: WorkloadInventory
    risks: RiskRegister
    decisions: TargetDecisionSet
    waves: WavePlan
    plans: list[MigrationPlan]
    issues: Any
    documents: dict[str, str] = field(default_factory=dict)
    structured: dict[str, Any] = field(default_factory=dict)
    validation_report: ValidationReport | None = None

    @property
    def artifacts(self) -> dict[str, Any]:
        """Filename to content: structured objects for JSON/YAML, strings for Markdown."""
        return {**self.structured, **self.documents}


def load_engagement(path: Path) -> Engagement:
    if not path.is_file():
        raise InputNotFoundError(f"Engagement file not found: {path}")
    return Engagement.model_validate(read_structured(path))


def run_pipeline(
    repo_root: Path,
    engagement_path: Path,
    evidence_dir: Path,
    playbook_dir: Path,
    validation_report_path: Path | None = None,
) -> PipelineResult:
    engagement = load_engagement(engagement_path)

    playbook, findings = validate_playbook(playbook_dir, as_of=engagement.as_of)
    if playbook is None or not findings.ok:
        # Exit code 1, the same as ``dbmodernize validate-playbook`` returns for the same
        # defect. One condition, one exit code, whichever command surfaces it.
        messages = "; ".join(f.message for f in findings.errors) or "see findings"
        raise ValidationFailedError(
            f"Playbook at {playbook_dir} is not usable: {messages}", findings
        )

    playbook_ref = playbook_reference(playbook, repo_root)

    bundle = normalize_directory(
        evidence_dir,
        engagement_id=engagement.engagement_id,
        collected_on=engagement.as_of,
    )
    inventory, risks = assess(engagement, bundle, playbook_ref)
    decisions = recommend_all(inventory, engagement, playbook, playbook_ref, risks)
    waves = plan_waves(inventory, decisions, engagement, playbook_ref)
    plans = [
        build_plan(wave, decisions, engagement, playbook, playbook_ref)
        for wave in sorted(waves.waves, key=lambda w: w.sequence)
    ]
    issues = generate_issues(engagement, inventory, decisions, waves, playbook_ref)

    structured: dict[str, Any] = {
        "evidence.json": _dump(bundle),
        "workloads.json": _dump(inventory),
        "risks.json": _dump(risks),
        "target-decisions.json": _dump(decisions),
        "waves.json": _dump(waves),
        "issues.yaml": _dump(issues),
    }

    rendered: dict[str, str] = {
        "assessment-summary.md": documents.render_assessment_summary(
            repo_root, engagement, inventory, bundle, risks
        ),
        "target-decision.md": documents.render_target_decisions(
            repo_root, engagement, decisions, inventory
        ),
        "migration-waves.md": documents.render_wave_plan(repo_root, engagement, waves, inventory),
        "executive-brief.md": documents.render_executive_brief(
            repo_root, engagement, inventory, decisions, waves, risks
        ),
    }

    if plans:
        for wave, plan in zip(sorted(waves.waves, key=lambda w: w.sequence), plans, strict=True):
            suffix = wave.sequence
            checks = build_validation_plan(wave, decisions, inventory)
            rendered[f"migration-plan-{suffix}.md"] = documents.render_migration_plan(
                repo_root, engagement, plan, wave, decisions, inventory
            )
            rendered[f"cutover-plan-{suffix}.md"] = documents.render_cutover_plan(
                repo_root, engagement, plan, wave
            )
            rendered[f"rollback-plan-{suffix}.md"] = documents.render_rollback_plan(
                repo_root, engagement, plan, wave
            )
            rendered[f"validation-plan-{suffix}.md"] = documents.render_validation_plan(
                repo_root, engagement, wave, checks
            )
            structured[f"migration-plan-{suffix}.json"] = _dump(plan)

    report: ValidationReport | None = None
    if validation_report_path and validation_report_path.is_file():
        report = ValidationReport.model_validate(read_structured(validation_report_path))
        rendered["validation-report.md"] = documents.render_validation_report(
            repo_root, engagement, report
        )
        structured["validation-report.json"] = _dump(report)

    return PipelineResult(
        engagement=engagement,
        playbook=playbook,
        playbook_ref=playbook_ref,
        bundle=bundle,
        inventory=inventory,
        risks=risks,
        decisions=decisions,
        waves=waves,
        plans=plans,
        issues=issues,
        documents=rendered,
        structured=structured,
        validation_report=report,
    )


def _dump(model: Any) -> Any:
    """Serialize a Pydantic model to plain JSON-compatible data, deterministically."""
    return model.model_dump(mode="json", exclude_none=False)


__all__ = [
    "JSON_OUTPUTS",
    "MARKDOWN_OUTPUTS",
    "PER_WAVE_OUTPUTS",
    "YAML_OUTPUTS",
    "PipelineResult",
    "load_engagement",
    "run_pipeline",
]
