# Migration plan — {{ wave.name }}

> {{ provenance_note }}

| | |
| --- | --- |
| Engagement | `{{ engagement.engagement_id }}` |
| Plan | `{{ plan.id }}` |
| Wave | `{{ wave.id }}` (sequence {{ wave.sequence }}) |
| As at | {{ as_of }} |
| Playbook | `{{ plan.playbook.path }}` v{{ plan.playbook.version }} |
| Target decisions | {{ plan.target_decision_ids | join(', ') }} |
| Tasks that change an environment | {{ mutating_tasks | length }} |

{{ wave.objective | sentence }}

## Workloads and targets

| Workload | Target | Disposition | Application change | Conversion |
| --- | --- | --- | --- | --- |
{% for decision in decisions %}
| {{ workload_names.get(decision.workload_id, decision.workload_id) }} | {{ decision.recommended_target.value }} | {{ decision.disposition.value }} | {{ decision.requires_application_change | yes_no }} | {{ decision.conversion_required | yes_no }} |
{% endfor %}

## Approval gates

Every task marked as changing an environment requires a recorded approval before it runs,
and documents how to undo it. Production cutover additionally requires all five owner
roles. Nothing in this repository executes any of it.

{% for task in mutating_tasks %}
- **{{ task.title }}** (`{{ task.id }}`, {{ task.kind.value }}) — owner {{ task.owner_role }}
  - Rollback: {{ task.rollback_note }}
{% if task.dry_run_command %}
  - Dry run first: `{{ task.dry_run_command }}`
{% endif %}
{% endfor %}

## Phases

{% for phase in plan.phases %}
### {{ loop.index }}. {{ phase.name }}

{{ phase.objective | sentence }}

| Task | Kind | Owner | Depends on | Changes environment | Approval |
| --- | --- | --- | --- | --- | --- |
{% for task in phase.tasks %}
| {{ task.title }} | {{ task.kind.value }} | {{ task.owner_role }} | {% if task.depends_on %}{{ task.depends_on | join(', ') }}{% else %}—{% endif %} | {{ task.changes_environment | yes_no }} | {{ task.approval_required | yes_no }} |
{% endfor %}

{% for task in phase.tasks %}
#### {{ task.title }}

{{ task.description | sentence }}

- Identifier: `{{ task.id }}`
- Owner: {{ task.owner_role }}
{% if task.dry_run_command %}
- Dry run: `{{ task.dry_run_command }}`
{% endif %}
{% if task.rollback_note %}
- Rollback: {{ task.rollback_note }}
{% endif %}
{% if task.policy_ids %}
- Policies applied: {{ task.policy_ids | join(', ') }}
{% endif %}

{% endfor %}
{% endfor %}

## Acceptance criteria

| Criterion | Verified by | Owner | Automated |
| --- | --- | --- | --- |
{% for criterion in plan.acceptance_criteria %}
| {{ criterion.statement }} | {{ criterion.verification_method }} | {{ criterion.owner_role }} | {{ criterion.automated | yes_no }} |
{% endfor %}

## Cutover and rollback

The cutover plan and the rollback plan are separate documents so they can be read under
pressure without scrolling past anything else:

- `cutover-plan-{{ wave.sequence }}.md`
- `rollback-plan-{{ wave.sequence }}.md`

## Validation

Validation for this wave is defined in `{{ plan.validation_plan_ref }}`. A blocking check
that has not run is not a pass, and generated tests are supporting evidence rather than
proof.

## Evidence and provenance

- Evidence: {% if plan.evidence_refs %}{{ plan.evidence_refs | join(', ') }}{% else %}_none cited_{% endif %}

- Risks: {% if plan.risk_ids %}{{ plan.risk_ids | join(', ') }}{% else %}_none linked_{% endif %}

- Policies in force: {% if plan.playbook.policy_ids %}{{ plan.playbook.policy_ids | join(', ') }}{% else %}_none recorded_{% endif %}

> {{ revalidation_note }}
