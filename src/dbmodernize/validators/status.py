"""Artifact status transitions and approval gating."""

from __future__ import annotations

from dbmodernize.errors import FindingSet
from dbmodernize.models.approval import Approval, ApprovalDecision, ApprovalLedger
from dbmodernize.models.base import CUTOVER_REQUIRED_ROLES, ArtifactBase, ArtifactStatus
from dbmodernize.utils.hashing import content_hash

S = ArtifactStatus

#: The only permitted transitions. Anything else is a validation error, not a warning.
ALLOWED_TRANSITIONS: dict[ArtifactStatus, frozenset[ArtifactStatus]] = {
    S.DRAFT: frozenset({S.EVIDENCE_COMPLETE, S.REJECTED, S.SUPERSEDED}),
    S.EVIDENCE_COMPLETE: frozenset({S.RECOMMENDED, S.DRAFT, S.REJECTED, S.SUPERSEDED}),
    S.RECOMMENDED: frozenset({S.REVIEWED, S.DRAFT, S.REJECTED, S.SUPERSEDED}),
    S.REVIEWED: frozenset({S.APPROVED, S.RECOMMENDED, S.REJECTED, S.SUPERSEDED}),
    S.APPROVED: frozenset({S.IMPLEMENTATION_READY, S.SUPERSEDED, S.REJECTED}),
    S.IMPLEMENTATION_READY: frozenset({S.VALIDATING, S.REJECTED, S.SUPERSEDED}),
    S.VALIDATING: frozenset({S.ACCEPTED, S.REJECTED, S.SUPERSEDED}),
    S.ACCEPTED: frozenset({S.SUPERSEDED}),
    S.REJECTED: frozenset({S.DRAFT, S.SUPERSEDED}),
    S.SUPERSEDED: frozenset(),
}

#: Reaching these states requires a matching, valid approval artifact.
APPROVAL_GATED = frozenset({S.APPROVED, S.IMPLEMENTATION_READY})


def check_transition(current: ArtifactStatus, proposed: ArtifactStatus) -> FindingSet:
    findings = FindingSet()
    if current == proposed:
        return findings
    if proposed not in ALLOWED_TRANSITIONS[current]:
        allowed = ", ".join(sorted(s.value for s in ALLOWED_TRANSITIONS[current]))
        findings.add(
            rule="STATUS-TRANSITION",
            message=(
                f"Cannot move from {current.value} to {proposed.value}. "
                f"Allowed from {current.value}: {allowed or 'nothing'}."
            ),
            path="",
        )
    return findings


def check_approval(
    artifact: ArtifactBase,
    artifact_payload: dict[str, object],
    ledger: ApprovalLedger,
) -> FindingSet:
    """Verify that an artifact claiming an approved status actually has one.

    The payload is hashed and compared with the hash recorded at approval time, so an
    edit after approval invalidates it rather than inheriting it.
    """
    findings = FindingSet()
    if artifact.status not in APPROVAL_GATED:
        return findings

    approvals = [
        a for a in ledger.for_artifact(artifact.id) if a.decision is not ApprovalDecision.REJECTED
    ]
    if not approvals:
        findings.add(
            rule="APPROVAL-MISSING",
            message=(
                f"Artifact {artifact.id} has status {artifact.status.value} but no approval "
                "artifact references it. A recommendation cannot approve itself."
            ),
            path=artifact.id,
        )
        return findings

    expected = content_hash(artifact_payload)
    for approval in approvals:
        findings.extend(_check_single(approval, artifact, expected))
    return findings


def _check_single(approval: Approval, artifact: ArtifactBase, expected_hash: str) -> FindingSet:
    findings = FindingSet()
    if approval.artifact_hash != expected_hash:
        findings.add(
            rule="APPROVAL-STALE",
            message=(
                f"Approval {approval.id} was granted against a different version of "
                f"{artifact.id}. The artifact changed after approval, so the approval no "
                "longer applies."
            ),
            path=approval.id,
            hint="Re-request approval, or revert the artifact to the approved content.",
        )
    if approval.artifact_author.strip().lower() == approval.approver_principal.strip().lower():
        findings.add(
            rule="APPROVAL-SELF",
            message=f"Approval {approval.id}: the author approved their own artifact.",
            path=approval.id,
        )
    if approval.approved_artifact_type != artifact.artifact_type:
        findings.add(
            rule="APPROVAL-TYPE-MISMATCH",
            message=(
                f"Approval {approval.id} claims type {approval.approved_artifact_type!r} but "
                f"{artifact.id} is {artifact.artifact_type!r}."
            ),
            path=approval.id,
        )
    return findings


def check_cutover_approvals(artifact_id: str, ledger: ApprovalLedger) -> FindingSet:
    """A cutover needs all five owner roles. Four is not a cutover approval."""
    findings = FindingSet()
    present = ledger.roles_approving(artifact_id)
    missing = CUTOVER_REQUIRED_ROLES - present
    if missing:
        findings.add(
            rule="APPROVAL-CUTOVER-INCOMPLETE",
            message=(
                f"Cutover for {artifact_id} is missing approval from: "
                + ", ".join(sorted(role.value for role in missing))
            ),
            path=artifact_id,
        )
    return findings


__all__ = [
    "ALLOWED_TRANSITIONS",
    "APPROVAL_GATED",
    "check_approval",
    "check_cutover_approvals",
    "check_transition",
]
