# Infrastructure tests

These assert properties of the **templates**, not of a deployment. No test here contacts
Azure, and none ever should: CI has no credentials and should never be given any.

Compilation and linting run in `.github/workflows/ci.yml`:

```bash
az bicep build --file infra/bicep/main.bicep
az bicep lint  --file infra/bicep/main.bicep
```

The properties worth asserting, and where they are enforced today:

| Property | Enforced by |
| --- | --- |
| Templates compile | `bicep build` in CI |
| No lint violations | `bicep lint` in CI |
| No administrator password parameter exists | `tests/repository/test_repository.py` secret scan, plus review |
| No real subscription, tenant, or resource id | `scripts/check_no_secrets.py` |
| No production default for region or environment | Review against `.github/instructions/infrastructure.instructions.md` |
| Public network access defaults to disabled | Review; see `infra/README.md` for the policy mapping |

## Why there is no deployment test

A deployment test needs a subscription, a credential, and a resource group that somebody
pays for. It would also be the only thing in this repository capable of changing a cloud
environment, which is precisely the boundary the whole design exists to hold.

What-if output is reviewed by a human as a plan task, with an approval and a rollback note
attached. That is the control; an automated deployment test would replace it with a weaker
one.

## Adding a module

1. One concern per file, with a header comment saying what it creates, what it assumes, and
   what it deliberately does not do.
2. Secure defaults, so an insecure deployment takes a deliberate act.
3. Any parameter that could turn a control off carries a comment explaining when that is
   legitimate.
4. Compose it from `main.bicep`; `main.bicep` holds no resources of its own.
5. Update the policy mapping table in `infra/README.md`.
