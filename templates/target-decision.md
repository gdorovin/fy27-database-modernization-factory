# Target decisions — {{ engagement.customer_alias }}

> {{ provenance_note }}

| | |
| --- | --- |
| Engagement | `{{ engagement.engagement_id }}` |
| As at | {{ as_of }} |
| Recommendations | {{ decisions | length }} |
| Workloads with no recommendation | {{ unresolved | length }} |

Every entry below is a **recommendation**, not a decision. It becomes a decision when an
architecture review records an approval against it, and the approver cannot be the author.

## Workloads with no recommendation

{% if unresolved %}
These workloads have open blocking findings. No target is proposed for them, because a
target chosen from incomplete evidence is a guess wearing a decision's clothes.

{% for workload_id in unresolved %}
- `{{ workload_id }}` — {{ workload_names.get(workload_id, workload_id) }}
{% endfor %}
{% else %}
Every workload received a recommendation.
{% endif %}

## Recommendations

{% for decision in decisions %}
### {{ workload_names.get(decision.workload_id, decision.workload_id) }} (`{{ decision.workload_id }}`)

| | |
| --- | --- |
| Recommended target | **{{ decision.recommended_target.value }}** |
| Disposition | {{ decision.disposition.value }} |
| Status | {{ decision.status.value }} |
| Confidence | {{ decision.confidence.value }} |
| Requires application change | {{ decision.requires_application_change | yes_no }} |
| Requires schema or code conversion | {{ decision.conversion_required | yes_no }} |

{{ decision.rationale | sentence }}

#### Options considered

| Target | Verdict | Score | Reasoning |
| --- | --- | --- | --- |
{% for option in decision.considered_options %}
| {{ option.target.value }} | {{ option.verdict.value }} | {{ option.score }} | {{ option.rationale }} |
{% endfor %}

{% set rejected = decision.rejected_alternatives %}
{% if rejected %}
#### Why the alternatives were not chosen

{% for option in rejected %}
- **{{ option.target.value }}** — {{ option.rationale | sentence }}
{% if option.blockers %}
  - Blockers: {{ option.blockers | join('; ') }}
{% endif %}
{% endfor %}
{% endif %}

#### Compatibility

{{ decision.compatibility_notes | bullets }}

#### Operations

{{ decision.operational_notes | bullets }}

#### Security

{{ decision.security_notes | bullets }}

#### Performance

{{ decision.performance_notes | bullets }}

#### Data residency

{{ decision.sovereignty_notes | bullets }}

#### Application impact

{{ decision.application_impact | bullets }}

#### Downtime approach

| | |
| --- | --- |
| Method | {{ decision.downtime_approach.method }} |
| Expected class | `{{ decision.downtime_approach.expected_class.value }}` |
| Basis | {{ decision.downtime_approach.basis }} |
| Measured | {{ decision.downtime_approach.measured | yes_no }} |

{% if not decision.downtime_approach.measured %}
The downtime class is provisional. It stays provisional until a rehearsal produces a
measured figure; no stronger claim is available before then.
{% endif %}

#### Cost inputs

{% if decision.cost_inputs %}
| Label | Amount | Period | Source | Estimate |
| --- | --- | --- | --- | --- |
{% for cost in decision.cost_inputs %}
| {{ cost.label }} | {{ cost.amount }} {{ cost.currency }} | {{ cost.period }} | {{ cost.source }} | {{ cost.is_estimate | yes_no }} |
{% endfor %}
{% else %}
No cost inputs were supplied. The repository does not invent cost figures; the business
case needs them from the customer or the account team.
{% endif %}

#### Evidence and assumptions

- Evidence: {% if decision.evidence_refs %}{{ decision.evidence_refs | join(', ') }}{% else %}_none cited_{% endif %}

{% if decision.assumptions %}
- Assumptions:
{% for assumption in decision.assumptions %}
  - {{ assumption.statement }} (owner: {{ assumption.owner_role }}; settle by: {{ assumption.validation_step }})
{% endfor %}
{% else %}
- Assumptions: none recorded.
{% endif %}
{% if decision.open_questions %}
- Open questions:
{% for question in decision.open_questions %}
  - {{ question.question }} (owner: {{ question.owner_role }}{{ ", blocking" if question.blocking else "" }})
{% endfor %}
{% endif %}

{% endfor %}

> {{ revalidation_note }}
