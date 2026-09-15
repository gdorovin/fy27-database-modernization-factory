# Validation plan — {{ wave.name }}

> {{ provenance_note }}

| | |
| --- | --- |
| Engagement | `{{ engagement.engagement_id }}` |
| Wave | `{{ wave.id }}` |
| As at | {{ as_of }} |
| Checks | {{ checks | length }} |
| Blocking checks | {{ blocking_count }} |

## How this plan is used

Each check records an observation against a tolerance. Three rules decide the outcome:

1. A blocking check that fails forces a **no-go**.
2. A blocking check that has not run forbids a **go**. Not run is not a pass.
3. Generated tests are supporting evidence. A `go` cannot rest on them alone.

Checks without a tolerance are judgement calls and name the owner who makes the judgement.

## Checks

{% for category, items in by_category.items() %}
### {{ category | titlecase }}

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
{% for check in items %}
| {{ check.name }} | {{ check.method }} | {{ check.tolerance or "Judgement call" }} | {{ check.blocking | yes_no }} |
{% endfor %}

{% endfor %}

## Recording results

For every check, record:

- the observed value,
- the result (`pass`, `fail`, `not-run`, `not-applicable`),
- an evidence reference,
- and, where the result is a judgement call, who made it.

The completed record is a validation report artifact, which is what a go / no-go decision
is taken against.
