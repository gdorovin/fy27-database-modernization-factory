# AI-ready data playbook — targets

The target set is close to the default. That is deliberate: the destination is rarely what
decides whether an intelligent scenario works, and treating it as the interesting question
is how these engagements go wrong.

## Approved targets

| Target | Status | Conditions |
| --- | --- | --- |
| azure-sql-database | approved | Common where the consuming application is modern and database-scoped. |
| azure-sql-database-hyperscale | conditional | Where measured size or growth justifies it. Event and history stores often qualify. |
| azure-sql-managed-instance | approved | Where instance-scoped capability is evidenced as in use. |
| azure-database-for-postgresql-flexible-server | approved | Extension availability verified per extension and per version. |
| azure-database-for-mysql-flexible-server | approved | Plugin and version compatibility verified before recommendation. |
| retain-on-premises | conditional | Requires a recorded reason and a review date. Note that a retained workload cannot serve a cloud-hosted scenario without a separate data path, which is its own decision. |
| retire | conditional | Requires business-owner confirmation and a retention decision. |
| azure-arc-enabled-sql-server | conditional | A governance bridge only. Never recorded as completed modernization, and never as readiness. |

## Prohibited targets

| Target | Status | Reason |
| --- | --- | --- |
| sql-server-on-azure-vm | prohibited | Not because it cannot work, but because in this engagement type it consistently absorbs the effort that data quality and ownership needed. An exception requires an architect and the data owner, with a named reason why an infrastructure target is necessary here. |

## Notes

Free-text governance context, enforced in code and in the skills rather than by the tables
above.

**The target does not make the estate ready.** Readiness is assessed separately, against
ownership, quality, semantics, access, retention, and headroom. A perfect migration to a
perfect target changes none of those.

**Serving path is a separate decision.** Whether the intelligent scenario reads the
operational system directly, or a separate serving copy, affects concurrency, access
control, and deletion obligations. Decide it explicitly; it is not a consequence of the
target.

**Every derived copy inherits obligations, not permissions.** An index, cache, or embedding
built from regulated data carries the retention and deletion duty. It does not
automatically carry the row-level access control, and assuming otherwise is the security
failure this playbook exists to prevent.
