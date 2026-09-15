# Executive brief — {{ engagement.customer_alias }}

> {{ provenance_note }} This brief introduces no fact that is not already recorded in an
> underlying artifact.

**As at {{ as_of }}.** Engagement `{{ engagement.engagement_id }}`.

## The outcome being pursued

{% for outcome in engagement.desired_outcomes %}
{{ loop.index }}. {{ outcome | sentence }}
{% endfor %}

{{ engagement.business_context | sentence }}

## Where the work stands

| | |
| --- | --- |
| Workloads assessed | {{ workload_count }} |
| Targets recommended | {{ decided_count }} |
| Awaiting evidence | {{ unresolved | length }} |
| Waves planned | {{ wave_count }} |
| Inventory completeness | {{ inventory.inventory_completeness.value }} |

{% if unresolved %}
{{ unresolved | length }} workload(s) have no recommendation because evidence is
outstanding. That is a deliberate stop, not a delay: a target chosen without the evidence
would have to be revisited later, usually after money has been spent against it.
{% endif %}

## Proposed destinations

{% if target_mix %}
| Target | Workloads |
| --- | --- |
{% for target, count in target_mix.items() %}
| {{ target }} | {{ count }} |
{% endfor %}

Not every workload moves to the same place, and retaining, retiring, or replacing a
workload is a legitimate outcome rather than a failure to migrate.
{% else %}
No targets have been recommended yet.
{% endif %}

## Sequence

{% if waves %}
| # | Wave | Workloads | Pilot |
| --- | --- | --- | --- |
{% for wave in waves %}
| {{ wave.sequence }} | {{ wave.name }} | {{ wave.workload_ids | length }} | {{ wave.is_pilot | yes_no }} |
{% endfor %}
{% else %}
No waves have been planned yet.
{% endif %}

## What could go wrong

{% if top_risks %}
| Risk | Severity | Owner | Mitigation |
| --- | --- | --- | --- |
{% for risk in top_risks %}
| {{ risk.title }} | {{ risk.severity.value }} | {{ risk.owner_role }} | {{ risk.mitigation }} |
{% endfor %}
{% else %}
No high-severity risks are currently open.
{% endif %}

## Decisions needed from the sponsor

1. Confirm the outcomes above are the ones being measured.
2. Name the approvers for each of the five cutover roles.
3. Agree the planned-downtime budget for business-critical workloads.
4. Fund the evidence gathering that is currently blocking recommendations.

## What this brief is not

It is not a commitment to a date, a cost, or a downtime figure. Where a figure is not
recorded here, it is because it has not been measured, and estimating it would create
confidence the evidence does not support.

{% if engagement.success_measures %}
## How success will be judged

| Measure | Baseline known | Measured by |
| --- | --- | --- |
{% for measure in engagement.success_measures %}
| {{ measure.statement }} | {{ measure.baseline_known | yes_no }} | {{ measure.measured_by }} |
{% endfor %}
{% endif %}
