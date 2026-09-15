# Regulated enterprise playbook — targets

Narrower than the default. The narrowing is the point: in a supervised estate, every
additional option is an additional thing to justify.

## Approved targets

| Target | Status | Conditions |
| --- | --- | --- |
| azure-sql-managed-instance | approved | Where instance-scoped capability is evidenced as in use. |
| azure-sql-database | approved | Where no instance-scoped dependency exists. |
| azure-sql-database-hyperscale | conditional | Only where measured size or growth justifies it. Estimated sizing is not sufficient here. |
| azure-database-for-postgresql-flexible-server | approved | Extension availability verified per extension and per version before recommendation. |
| azure-database-for-mysql-flexible-server | approved | Plugin and version compatibility verified before recommendation. |
| azure-arc-enabled-sql-server | conditional | Permitted only as a governance bridge, and only with a recorded review date. Never recorded as completed modernization. |
| retain-on-premises | conditional | Requires a recorded reason, a compensating control review, and a review date. |
| retire | conditional | Requires business-owner confirmation and a documented retention decision under the applicable regime. |

## Prohibited targets

| Target | Status | Reason |
| --- | --- | --- |
| sql-server-on-azure-vm | prohibited | Transfers patching, hardening, and availability back to the customer. Supervisory expectations here favour platform-managed controls. An exception requires compliance-officer approval with a named alternative control set. |
| replace-with-saas | prohibited | A third-party processor introduces a supervisory assessment this playbook does not cover. Handle it as a separate engagement with its own due diligence. |

A prohibited target is still compared and still appears in the decision record, rejected
with a citation. Silently omitting it would hide that it was considered.

## Notes

Free-text governance context. The points below are enforced in code and in the skills
rather than by the tables above.

**Residency blocks, it does not score.** Where a residency requirement is recorded, any
option that cannot satisfy it is blocked outright.

**Measured sizing is required for a tier commitment.** The default playbook permits a
recommendation on estimated sizing while forbidding a commitment. Here, a high-scale tier
additionally requires measurement before it may be recommended at all.

**Arc carries a review date.** A governance bridge with no review date becomes the
architecture by default, and a supervisor will eventually ask when it stopped being
temporary.
