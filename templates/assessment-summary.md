# Assessment summary — {{ engagement.customer_alias }}

> {{ provenance_note }}

| | |
| --- | --- |
| Engagement | `{{ engagement.engagement_id }}` |
| As at | {{ as_of }} |
| Primary trigger | `{{ engagement.primary_trigger.value }}` |
| Workloads assessed | {{ workloads | length }} |
| Inventory completeness | {{ inventory.inventory_completeness.value }} |

## What the customer asked for

{% for outcome in engagement.desired_outcomes %}
{{ loop.index }}. {{ outcome | sentence }}
{% endfor %}

{{ engagement.business_context | sentence }}

## Inventory completeness

{{ inventory.completeness_basis | sentence }}

Completeness is judged `{{ inventory.inventory_completeness.value }}`. An estate that has
not been proven complete cannot support a claim about total scope, cost, or timeline.

### Evidence sources

| Source | Records |
| --- | --- |
{% for source, count in source_counts.items() %}
| {{ source }} | {{ count }} |
{% endfor %}

## Blocking issues

{% if blocked_workloads %}
{{ blocked_workloads | length }} workload(s) cannot receive a target recommendation until
the findings below are closed. This is deliberate: recommending a destination from
incomplete evidence produces a decision nobody can defend.

{% for workload in blocked_workloads %}
### {{ workload.name }} (`{{ workload.id }}`)

{% for finding in workload.blocking_findings %}
- **{{ finding.category.value }}** — {{ finding.statement | sentence }}
  - Evidence class: `{{ finding.evidence_class.value }}`
  - Evidence: {% if finding.evidence_refs %}{{ finding.evidence_refs | join(', ') }}{% else %}_none cited_{% endif %}

  - Remediation: {{ finding.remediation or "Not yet determined." }}
{% endfor %}
{% endfor %}
{% else %}
No workload has an open blocking finding.
{% endif %}

## Evidence conflicts

{% if conflicts %}
Sources disagree on the following. The repository records the disagreement and does not
choose between them; resolution is a human decision.

| Subject | Attribute | Values | Owner |
| --- | --- | --- | --- |
{% for conflict in conflicts %}
| `{{ conflict.subject_id }}` | {{ conflict.attribute }} | {{ conflict.values | join(' / ') }} | {{ conflict.resolution_owner_role }} |
{% endfor %}
{% else %}
No unresolved conflicts between evidence sources.
{% endif %}

## Imported content flagged for review

{% if injection_flagged %}
{{ injection_flagged | length }} evidence record(s) contain directive-like text. The text
was treated as data and was not acted on. Review the source before trusting the record.

| Evidence | Source | Patterns |
| --- | --- | --- |
{% for record in injection_flagged %}
| `{{ record.id }}` | {{ record.source_ref }} | {{ record.injection_findings | map(attribute='pattern') | unique | join(', ') }} |
{% endfor %}
{% else %}
No imported content matched a prompt-injection pattern.
{% endif %}

## Workloads

| Workload | Platform | Version | Support | Environment | Criticality | Findings | Ready for a target decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
{% for workload in workloads %}
| {{ workload.name }} | {{ workload.source_platform.value }} | {{ workload.source_version or "unknown" }} | {{ workload.support_status.value }} | {{ workload.environment.value }} | {{ workload.criticality.value }} | {{ workload.findings | length }} | {{ workload.is_recommendation_ready | yes_no }} |
{% endfor %}

## Findings by workload

{% for workload in workloads %}
### {{ workload.name }} (`{{ workload.id }}`)

- Sizing: {% if workload.sizing.data_size_gb %}{{ workload.sizing.data_size_gb }} GB{% else %}unknown{% endif %}, {{ "measured" if workload.sizing.measured else "estimated" }}

- Service level: RPO {{ workload.service_level.rpo_minutes if workload.service_level.rpo_minutes is not none else "unstated" }}, RTO {{ workload.service_level.rto_minutes if workload.service_level.rto_minutes is not none else "unstated" }}{{ " (assumed)" if workload.service_level.is_assumption else "" }}
- Instance features in use: {% if workload.instance_features %}{{ workload.instance_features | join(', ') }}{% else %}none recorded{% endif %}

- Dependency discovery complete: {{ workload.dependency_discovery_complete | yes_no }}

{% if workload.findings %}
| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
{% for finding in workload.findings %}
| {{ finding.statement }} | {{ finding.category.value }} | {{ finding.severity.value }} | {{ finding.evidence_class.value }} | {{ finding.blocking | yes_no }} |
{% endfor %}
{% else %}
No findings recorded.
{% endif %}

{% endfor %}

## Risks raised

{% if risks %}
| Risk | Category | Likelihood | Impact | Severity | Owner |
| --- | --- | --- | --- | --- | --- |
{% for risk in risks %}
| {{ risk.title }} | {{ risk.category.value }} | {{ risk.likelihood.value }} | {{ risk.impact.value }} | {{ risk.severity.value }} | {{ risk.owner_role }} |
{% endfor %}
{% else %}
No risks were derived from this assessment.
{% endif %}

## What this document is not

It is not an approval, a commitment, or a statement of cost. Every recommendation
downstream of it requires architecture review, and every production change requires
documented approval from the business, application, database, security, and operations
owners.

> {{ revalidation_note }}
