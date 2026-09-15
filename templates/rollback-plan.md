# Rollback plan — {{ wave.name }}

> {{ provenance_note }}

| | |
| --- | --- |
| Engagement | `{{ engagement.engagement_id }}` |
| Wave | `{{ wave.id }}` |
| Plan | `{{ plan.id }}` |
| As at | {{ as_of }} |
| Owner | {{ rollback.owner_role }} |
| Rehearsed | {{ rollback.rehearsed | yes_no }} |

{% if not rollback.rehearsed %}
> **This rollback has not been rehearsed.** An unrehearsed rollback is a hypothesis. The
> wave entry criteria require a rehearsal before cutover.
{% endif %}

## Triggers

Any one of these triggers a rollback decision. They are thresholds, not opinions, so the
decision does not depend on who is in the room at 03:00.

| Trigger | Verified by | Owner | Automated |
| --- | --- | --- | --- |
{% for criterion in rollback.triggers %}
| {{ criterion.statement }} | {{ criterion.verification_method }} | {{ criterion.owner_role }} | {{ criterion.automated | yes_no }} |
{% endfor %}

## Decision window

{{ rollback.maximum_decision_window | sentence }}

Past that point the rollback itself no longer fits inside the agreed window, and the
decision changes from "roll back" to "fix forward under incident management".

## Method

{{ rollback.method | sentence }}

## Preserve evidence first

{{ rollback.evidence_preservation | sentence }}

Rolling back without capturing evidence guarantees the next attempt fails the same way.

## Data reconciliation

{{ rollback.data_reconciliation_note | sentence }}

Rollback is not complete when the application is serving again. It is complete when the
data question is settled and the business owner has agreed the outcome.

## After a rollback

1. Record the outcome as a validation report with a `no-go` result.
2. Raise corrective issues for every failure, each with an owner.
3. Hold a blameless review and update the plan before scheduling another attempt.
4. Never describe a rolled-back attempt as a success.
