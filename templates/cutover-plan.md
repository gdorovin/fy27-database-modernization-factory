# Cutover plan — {{ wave.name }}

> {{ provenance_note }}

| | |
| --- | --- |
| Engagement | `{{ engagement.engagement_id }}` |
| Wave | `{{ wave.id }}` |
| Plan | `{{ plan.id }}` |
| As at | {{ as_of }} |
| Owner | {{ cutover.owner_role }} |
| Execution window | {{ cutover.execution_window }} |
| Freeze starts | {{ cutover.freeze_start }} |

## Required approvals

All of the following must have recorded an approval before the cutover begins. Four of
five is not a cutover approval.

{% for role in cutover.required_approval_roles %}
- [ ] {{ role.value }}
{% endfor %}

## Replication

{{ cutover.replication_method | sentence }}

## Go / no-go criteria

The decision is explicit and is announced either way. "No objection" is not a go.

| Criterion | Verified by | Owner | Automated |
| --- | --- | --- | --- |
{% for criterion in cutover.go_no_go_criteria %}
| {{ criterion.statement }} | {{ criterion.verification_method }} | {{ criterion.owner_role }} | {{ criterion.automated | yes_no }} |
{% endfor %}

## Sequence

1. Announce the freeze and confirm the on-call roster is in place.
2. Apply the write freeze at {{ cutover.freeze_start }}.
3. Drain replication to zero lag and hold for the agreed period.
4. Run the go / no-go review with all five owner roles present.
5. On go: switch the application, run smoke tests, and confirm write availability.
6. On no-go: stop, announce it, and follow `rollback-plan.md`.
7. Announce the outcome, including the time taken and any deviation from plan.

## Communication

{{ cutover.communication_plan | bullets }}

## If anything goes wrong

Rollback triggers, method, decision window, and evidence preservation are in
`rollback-plan-{{ wave.sequence }}.md`. Read it before the window opens, not during it.

## What this document does not do

It does not execute anything. Every step above is performed by a named human with the
recorded approvals in hand.
