"""Render artifacts into the human-readable documents an engagement actually uses."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dbmodernize.models.decision import TargetDecisionSet
from dbmodernize.models.engagement import Engagement
from dbmodernize.models.evidence import EvidenceBundle
from dbmodernize.models.planning import MigrationPlan, MigrationWave, WavePlan
from dbmodernize.models.risk import RiskRegister
from dbmodernize.models.validation import ValidationCheck, ValidationReport
from dbmodernize.models.workload import WorkloadInventory
from dbmodernize.renderers.engine import render
from dbmodernize.scoring.reference import REVALIDATION_NOTE

PROVENANCE_NOTE = (
    "Generated from repository artifacts. Every statement here traces to an evidence "
    "reference, an assumption, or a recommendation, and is labelled as such. This document "
    "is a proposal until a human approves it."
)


def _base_context(engagement: Engagement) -> dict[str, Any]:
    return {
        "engagement": engagement,
        # The engagement's own as-of date, not the wall clock: rendering must be reproducible.
        "as_of": engagement.as_of.isoformat(),
        "provenance_note": PROVENANCE_NOTE,
        "revalidation_note": REVALIDATION_NOTE,
    }


def render_assessment_summary(
    repo_root: Path,
    engagement: Engagement,
    inventory: WorkloadInventory,
    bundle: EvidenceBundle,
    risks: RiskRegister,
) -> str:
    context = _base_context(engagement)
    context.update(
        {
            "inventory": inventory,
            "workloads": sorted(inventory.workloads, key=lambda w: w.id),
            "bundle": bundle,
            "risks": sorted(risks.risks, key=lambda r: r.id),
            "blocked_workloads": [w for w in inventory.workloads if w.blocking_findings],
            "conflicts": bundle.unresolved_conflicts,
            "injection_flagged": bundle.injection_flagged,
            "source_counts": _source_counts(bundle),
        }
    )
    return render(repo_root, "assessment-summary.md", context)


def render_target_decisions(
    repo_root: Path,
    engagement: Engagement,
    decisions: TargetDecisionSet,
    inventory: WorkloadInventory,
) -> str:
    context = _base_context(engagement)
    context.update(
        {
            "decisions": sorted(decisions.decisions, key=lambda d: d.workload_id),
            "unresolved": decisions.unresolved_workload_ids,
            "inventory": inventory,
            "workload_names": {w.id: w.name for w in inventory.workloads},
        }
    )
    return render(repo_root, "target-decision.md", context)


def render_migration_plan(
    repo_root: Path,
    engagement: Engagement,
    plan: MigrationPlan,
    wave: MigrationWave,
    decisions: TargetDecisionSet,
    inventory: WorkloadInventory,
) -> str:
    context = _base_context(engagement)
    context.update(
        {
            "plan": plan,
            "wave": wave,
            "decisions": [d for d in decisions.decisions if d.workload_id in wave.workload_ids],
            "workload_names": {w.id: w.name for w in inventory.workloads},
            "mutating_tasks": [
                task for phase in plan.phases for task in phase.tasks if task.changes_environment
            ],
        }
    )
    return render(repo_root, "migration-plan.md", context)


def render_cutover_plan(
    repo_root: Path, engagement: Engagement, plan: MigrationPlan, wave: MigrationWave
) -> str:
    context = _base_context(engagement)
    context.update({"plan": plan, "wave": wave, "cutover": plan.cutover})
    return render(repo_root, "cutover-plan.md", context)


def render_rollback_plan(
    repo_root: Path, engagement: Engagement, plan: MigrationPlan, wave: MigrationWave
) -> str:
    context = _base_context(engagement)
    context.update({"plan": plan, "wave": wave, "rollback": plan.rollback})
    return render(repo_root, "rollback-plan.md", context)


def render_validation_plan(
    repo_root: Path,
    engagement: Engagement,
    wave: MigrationWave,
    checks: list[ValidationCheck],
) -> str:
    context = _base_context(engagement)
    context.update(
        {
            "wave": wave,
            "checks": checks,
            "by_category": _group_by_category(checks),
            "blocking_count": sum(1 for check in checks if check.blocking),
        }
    )
    return render(repo_root, "validation-plan.md", context)


def render_validation_report(
    repo_root: Path, engagement: Engagement, report: ValidationReport
) -> str:
    context = _base_context(engagement)
    context.update(
        {
            "report": report,
            "counts": report.counts,
            "blocking_failures": report.blocking_failures,
            "blocking_not_run": report.blocking_not_run,
            "by_category": _group_by_category(report.checks),
            "is_no_go": report.outcome.value == "no-go",
        }
    )
    return render(repo_root, "validation-report.md", context)


def render_wave_plan(
    repo_root: Path,
    engagement: Engagement,
    waves: WavePlan,
    inventory: WorkloadInventory,
) -> str:
    context = _base_context(engagement)
    context.update(
        {
            "waves": sorted(waves.waves, key=lambda w: w.sequence),
            "deferred": waves.deferred_workload_ids,
            "workload_names": {w.id: w.name for w in inventory.workloads},
        }
    )
    return render(repo_root, "migration-wave.md", context)


def render_executive_brief(
    repo_root: Path,
    engagement: Engagement,
    inventory: WorkloadInventory,
    decisions: TargetDecisionSet,
    waves: WavePlan,
    risks: RiskRegister,
) -> str:
    """Summarise approved artifacts. Introduces no fact that is not already recorded."""
    context = _base_context(engagement)
    context.update(
        {
            "workload_count": len(inventory.workloads),
            "decided_count": len(decisions.decisions),
            "unresolved": decisions.unresolved_workload_ids,
            "wave_count": len(waves.waves),
            "waves": sorted(waves.waves, key=lambda w: w.sequence),
            "top_risks": sorted(risks.open_high_risks, key=lambda r: (-r.score, r.id))[:5],
            "target_mix": _target_mix(decisions),
            "inventory": inventory,
        }
    )
    return render(repo_root, "executive-brief.md", context)


def _group_by_category(checks: list[ValidationCheck]) -> dict[str, list[ValidationCheck]]:
    grouped: dict[str, list[ValidationCheck]] = {}
    for check in sorted(checks, key=lambda c: (c.category.value, c.id)):
        grouped.setdefault(check.category.value, []).append(check)
    return grouped


def _source_counts(bundle: EvidenceBundle) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in bundle.records:
        counts[record.source.value] = counts.get(record.source.value, 0) + 1
    return dict(sorted(counts.items()))


def _target_mix(decisions: TargetDecisionSet) -> dict[str, int]:
    counts: dict[str, int] = {}
    for decision in decisions.decisions:
        key = decision.recommended_target.value
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


__all__ = [
    "PROVENANCE_NOTE",
    "render_assessment_summary",
    "render_cutover_plan",
    "render_executive_brief",
    "render_migration_plan",
    "render_rollback_plan",
    "render_target_decisions",
    "render_validation_plan",
    "render_validation_report",
    "render_wave_plan",
]
