"""Shared enumerations and the artifact base class.

Every decision-oriented artifact in this repository inherits :class:`ArtifactBase`, so
provenance, assumptions, confidence, open questions, playbook version, approvals, and
status are structurally impossible to omit.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from dbmodernize import SCHEMA_VERSION

Identifier = Annotated[str, Field(min_length=1, max_length=120, pattern=r"^[A-Za-z0-9][\w.\-]*$")]
NonEmptyStr = Annotated[str, Field(min_length=1)]


class StrictModel(BaseModel):
    """Rejects unknown fields so that a typo becomes an error, not a silent no-op."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=False)


class Confidence(StrEnum):
    """Deliberately coarse. A percentage would imply precision the evidence lacks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EvidenceClass(StrEnum):
    """How a statement came to be believed."""

    OBSERVED = "observed"
    USER_PROVIDED = "user-provided"
    DERIVED = "derived"
    ASSUMPTION = "assumption"
    RECOMMENDATION = "recommendation"
    APPROVED_DECISION = "approved-decision"


class Classification(StrEnum):
    """Data sensitivity. Anything above ``internal`` must never be committed."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


COMMITTABLE_CLASSIFICATIONS = frozenset({Classification.PUBLIC, Classification.INTERNAL})


class ArtifactStatus(StrEnum):
    DRAFT = "draft"
    EVIDENCE_COMPLETE = "evidence-complete"
    RECOMMENDED = "recommended"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    IMPLEMENTATION_READY = "implementation-ready"
    VALIDATING = "validating"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKER = "blocker"


class Likelihood(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SourcePlatform(StrEnum):
    SQL_SERVER = "sql-server"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MARIADB = "mariadb"
    ORACLE = "oracle"
    OTHER = "other"


class AzureTarget(StrEnum):
    """Every target the repository is allowed to recommend.

    ``RETAIN``, ``RETIRE``, and ``REPLACE_SAAS`` are first-class outcomes. A factory that
    can only say "migrate" is a sales script, not an assessment.
    """

    SQL_DATABASE = "azure-sql-database"
    SQL_DATABASE_HYPERSCALE = "azure-sql-database-hyperscale"
    SQL_MANAGED_INSTANCE = "azure-sql-managed-instance"
    SQL_ON_AZURE_VM = "sql-server-on-azure-vm"
    #: The source engine, self-managed on an Azure virtual machine. Used for PostgreSQL,
    #: MySQL, MariaDB, and Oracle sources, where offering "SQL Server on a VM" as the
    #: infrastructure alternative would be a different engine wearing a familiar label.
    SELF_MANAGED_ON_AZURE_VM = "self-managed-on-azure-vm"
    ARC_ENABLED_SQL = "azure-arc-enabled-sql-server"
    POSTGRESQL_FLEXIBLE = "azure-database-for-postgresql-flexible-server"
    MYSQL_FLEXIBLE = "azure-database-for-mysql-flexible-server"
    #: Oracle Database on Oracle-managed Exadata infrastructure inside Azure data centres,
    #: purchased through Azure Marketplace. Keeps the engine, so no conversion is involved.
    ORACLE_DATABASE_AT_AZURE = "oracle-database-at-azure"
    RETAIN = "retain-on-premises"
    RETIRE = "retire"
    REPLACE_SAAS = "replace-with-saas"


class Disposition(StrEnum):
    REHOST = "rehost"
    REPLATFORM = "replatform"
    REFACTOR = "refactor"
    REARCHITECT = "rearchitect"
    REBUILD = "rebuild"
    RETAIN = "retain"
    RETIRE = "retire"
    REPLACE = "replace"


class DowntimeClass(StrEnum):
    """``zero`` is intentionally absent. See ``.github/copilot-instructions.md``."""

    NEAR_ZERO_PLANNED = "near-zero-planned"
    SHORT_PLANNED = "short-planned"
    EXTENDED_PLANNED = "extended-planned"
    UNKNOWN = "unknown"


class ApprovalRole(StrEnum):
    BUSINESS_OWNER = "business-owner"
    APPLICATION_OWNER = "application-owner"
    DATABASE_OWNER = "database-owner"
    SECURITY_OWNER = "security-owner"
    OPERATIONS_OWNER = "operations-owner"
    ARCHITECT = "architect"
    DELIVERY_LEAD = "delivery-lead"


#: All five must sign a cutover. Fewer is not a cutover approval.
CUTOVER_REQUIRED_ROLES = frozenset(
    {
        ApprovalRole.BUSINESS_OWNER,
        ApprovalRole.APPLICATION_OWNER,
        ApprovalRole.DATABASE_OWNER,
        ApprovalRole.SECURITY_OWNER,
        ApprovalRole.OPERATIONS_OWNER,
    }
)


class Assumption(StrictModel):
    """A gap filled in so work could proceed. It carries an owner and a way to settle it."""

    id: Identifier
    statement: NonEmptyStr
    owner_role: NonEmptyStr
    validation_step: NonEmptyStr
    impact_if_wrong: Severity = Severity.MEDIUM


class OpenQuestion(StrictModel):
    id: Identifier
    question: NonEmptyStr
    owner_role: NonEmptyStr
    blocking: bool = False
    needed_by: date | None = None


class PlaybookRef(StrictModel):
    """Pins the governance contract that produced an artifact."""

    path: NonEmptyStr
    version: NonEmptyStr
    commit: str | None = None
    policy_ids: list[str] = Field(default_factory=list)

    @field_validator("policy_ids")
    @classmethod
    def _sorted_unique(cls, value: list[str]) -> list[str]:
        return sorted(set(value))


class ApprovalRef(StrictModel):
    """A pointer to an approval artifact, not the approval itself."""

    approval_id: Identifier
    role: ApprovalRole
    decision: str
    approved_at: datetime


class ArtifactBase(StrictModel):
    """Common provenance envelope for every decision-oriented artifact."""

    id: Identifier
    schema_version: str = SCHEMA_VERSION
    artifact_type: str
    engagement_id: Identifier
    workload_ids: list[Identifier] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    author: NonEmptyStr = Field(
        description="Human principal or generating agent name, e.g. 'agent:target-architect'."
    )
    evidence_refs: list[Identifier] = Field(default_factory=list)
    assumptions: list[Assumption] = Field(default_factory=list)
    confidence: Confidence = Confidence.LOW
    open_questions: list[OpenQuestion] = Field(default_factory=list)
    risk_ids: list[Identifier] = Field(default_factory=list)
    playbook: PlaybookRef
    approvals: list[ApprovalRef] = Field(default_factory=list)
    status: ArtifactStatus = ArtifactStatus.DRAFT
    supersedes: Identifier | None = None

    @property
    def is_approved(self) -> bool:
        return self.status in {
            ArtifactStatus.APPROVED,
            ArtifactStatus.IMPLEMENTATION_READY,
            ArtifactStatus.ACCEPTED,
        }

    @property
    def blocking_questions(self) -> list[OpenQuestion]:
        return [q for q in self.open_questions if q.blocking]
