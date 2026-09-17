# Infrastructure reference

Bicep that shows what a compliant target looks like under the default playbook. It is a
**reference**, not a deployment pipeline.

**Nothing in this repository applies a deployment.** There are no credentials here, no
workflow that runs `az deployment ... create`, and none should be added. CI compiles and
lints the templates; a human previews and applies them.

## Preview only

```bash
az deployment group what-if \
  --resource-group <your-resource-group> \
  --template-file infra/bicep/main.bicep \
  --parameters infra/bicep/main.bicepparam
```

Read the output before doing anything else. An unexplained change in a preview is the
cheapest place that surprise will ever appear; the same surprise at cutover costs the
window.

## Compile and lint

```bash
az bicep build --file infra/bicep/main.bicep
az bicep lint  --file infra/bicep/main.bicep
```

Both run in CI. Deployment does not.

## Layout

| Path | Holds |
| --- | --- |
| `bicep/main.bicep` | Composition only. No resources of its own. |
| `bicep/main.bicepparam` | An example parameter set with obviously fake values. |
| `bicep/modules/sql-database.bicep` | A database-scoped SQL target |
| `bicep/modules/sql-managed-instance.bicep` | An instance-scoped SQL target |
| `bicep/modules/postgresql-flexible.bicep` | A managed PostgreSQL target |
| `bicep/modules/private-endpoint.bicep` | Private connectivity and DNS integration |
| `bicep/modules/diagnostics.bicep` | Diagnostic settings to a workspace |
| `tests/` | Expectations about the templates themselves |

## Secure by default

The modules default to the posture `playbooks/default/policies.md` requires, so an insecure
deployment takes a deliberate act rather than an oversight:

| Policy | How the modules satisfy it |
| --- | --- |
| `SEC-001` public endpoint prohibited | `publicNetworkAccess` defaults to `Disabled` |
| `SEC-002` encryption at rest | Enabled and not parameterised off |
| `SEC-003` encryption in transit | Minimum TLS version set explicitly |
| `IAM-001` managed or directory identity | No administrator password parameter exists |
| `NET-001` private connectivity | SQL Database: private endpoint module composed by default. Managed Instance and PostgreSQL Flexible Server: injected into a delegated subnet, which is private by construction |
| `NET-002` name resolution | SQL Database: private DNS zone group created with the endpoint. PostgreSQL: the server is linked to a `*.private.postgres.database.azure.com` zone you supply; a `privatelink.*` zone is the wrong kind and the deployment will say so |
| `OBS-002` diagnostics | Diagnostic settings module requires a workspace |
| `AVL-003` backup | Retention is a parameter with a conservative default. Backup storage redundancy (`Geo` by default) and PostgreSQL geo-redundant backup (`Enabled` by default) are separate, explicit parameters, never derived from zone redundancy: deriving them silently produced locally redundant backups with no geo-restore |

Where a parameter could turn a control off, it carries a comment explaining when that is
legitimate.

## No production defaults

No default subscription, resource group, region, or environment. Every parameter that
identifies a target is required, so a copy-paste cannot deploy somewhere unintended.
`environmentName` defaults to a non-production value.

## Relationship to the rest of the repository

A migration plan's build and cutover tasks reference a what-if command against these
templates, and both tasks carry an approval requirement and a rollback note. The plan is
the governance; this directory is only the shape of the thing being governed.
