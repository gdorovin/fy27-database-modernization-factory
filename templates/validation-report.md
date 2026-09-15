# Validation report — {{ report.wave_id }}

> {{ provenance_note }}

| | |
| --- | --- |
| Engagement | `{{ engagement.engagement_id }}` |
| Report | `{{ report.id }}` |
| Wave | `{{ report.wave_id }}` |
| Migration plan | `{{ report.migration_plan_id }}` |
| Executed | {{ report.executed_on }} |
| **Outcome** | **{{ report.outcome.value | upper }}** |
| Rollback triggered | {{ report.rollback_triggered | yes_no }} |

{% if is_no_go %}
> **Outcome: no-go.** The documented rollback path applies. This attempt did not succeed,
> and nothing in this report should be read as a partial success. Corrective issues are
> listed below and must be closed before another attempt is scheduled.
{% endif %}

## Result summary

| Result | Count |
| --- | --- |
| Pass | {{ counts['pass'] }} |
| Fail | {{ counts['fail'] }} |
| Not run | {{ counts['not-run'] }} |
| Not applicable | {{ counts['not-applicable'] }} |

## Blocking failures

{% if blocking_failures %}
Each of these forces a no-go on its own.

| Check | Category | Tolerance | Baseline | Observed |
| --- | --- | --- | --- | --- |
{% for check in blocking_failures %}
| {{ check.name }} | {{ check.category.value }} | {{ check.tolerance or "—" }} | {{ check.baseline or "—" }} | {{ check.observed or "—" }} |
{% endfor %}
{% else %}
No blocking check failed.
{% endif %}

## Blocking checks that did not run

{% if blocking_not_run %}
A check that did not run is not a pass. While any of these remain, `go` is not available.

{% for check in blocking_not_run %}
- {{ check.name }} ({{ check.category.value }})
{% endfor %}
{% else %}
Every blocking check was executed.
{% endif %}

## Business acceptance

| | |
| --- | --- |
| Business owner accepted | {{ report.business_acceptance.business_owner_accepted | yes_no }} |
| Application owner accepted | {{ report.business_acceptance.application_owner_accepted | yes_no }} |
| Accepted on | {{ report.business_acceptance.accepted_on or "—" }} |

{% if report.business_acceptance.conditions %}
Conditions:

{{ report.business_acceptance.conditions | bullets }}
{% endif %}

## All checks

{% for category, items in by_category.items() %}
### {{ category | titlecase }}

| Check | Result | Tolerance | Baseline | Observed | Blocking | Generated test |
| --- | --- | --- | --- | --- | --- | --- |
{% for check in items %}
| {{ check.name }} | {{ check.result.value }} | {{ check.tolerance or "—" }} | {{ check.baseline or "—" }} | {{ check.observed or "—" }} | {{ check.blocking | yes_no }} | {{ check.generated_test | yes_no }} |
{% endfor %}

{% endfor %}

{% if report.rollback_triggered %}
## Rollback

Reason: {{ report.rollback_reason }}

Evidence was preserved before the rollback ran, per the rollback plan. Review it before
scheduling another attempt.
{% endif %}

## Corrective work

{% if report.corrective_issue_ids %}
{% for issue_id in report.corrective_issue_ids %}
- `{{ issue_id }}`
{% endfor %}
{% else %}
No corrective issues are recorded.
{% endif %}

## Evidence

- Evidence: {% if report.evidence_refs %}{{ report.evidence_refs | join(', ') }}{% else %}_none cited_{% endif %}

- Playbook: `{{ report.playbook.path }}` v{{ report.playbook.version }}
