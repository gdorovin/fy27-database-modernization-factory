"""Dated reference data.

Everything here perishes. Support lifecycles change, service capabilities change, and
what is blocked today may be supported next quarter. Each table therefore carries a
``VERIFIED_ON`` date, and the guidance is explicit: revalidate before using any of this
with a customer.

These tables encode *shape*, not commercial terms. There is deliberately no pricing, no
funding eligibility, and no preview status here — those change faster than a repository
can track and belong in a live conversation with the account team.
"""

from __future__ import annotations

from datetime import date

from dbmodernize.models.base import AzureTarget, SourcePlatform
from dbmodernize.models.workload import SupportStatus

#: The date a maintainer last checked these tables against published product guidance.
VERIFIED_ON: date = date(2026, 9, 16)

REVALIDATION_NOTE = (
    "Reference tables were last verified on "
    f"{VERIFIED_ON.isoformat()}. Support status, service capabilities, and limits change. "
    "Revalidate against current product documentation before presenting any conclusion "
    "drawn from them to a customer."
)

#: SQL Server major version to support posture. Keys are the engine major version.
#:
#: Mainstream support is what ``SUPPORTED`` means here. A version in extended support still
#: receives security fixes, but nothing else, and that finite window is what should anchor
#: a modernization date. Dates from the Microsoft Lifecycle pages, checked on VERIFIED_ON:
#: 2016 extended support ended 2026-07-14; 2017 mainstream ended 2022-10-11 (extended to
#: 2027-10-12); 2019 mainstream ended 2025-02-28 (extended to 2030-01-08); 2022 mainstream
#: runs to 2028-01-11; 2025 (engine major 17) was released 2025-11-18.
SQL_SERVER_SUPPORT: dict[int, SupportStatus] = {
    10: SupportStatus.END_OF_SUPPORT,  # 2008 / 2008 R2
    11: SupportStatus.END_OF_SUPPORT,  # 2012
    12: SupportStatus.END_OF_SUPPORT,  # 2014
    13: SupportStatus.END_OF_SUPPORT,  # 2016
    14: SupportStatus.EXTENDED_SUPPORT,  # 2017
    15: SupportStatus.EXTENDED_SUPPORT,  # 2019
    16: SupportStatus.SUPPORTED,  # 2022
    17: SupportStatus.SUPPORTED,  # 2025
}

#: PostgreSQL major versions this repository treats as unsupported for new deployments.
#: PostgreSQL 13 reached community end of life on 2025-11-13. PostgreSQL 14 follows on
#: 2026-11-12, inside FY27, so an estate on 14 should already be planning its upgrade.
POSTGRESQL_END_OF_SUPPORT_BELOW = 14

#: MySQL major.minor below this is treated as unsupported for new deployments. MySQL 8.0
#: reached community end of life on 2026-04-30; 8.4 is the current long-term-support line.
#: A managed service may sell extended support for 8.0 beyond that date; that is a
#: commercial arrangement the account team confirms, not a support posture this table
#: asserts.
MYSQL_END_OF_SUPPORT_BELOW = (8, 4)

#: Engine features that are scoped to an instance rather than a database. Their presence
#: does not forbid a database-scoped target, but it does mean the application must change,
#: and that has to be an explicit decision rather than a silent assumption.
#:
#: Every feature listed here is available on an instance-scoped managed target. That is
#: the property the scoring relies on: an instance-scoped feature *rewards* the instance
#: target. A feature that no managed target offers belongs in
#: MANAGED_TARGET_UNAVAILABLE_FEATURES instead, and a unit test keeps the two sets disjoint.
INSTANCE_SCOPED_FEATURES: frozenset[str] = frozenset(
    {
        "sql-agent",
        "service-broker",
        "cross-database-queries",
        "linked-servers",
        "clr",
        "replication",
        # Managed instances support distributed transactions between managed instances and
        # with SQL Server; a classic on-premises coordinator in the loop is an application
        # change that the assessment has to confirm rather than assume.
        "distributed-transactions",
        "database-mail",
        "server-level-triggers",
    }
)

#: Engine features that no managed SQL target offers, at either database or instance scope.
#: Using one of them rules out every platform-as-a-service target, exactly as an
#: operating-system dependency does, until the application stops depending on it. Listing
#: them as instance-scoped would have scored a managed instance *up* for a feature it
#: cannot run.
MANAGED_TARGET_UNAVAILABLE_FEATURES: frozenset[str] = frozenset(
    {
        "filestream",
        "filetable",
        "polybase",
    }
)

#: Features that require operating-system access and therefore rule out any PaaS target.
OS_LEVEL_FEATURES: frozenset[str] = frozenset(
    {
        "os-level-access",
        "third-party-agent",
        "custom-filesystem-access",
        "unsupported-extended-stored-procedures",
        "kerberos-constrained-delegation-custom",
    }
)

#: Everything that blocks a managed target, whichever of the two reasons applies.
PAAS_BLOCKING_FEATURES: frozenset[str] = OS_LEVEL_FEATURES | MANAGED_TARGET_UNAVAILABLE_FEATURES

#: Data size above which a Hyperscale comparison becomes worth making, in gigabytes.
HYPERSCALE_SIZE_THRESHOLD_GB = 1024.0

#: Annual growth above which Hyperscale enters the comparison regardless of current size.
HYPERSCALE_GROWTH_THRESHOLD_PERCENT = 40.0

#: Targets that can serve each source platform. Membership means "worth comparing",
#: never "compatible" — compatibility is decided per workload from evidence.
PLATFORM_CANDIDATES: dict[SourcePlatform, tuple[AzureTarget, ...]] = {
    SourcePlatform.SQL_SERVER: (
        AzureTarget.SQL_MANAGED_INSTANCE,
        AzureTarget.SQL_DATABASE,
        AzureTarget.SQL_DATABASE_HYPERSCALE,
        AzureTarget.SQL_ON_AZURE_VM,
        AzureTarget.ARC_ENABLED_SQL,
        AzureTarget.RETAIN,
    ),
    SourcePlatform.POSTGRESQL: (
        AzureTarget.POSTGRESQL_FLEXIBLE,
        AzureTarget.SELF_MANAGED_ON_AZURE_VM,
        AzureTarget.RETAIN,
    ),
    SourcePlatform.MYSQL: (
        AzureTarget.MYSQL_FLEXIBLE,
        AzureTarget.SELF_MANAGED_ON_AZURE_VM,
        AzureTarget.RETAIN,
    ),
    SourcePlatform.MARIADB: (
        AzureTarget.MYSQL_FLEXIBLE,
        AzureTarget.SELF_MANAGED_ON_AZURE_VM,
        AzureTarget.RETAIN,
    ),
    SourcePlatform.ORACLE: (
        AzureTarget.ORACLE_DATABASE_AT_AZURE,
        AzureTarget.POSTGRESQL_FLEXIBLE,
        AzureTarget.SQL_MANAGED_INSTANCE,
        AzureTarget.SQL_DATABASE,
        AzureTarget.SELF_MANAGED_ON_AZURE_VM,
        AzureTarget.REPLACE_SAAS,
        AzureTarget.RETAIN,
    ),
    SourcePlatform.OTHER: (AzureTarget.RETAIN,),
}

#: Migrating between engine families always means schema and code conversion. Oracle on
#: Oracle-managed infrastructure inside Azure, and Oracle on an Azure virtual machine, keep
#: the engine and are therefore *not* in this set: they are relocations, not conversions.
#: MariaDB to a MySQL-family managed service is a fork crossing; it is listed so that
#: conversion evidence is required rather than assumed from the shared ancestry.
HETEROGENEOUS_PAIRS: frozenset[tuple[SourcePlatform, AzureTarget]] = frozenset(
    {
        (SourcePlatform.ORACLE, AzureTarget.POSTGRESQL_FLEXIBLE),
        (SourcePlatform.ORACLE, AzureTarget.SQL_MANAGED_INSTANCE),
        (SourcePlatform.ORACLE, AzureTarget.SQL_DATABASE),
        (SourcePlatform.ORACLE, AzureTarget.REPLACE_SAAS),
        (SourcePlatform.MARIADB, AzureTarget.MYSQL_FLEXIBLE),
    }
)


def sql_server_support(version: str | None) -> SupportStatus:
    """Map a SQL Server version string to a support posture.

    An unparseable or missing version returns ``UNKNOWN``. It never guesses, because a
    wrong support status silently changes the urgency of the whole engagement.
    """
    if not version:
        return SupportStatus.UNKNOWN
    head = version.strip().split(".")[0]
    if not head.isdigit():
        return SupportStatus.UNKNOWN
    return SQL_SERVER_SUPPORT.get(int(head), SupportStatus.UNKNOWN)


def open_source_support(platform: SourcePlatform, version: str | None) -> SupportStatus:
    if not version:
        return SupportStatus.UNKNOWN
    parts = version.strip().split(".")
    if not parts[0].isdigit():
        return SupportStatus.UNKNOWN
    major = int(parts[0])

    if platform is SourcePlatform.POSTGRESQL:
        return (
            SupportStatus.END_OF_SUPPORT
            if major < POSTGRESQL_END_OF_SUPPORT_BELOW
            else SupportStatus.SUPPORTED
        )
    if platform in {SourcePlatform.MYSQL, SourcePlatform.MARIADB}:
        minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        return (
            SupportStatus.END_OF_SUPPORT
            if (major, minor) < MYSQL_END_OF_SUPPORT_BELOW
            else SupportStatus.SUPPORTED
        )
    return SupportStatus.UNKNOWN


__all__ = [
    "HETEROGENEOUS_PAIRS",
    "HYPERSCALE_GROWTH_THRESHOLD_PERCENT",
    "HYPERSCALE_SIZE_THRESHOLD_GB",
    "INSTANCE_SCOPED_FEATURES",
    "MANAGED_TARGET_UNAVAILABLE_FEATURES",
    "MYSQL_END_OF_SUPPORT_BELOW",
    "OS_LEVEL_FEATURES",
    "PAAS_BLOCKING_FEATURES",
    "PLATFORM_CANDIDATES",
    "POSTGRESQL_END_OF_SUPPORT_BELOW",
    "REVALIDATION_NOTE",
    "SQL_SERVER_SUPPORT",
    "VERIFIED_ON",
    "open_source_support",
    "sql_server_support",
]
