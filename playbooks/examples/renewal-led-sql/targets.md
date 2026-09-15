# Renewal-led SQL playbook — targets

Wider than the regulated playbook, because the constraint here is time rather than
supervision. A target that gets a workload live before the date, with an honest record of
what it costs later, can be the right answer.

## Approved targets

| Target | Status | Conditions |
| --- | --- | --- |
| azure-sql-managed-instance | approved | The common answer where instance-scoped features are in use and the application cannot change before the date. |
| azure-sql-database | approved | Where no instance-scoped dependency exists. |
| azure-sql-database-hyperscale | conditional | Only where size or growth evidence justifies it. |
| sql-server-on-azure-vm | conditional | Legitimate where operating-system control is evidenced, or where it is the only path that completes before the date. In the latter case the decision must record that it is a staging step, with a review date, so it is not mistaken later for the intended architecture. |
| azure-arc-enabled-sql-server | conditional | A governance bridge for workloads that will not move before the date. Must carry a review date and must never be recorded as completed modernization. |
| retain-on-premises | approved | Expected for part of the estate. Requires a recorded reason, the renewal impact, and a review date. |
| retire | conditional | Requires business-owner confirmation and a retention decision. Often the cheapest win available before a renewal. |
| replace-with-saas | conditional | Rarely completable before a near date. Requires evidence of product fit plus an owned data and integration plan. |
| azure-database-for-postgresql-flexible-server | approved | Where open-source workloads sit inside the renewal boundary. |
| azure-database-for-mysql-flexible-server | approved | As above. |

## Prohibited targets

This playbook prohibits no target. Under time pressure, removing an option without a reason
tends to mean the reason was never examined.

## Notes

Free-text governance context, enforced in code and in the skills rather than by the tables
above.

**A staging step must be labelled as one.** Where infrastructure is chosen because it is
the only path that completes in time, the decision records that explicitly and carries a
review date. Otherwise, in eighteen months, nobody can tell a deliberate architecture from
an expedient one — and the expedient one gets defended as if it were deliberate.

**Retiring is underrated before a renewal.** A workload nobody uses still carries a licence
line. Ask early, because the answer takes longer to confirm than to act on.

**Arc is not progress.** Enrolling an instance improves governance and changes nothing
about the renewal position. Counting it as progress against the date is the specific error
this note exists to prevent.
