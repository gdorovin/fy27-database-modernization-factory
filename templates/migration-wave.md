# Migration waves — {{ engagement.customer_alias }}

> {{ provenance_note }}

| | |
| --- | --- |
| Engagement | `{{ engagement.engagement_id }}` |
| As at | {{ as_of }} |
| Waves | {{ waves | length }} |
| Deferred workloads | {{ deferred | length }} |

Waves are ordered lowest risk first, and workloads that depend on each other stay
together. Splitting a dependency pair across waves produces a cutover that half-works,
which is harder to recover from than either whole option.

## Deferred workloads

{% if deferred %}
These workloads are not yet assignable, normally because a blocking finding is open.

{% for workload_id in deferred %}
- `{{ workload_id }}` — {{ workload_names.get(workload_id, workload_id) }}
{% endfor %}
{% else %}
No workloads are deferred.
{% endif %}

## Sequence

| # | Wave | Pilot | Workloads | Depends on |
| --- | --- | --- | --- | --- |
{% for wave in waves %}
| {{ wave.sequence }} | {{ wave.name }} | {{ wave.is_pilot | yes_no }} | {{ wave.workload_ids | length }} | {% if wave.depends_on_wave_ids %}{{ wave.depends_on_wave_ids | join(', ') }}{% else %}—{% endif %} |
{% endfor %}

{% for wave in waves %}
## {{ wave.name }}

{{ wave.objective | sentence }}

| | |
| --- | --- |
| Identifier | `{{ wave.id }}` |
| Sequence | {{ wave.sequence }} |
| Pilot | {{ wave.is_pilot | yes_no }} |
| Owners | {{ wave.owner_roles | join(', ') }} |
| Rollback required | {{ wave.rollback_required | yes_no }} |

### Workloads

{% for workload_id in wave.workload_ids %}
- `{{ workload_id }}` — {{ workload_names.get(workload_id, workload_id) }}
{% endfor %}

### Prerequisites

{{ wave.prerequisites | bullets }}

### Entry criteria

| Criterion | Verified by | Owner | Automated |
| --- | --- | --- | --- |
{% for criterion in wave.entry_criteria %}
| {{ criterion.statement }} | {{ criterion.verification_method }} | {{ criterion.owner_role }} | {{ criterion.automated | yes_no }} |
{% endfor %}

### Exit criteria

| Criterion | Verified by | Owner | Automated |
| --- | --- | --- | --- |
{% for criterion in wave.exit_criteria %}
| {{ criterion.statement }} | {{ criterion.verification_method }} | {{ criterion.owner_role }} | {{ criterion.automated | yes_no }} |
{% endfor %}

{% endfor %}
