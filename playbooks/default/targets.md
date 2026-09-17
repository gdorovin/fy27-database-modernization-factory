# Default playbook — targets

Which destinations may be recommended, and on what terms. A target absent from both
tables is treated as prohibited: silence is not permission.

Membership in "approved" means *may be compared and recommended*. It never means
*compatible*. Compatibility is decided per workload, from evidence.

## Approved targets

| Target | Status | Conditions |
| --- | --- | --- |
| azure-sql-managed-instance | approved | Strong candidate where instance-scoped capability or broad engine compatibility matters. |
| azure-sql-database | approved | Strong candidate for database-level isolation where no instance-scoped dependency exists. |
| azure-sql-database-hyperscale | conditional | Only where size or growth evidence justifies it. Choosing it without that evidence adds capability nobody asked for. |
| sql-server-on-azure-vm | conditional | Only where operating-system control, engine control, a feature no managed target offers (FILESTREAM, FileTable, PolyBase), or a third-party application constraint is evidenced. Patching and availability remain the customer's responsibility, and that must be stated in the decision. |
| self-managed-on-azure-vm | conditional | The source engine (PostgreSQL, MySQL, MariaDB, Oracle) self-managed on an Azure virtual machine. Same terms as sql-server-on-azure-vm: only where operating-system or engine control is evidenced, and the retained operational burden is stated in the decision. |
| azure-arc-enabled-sql-server | conditional | A governed bridge for estates with incomplete inventory. Must never be described as completed modernization; the workload has not moved. |
| azure-database-for-postgresql-flexible-server | approved | Default managed-service candidate for PostgreSQL. Extension availability is verified per extension and per version. |
| azure-database-for-mysql-flexible-server | approved | Default managed-service candidate for MySQL. Plugin and version compatibility verified before recommendation. A MariaDB source is a fork crossing and requires conversion evidence like any other engine change. |
| oracle-database-at-azure | conditional | Oracle Database on Oracle-managed Exadata infrastructure inside Azure, bought through Azure Marketplace. The engine is unchanged, so no conversion is required; it is a relocation and a licensing decision, not an engine modernization. Regional availability, private-offer terms, and licence entitlement are confirmed by the account team and recorded with a date before commitment. |
| retain-on-premises | approved | A legitimate outcome. Requires a recorded reason and a review date, so it does not become a decision by default. |
| retire | conditional | Requires business-owner confirmation that the workload is genuinely unused, plus a data retention decision. |
| replace-with-saas | conditional | Requires evidence that a product covers the capability, and an owned data migration and integration plan. |

## Prohibited targets

This baseline prohibits no target. A customer playbook may prohibit one — for example a
regulated estate that forbids infrastructure targets — by adding a table here with
`Target`, `Status`, and `Reason` columns. The comparison will then reject that option and
cite this file as the reason.

## Notes

Free-text governance context. The points below are enforced in code and in the skills
rather than by the tables above, so this section is explanation, not a machine-checked
rule. The validator reports it as extended content for exactly that reason.

**Heterogeneous migration is a conversion exercise.** Moving between engine families —
Oracle to SQL, Oracle to PostgreSQL, MariaDB to MySQL, anything similar — requires schema
and code conversion evidence before a recommendation is possible. Conversion tooling
statistics describe tool output. They are not a compatibility verdict, and they say nothing
about whether converted code behaves identically.

**Keeping the engine is a legitimate answer for Oracle.** An Oracle estate that cannot
convert, or has no business case to, is compared against Oracle on Oracle-managed
infrastructure inside Azure and against a self-managed virtual machine, not only against
retention. Neither is an engine modernization, and the decision record says so.

**Some engine features have no managed home.** FILESTREAM, FileTable, and PolyBase are not
available on any managed SQL target at any scope. Their presence blocks every managed
target rather than favouring the instance-scoped one, and the assessment names them.

**One target per workload, chosen on its own evidence.** There is no estate-wide default.
Two workloads on the same instance can legitimately land in different places.

**Arc is a bridge.** It delivers inventory, assessment, and governance over a workload
that has not moved. It classifies as `retain`, and any plan that counts an Arc-enabled
workload as modernized is wrong.

**Sizing evidence gates commitment.** Where sizing is estimated rather than measured, the
decision may still be made, but no capacity or cost commitment rests on it until a
baseline exists.

**Data residency is a hard constraint.** Where a residency requirement is recorded, any
option that cannot satisfy it is blocked rather than scored down.
