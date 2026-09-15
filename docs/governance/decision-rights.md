# Decision rights

Who decides what, and — more usefully — who may not.

## The table

| Decision | Proposed by | Decided by | May not decide |
| --- | --- | --- | --- |
| Engagement scope and outcomes | Engagement orchestrator | Business owner with engagement lead | Any agent |
| Workload classification | Estate assessor | Database owner | The proposing agent |
| Azure target per workload | Target architect | Architect with application owner | Target architect |
| Business case acceptance | Value advisor | Business owner | Any agent |
| Wave composition and sequence | Migration planner | Delivery lead with application owners | Any agent |
| Policy exception | The requester | Security owner and architect | The requester |
| **Go / no-go for cutover** | Validation engineer supplies evidence | **All five owner roles** | Any agent |
| Rollback trigger | Validation engineer | Delivery lead, against documented thresholds | Any agent |
| Risk acceptance | Anyone | The named accepting role, with a date | Any agent |
| Decommissioning the source | Migration planner | Business owner, after hypercare | Any agent |
| Playbook change | Any contributor | Architect owner **and** security owner | A single reviewer |
| Contract change | Any contributor | Architect owner and security owner | A single reviewer |

## Three rules that cut across everything

**No self-approval.** The author of an artifact may not approve it. An agent may never
approve agent-authored work at all. Enforced in `models/approval.py`; an approval naming the
author as approver will not construct.

**Cutover needs all five.** Business, application, database, security, operations. The count
is checked, not assumed, because four-of-five is exactly what happens when someone is on
leave and the date is fixed.

**Agents propose, humans decide.** No agent can move an artifact to `approved`. The strongest
statement available to an agent is the governance reviewer's "ready for human approval".

## The five cutover roles

| Role | Answers |
| --- | --- |
| Business owner | Is the outcome worth the risk, tonight? |
| Application owner | Will the applications work afterwards? |
| Database owner | Is the data correct and reconciled? |
| Security owner | Does posture hold? |
| Operations owner | Can we run it, and can we roll back? |

Each answers a question the others cannot. That is why the count is five and not "the senior
person present".

## Approvals in practice

An approval records the artifact id, its **content hash**, the approving role, the principal,
a timestamp, the decision, and any conditions.

The content hash is the part that earns its place. Edit an approved artifact and the approval
becomes stale automatically — which closes the gap between what was approved and what is in
the file at 17:00 the day before a cutover.

## Risk acceptance

A risk may be accepted. It must name the accepting role and the date.

Unattributed acceptance is not acceptance; it is a risk that stopped being discussed. The
model rejects an accepted risk with no `accepted_by_role` and `accepted_on`.

## Escalation

| Situation | Escalate to |
| --- | --- |
| Two evidence sources disagree | Database owner |
| Two options score within a few points | Architecture review |
| Blocking finding open at a wave gate | Delivery lead, then sponsor |
| An approval role is unavailable | Sponsor — naming a deputy is their decision |
| The date is at risk | Sponsor, with the scope-versus-gate trade stated explicitly |
| A boundary was crossed | Security owner and delivery lead |

That fifth row is worth rehearsing before you need it. The honest framing is: *"we can move
fewer workloads on the date, or the same workloads later. We cannot validate less."*

## Changing this table

An architect and a security owner, per `CODEOWNERS`. The role tables in
`validators/agent.py` and `models/base.py` must change with it, or the documentation and the
enforcement drift — and the enforcement is what people actually experience.
