---
applyTo: "infra/**"
---

# Infrastructure

Everything here is a **reference**. This repository previews infrastructure; it never
applies it.

## What-if first, always

```bash
az deployment group what-if \
  --resource-group <rg> \
  --template-file infra/bicep/main.bicep \
  --parameters infra/bicep/main.bicepparam
```

Read the output. An unexplained change in a preview is the cheapest place that surprise
will ever appear. No workflow in this repository runs an apply, and none should be added.

## No production defaults

- No default subscription, resource group, region, or environment name.
- Every parameter that identifies a target is required, so a copy-paste cannot deploy
  somewhere unintended.
- `environmentName` defaults to a non-production value if it defaults at all.
- No parameter value that would be correct in a real tenant.

## Parameterise identity

- Region, names, sizes, and tiers are parameters, never literals.
- Names are composed from a workload identifier and an environment, following the playbook
  naming policy.
- No hardcoded tenant id, subscription id, object id, or principal id. Placeholders are
  obviously fake: `00000000-0000-0000-0000-000000000000`.

## Secure by default

The modules default to the posture the playbook requires, so an insecure deployment takes a
deliberate act rather than an oversight:

- Public network access disabled.
- Private endpoint and private DNS integration.
- Managed identity authentication; no administrator password parameter exists.
- Encryption in transit enforced with an explicit minimum TLS version.
- Diagnostic settings pointing at a workspace parameter.
- Zone redundancy and backup retention as parameters with conservative defaults.

If a parameter would let someone turn a control off, it needs a comment explaining when
that is legitimate.

## Structure

- `main.bicep` composes modules. It contains no resource definitions of its own.
- `modules/` holds one concern per file.
- `main.bicepparam` holds an example parameter set with obviously fake values.
- Every module has a header comment: what it creates, what it assumes, and what it
  deliberately does not do.

## Validation

```bash
az bicep build --file infra/bicep/main.bicep
az bicep lint  --file infra/bicep/main.bicep
```

Compilation is checked in CI. Deployment is not, because CI has no credentials and should
never have any.

## Out of scope

- Applying a deployment.
- Deleting or modifying an existing resource.
- Anything that needs a long-lived credential. Future Azure access uses GitHub OIDC.
