---
name: postgres-mysql-modernization
description: Assess self-managed PostgreSQL, MySQL, or MariaDB for a managed flexible server, covering major version, extensions and plugins, high availability, backup, identity, networking, and application compatibility.
---

# Managed open-source relational modernization

The default candidate for these engines is the managed flexible server. The work is not
choosing it — the work is proving the extensions, the version, and the availability design
survive the move.

## Invoke when

- A PostgreSQL, MySQL, or MariaDB workload needs assessing.
- Extension or plugin compatibility needs establishing.
- Self-managed high availability is being replaced by a platform capability.
- An unsupported major version is driving the engagement.

## Do not invoke when

- The source is SQL Server — use `sql-server-modernization` instead.
- The source is Oracle — use `oracle-heterogeneous-migration` instead.
- The comparison itself is being run — defer to `azure-target-recommendation`.

## Required inputs

| Input | Source | Required |
| --- | --- | --- |
| Major and minor version | `SELECT version()` or equivalent | Yes |
| Installed and in-use extensions or plugins, with versions | Catalogue query | Yes |
| Current high-availability mechanism | Operations owner | Yes |
| Backup method and last successful restore | Operations owner | Yes |
| Authentication method | Database owner | Yes |
| Network path from applications | Network owner | Yes |
| Application driver and version | Application owner | Yes |

## Preconditions

1. Extension inventory distinguishes installed from in use. Installed is not used.
2. The version is known to minor level; upgrade paths depend on it.
3. Whether a restore has ever been tested is recorded honestly.

## Procedure

1. Record the version and derive support posture from the dated reference table.
2. List extensions and plugins with their versions, and mark which are in use.
3. For each in-use extension, record the availability question as unresolved until it is
   checked against the managed service for that engine version. Availability differs by
   version, so a general answer is not an answer.
4. Record the current high-availability design and whether failover has been tested.
5. Record the backup method and the date of the last successful restore. A backup that has
   never been restored is an assumption.
6. Record the authentication method. Shared database logins need an explicit plan or a
   policy exception.
7. Record the network path, and whether applications can reach a private endpoint.
8. Record driver versions. An old driver can fail against a newer server for reasons
   unrelated to the migration itself.
9. Hand the assessed workload to `azure-target-recommendation`.

## Decision points

| Evidence | Effect |
| --- | --- |
| Extension in use, availability unconfirmed | Recommendation is conditional; verification is a wave prerequisite |
| Extension unavailable on the managed service | Block the managed target; the alternative is infrastructure or removing the dependency |
| Major version below support | Raises urgency and adds an upgrade step to the plan |
| Self-managed replication scripting | Replacing it is a benefit, and removing it is a plan task |
| Shared login authentication | Requires a change or an exception with compensating controls |
| Untested restore | Blocking availability finding |

## Output contract

An assessed workload carrying `source_version`, `extensions`, `service_level`, findings for
every unverified extension and untested recovery path, and — for regulated data — the
compliance scope. The extension finding is high severity, because it is the single most
common cause of a failed open-source migration.

## Validation

```bash
dbmodernize assess --engagement input/engagement.yaml --input input --out out
dbmodernize validate-scenario scenarios/03-postgresql-to-flexible-server
```

## Failure and fallback

- **Extension list unobtainable.** Record it as unknown and block the recommendation. An
  unknown extension set is the same risk as an unknown dependency.
- **Extension unavailable and load-bearing.** The options are infrastructure, removing the
  dependency, or not moving. Record all three; do not pick one on technical grounds alone.
- **Backup never restored.** Raise a blocking finding and make a restore test a wave
  prerequisite.
- **Network path unclear.** Record it as an open question owned by the network owner. A
  connectivity surprise at cutover is avoidable and expensive.

## Avoid

- Describing this as a lift and shift. Version, extensions, availability, identity, and
  networking all change.
- Answering extension availability generally rather than per version.
- Assuming the managed service reproduces in-house replication behaviour.
- Treating the current availability design as tested because it exists.

## Example

Three extensions are in use. Two are widely available; one is central to the application's
core algorithm.

The recommendation names the managed flexible server, but conditionally: verifying that
extension for the target version is a wave entry prerequisite, and the validation plan
carries a check for it. If it turns out to be unavailable, the decision is revisited
before any data moves rather than after.
