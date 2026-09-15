"""Build the validation plan for a wave.

The plan is a list of checks with tolerances. A check without a tolerance cannot
distinguish pass from fail, so every generated check either carries one or is explicitly
marked as a judgement call with a named owner.

The plan is not a report. Reports record what was observed; a plan that pretended to be a
report would start life claiming a verdict it has no evidence for.
"""

from __future__ import annotations

from dbmodernize.models.decision import TargetDecisionSet
from dbmodernize.models.planning import MigrationWave
from dbmodernize.models.validation import CheckCategory, CheckResult, ValidationCheck
from dbmodernize.models.workload import Workload, WorkloadInventory

#: Default regression tolerance for the performance comparison, as a percentage.
DEFAULT_PERFORMANCE_TOLERANCE_PERCENT = 10


def build_validation_plan(
    wave: MigrationWave,
    decisions: TargetDecisionSet,
    inventory: WorkloadInventory,
) -> list[ValidationCheck]:
    workloads = [w for w in inventory.workloads if w.id in wave.workload_ids]
    checks: list[ValidationCheck] = list(_universal_checks(wave))

    for workload in workloads:
        checks.extend(_workload_checks(wave, workload))
        decision = decisions.get(workload.id)
        if decision is not None and decision.conversion_required:
            checks.extend(_conversion_checks(wave, workload))
        if workload.compliance_scopes:
            checks.append(_compliance_check(wave, workload))
        if workload.extensions:
            checks.append(_extension_check(wave, workload))

    return sorted(checks, key=lambda check: check.id)


def _check(
    wave_id: str,
    suffix: str,
    category: CheckCategory,
    name: str,
    method: str,
    tolerance: str | None,
    *,
    blocking: bool = True,
    notes: str | None = None,
) -> ValidationCheck:
    return ValidationCheck(
        id=f"{wave_id}-vc-{suffix}",
        category=category,
        name=name,
        method=method,
        tolerance=tolerance,
        result=CheckResult.NOT_RUN,
        blocking=blocking,
        notes=notes,
    )


def _universal_checks(wave: MigrationWave) -> list[ValidationCheck]:
    wave_id = wave.id
    return [
        _check(
            wave_id,
            "inventory-complete",
            CheckCategory.INVENTORY,
            "Every workload in the wave is accounted for",
            "Compare the migrated object inventory with the wave workload list",
            "Zero unaccounted workloads",
        ),
        _check(
            wave_id,
            "config-parity",
            CheckCategory.CONFIGURATION,
            "Target configuration matches the approved design",
            "Compare deployed configuration with the infrastructure-as-code definition",
            "Zero unexplained differences",
        ),
        _check(
            wave_id,
            "connectivity",
            CheckCategory.CONNECTIVITY,
            "Every confirmed consumer can connect to the target",
            "Connect from each application host using the production identity and network path",
            "All confirmed consumers connect successfully",
        ),
        _check(
            wave_id,
            "availability-failover",
            CheckCategory.AVAILABILITY,
            "Failover behaves as designed",
            "Trigger a controlled failover and measure recovery",
            "Recovery within the agreed RTO",
        ),
        _check(
            wave_id,
            "backup-restore",
            CheckCategory.BACKUP_RESTORE,
            "A restore from backup succeeds",
            "Restore into an isolated environment and verify the data",
            "Restore completes and row counts reconcile",
        ),
        _check(
            wave_id,
            "rpo-rto",
            CheckCategory.RPO_RTO,
            "Measured RPO and RTO meet the agreed targets",
            "Measure during the controlled failover and restore tests",
            "Within the agreed RPO and RTO",
        ),
        _check(
            wave_id,
            "security-config",
            CheckCategory.SECURITY_CONFIGURATION,
            "Security configuration matches policy",
            "Compare deployed settings with the playbook security policies",
            "Zero policy deviations without an approved exception",
        ),
        _check(
            wave_id,
            "identity",
            CheckCategory.IDENTITY,
            "Authentication and authorization work as designed",
            "Verify managed identity or directory authentication and least-privilege roles",
            "No account holds more privilege than its documented role",
        ),
        _check(
            wave_id,
            "network-isolation",
            CheckCategory.NETWORK_ISOLATION,
            "Network isolation is enforced",
            "Attempt connection from outside the approved network path",
            "Connection refused from every unapproved path",
        ),
        _check(
            wave_id,
            "encryption",
            CheckCategory.ENCRYPTION,
            "Encryption in transit and at rest is enabled",
            "Inspect the connection and storage encryption settings",
            "Encryption enabled on all paths",
        ),
        _check(
            wave_id,
            "auditing",
            CheckCategory.AUDITING,
            "Auditing and diagnostic logging reach their destination",
            "Generate an auditable event and confirm it arrives in the log sink",
            "Event visible in the sink within the agreed interval",
        ),
        _check(
            wave_id,
            "posture",
            CheckCategory.POSTURE,
            "Security posture and policy compliance show no new high findings",
            "Review posture and policy reporting for the target scope",
            "No new high or critical finding attributable to this migration",
        ),
        _check(
            wave_id,
            "monitoring",
            CheckCategory.MONITORING,
            "Monitoring and alerting are live and routed to an owner",
            "Trigger a test alert and confirm it reaches the on-call rota",
            "Alert received by a named owner",
        ),
        _check(
            wave_id,
            "runbooks",
            CheckCategory.RUNBOOKS,
            "Operational runbooks exist and have been walked through",
            "Operations owner walkthrough of the runbook against the deployed target",
            None,
            blocking=False,
            notes="A judgement call by the operations owner rather than a measured threshold.",
        ),
        _check(
            wave_id,
            "cost-sizing",
            CheckCategory.COST_SIZING,
            "Observed consumption is consistent with the sizing assumption",
            "Compare observed consumption with the sizing used in the business case",
            "Within the agreed variance, or a documented resize action",
            blocking=False,
        ),
        _check(
            wave_id,
            "business-acceptance",
            CheckCategory.BUSINESS_ACCEPTANCE,
            "Business owner accepts the outcome",
            "Formal acceptance recorded as an approval artifact",
            "Approval recorded by the business owner",
        ),
    ]


def _workload_checks(wave: MigrationWave, workload: Workload) -> list[ValidationCheck]:
    wave_id = wave.id
    slug = workload.id
    tolerance = f"Within {DEFAULT_PERFORMANCE_TOLERANCE_PERCENT}% of the recorded baseline"
    return [
        _check(
            wave_id,
            f"{slug}-schema",
            CheckCategory.SCHEMA,
            f"{workload.name}: schema objects reconcile",
            "Compare object counts and definitions between source and target",
            "Zero unexplained differences",
        ),
        _check(
            wave_id,
            f"{slug}-rowcounts",
            CheckCategory.DATA_RECONCILIATION,
            f"{workload.name}: row counts and checksums reconcile",
            "Compare row counts and column checksums per table",
            "Zero unreconciled tables",
        ),
        _check(
            wave_id,
            f"{slug}-datatypes",
            CheckCategory.DATA_TYPES,
            f"{workload.name}: data types and precision are preserved",
            "Compare column types, precision, scale, and collation",
            "Zero precision or collation differences without a recorded decision",
        ),
        _check(
            wave_id,
            f"{slug}-referential",
            CheckCategory.REFERENTIAL_INTEGRITY,
            f"{workload.name}: referential integrity holds",
            "Validate constraints and check for orphaned rows",
            "Zero constraint violations and zero orphans",
        ),
        _check(
            wave_id,
            f"{slug}-programmability",
            CheckCategory.PROGRAMMABILITY,
            f"{workload.name}: stored procedures and functions behave identically",
            "Execute the agreed procedure test set and compare results with the source",
            "Identical results for every case in the set",
        ),
        _check(
            wave_id,
            f"{slug}-functional",
            CheckCategory.FUNCTIONAL,
            f"{workload.name}: application functional tests pass",
            "Run the application functional suite against the target",
            "Zero failures",
        ),
        _check(
            wave_id,
            f"{slug}-regression",
            CheckCategory.REGRESSION,
            f"{workload.name}: regression suite passes",
            "Run the application regression suite against the target",
            "Zero new failures against the source run",
        ),
        _check(
            wave_id,
            f"{slug}-integration",
            CheckCategory.INTEGRATION,
            f"{workload.name}: integrations with dependent systems succeed",
            "Exercise each confirmed dependency end to end",
            "Every confirmed dependency succeeds",
        ),
        _check(
            wave_id,
            f"{slug}-performance",
            CheckCategory.PERFORMANCE,
            f"{workload.name}: performance is within tolerance of baseline",
            "Replay the baseline workload and compare latency and throughput",
            tolerance,
        ),
        _check(
            wave_id,
            f"{slug}-concurrency",
            CheckCategory.CONCURRENCY,
            f"{workload.name}: concurrency and locking behaviour are acceptable",
            "Run the peak concurrency profile and observe blocking and deadlocks",
            "No sustained blocking beyond the baseline profile",
        ),
    ]


def _conversion_checks(wave: MigrationWave, workload: Workload) -> list[ValidationCheck]:
    return [
        _check(
            wave.id,
            f"{workload.id}-converted-behaviour",
            CheckCategory.PROGRAMMABILITY,
            f"{workload.name}: converted code produces identical results",
            (
                "Run the agreed comparison set against source and target and diff the output. "
                "Conversion tooling statistics are not accepted as evidence here."
            ),
            "Identical results for every case in the comparison set",
        ),
        _check(
            wave.id,
            f"{workload.id}-converted-business-signoff",
            CheckCategory.BUSINESS_ACCEPTANCE,
            f"{workload.name}: business validation of converted behaviour",
            "Business users exercise the agreed scenarios and confirm the outcome",
            "Explicit confirmation from the named business validators",
        ),
    ]


def _compliance_check(wave: MigrationWave, workload: Workload) -> ValidationCheck:
    scopes = ", ".join(sorted(workload.compliance_scopes))
    return _check(
        wave.id,
        f"{workload.id}-compliance",
        CheckCategory.SECURITY_CONFIGURATION,
        f"{workload.name}: controls for {scopes} are in place and evidenced",
        "Collect control evidence for each scope and review with the security owner",
        "Every required control evidenced",
    )


def _extension_check(wave: MigrationWave, workload: Workload) -> ValidationCheck:
    extensions = ", ".join(sorted(workload.extensions))
    return _check(
        wave.id,
        f"{workload.id}-extensions",
        CheckCategory.CONFIGURATION,
        f"{workload.name}: required extensions are present and at a compatible version",
        f"Verify availability and version of each extension on the target: {extensions}",
        "Every required extension present at a compatible version",
    )


__all__ = ["DEFAULT_PERFORMANCE_TOLERANCE_PERCENT", "build_validation_plan"]
