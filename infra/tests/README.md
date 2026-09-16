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
| No administrator password parameter exists | `tests/infra/test_bicep_templates.py` |
| No real subscription, tenant, or resource id | `scripts/check_no_secrets.py`, plus a GUID check in `tests/infra/` |
| No production default for region | `tests/infra/test_bicep_templates.py` |
| Public network access is decided, and decided closed | `tests/infra/test_bicep_templates.py` |
| No template downgrades TLS below 1.2 | `tests/infra/test_bicep_templates.py` |
| `main.bicep` composes and declares no resources | `tests/infra/test_bicep_templates.py` |
| Every module is reachable from `main.bicep` | `tests/infra/test_bicep_templates.py` |

Three of these used to say "Review". A control that depends on somebody remembering to look
is not a control, and all three were checkable from the text of the templates.

The tests live in `tests/infra/` rather than here, because that is where pytest collects
from and a test nobody runs is worth less than no test at all. This file explains what they
assert and why; it is not a second place to put them.

## What these tests deliberately do not do

They read what the templates say. They do not model what Azure would do with them. A
property that can only be confirmed against a live API version — whether a given default is
secure this month, whether a preview flag still exists — is left to `bicep build` and to a
human reading what-if output. Approximating it here would produce a test that is confidently
wrong, which is worse than an honest gap.

One such gap: `postgresql-flexible.bicep` sets no TLS property, because Flexible Server
takes that from server configuration rather than from the resource body. The tests assert
only that nothing in the repository *downgrades* TLS, which is what the files can actually
tell us.

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
