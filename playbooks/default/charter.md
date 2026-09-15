# Default playbook — charter

version: 1.0.0

The playbook is the enterprise decision and governance contract. It records **decisions**:
what is approved, what is prohibited, what must hold. It does not record procedures —
those live in Agent Skills, where they can be improved without a governance review.

This is the baseline. Copy it to `playbooks/<name>/` and change what the customer's
context demands. Do not edit this one for a single engagement.

## Scope

Applies to every database workload assessed, planned, or migrated through this
repository, and to every artifact those activities produce.

In scope:

- Relational database workloads on SQL Server, PostgreSQL, MySQL, MariaDB, and Oracle.
- The evidence used to justify a target, a wave, or a cutover decision.
- The approval trail for any change to a customer environment.

Out of scope:

- Application architecture beyond its coupling to the database.
- Non-relational data stores, which need their own playbook.
- Commercial terms, funding, and licensing negotiations.

## Outcomes

The outcomes this playbook exists to protect, in priority order. When two conflict, the
higher one wins and the trade is recorded as an ADR.

1. **No unreviewed change reaches production.** Every environment-changing action carries
   a recorded approval and a rollback path.
2. **Every recommendation is traceable to evidence.** A recommendation that cannot name
   its evidence is withdrawn, not defended.
3. **Security and compliance posture improves, or is unchanged.** Modernization that
   weakens posture is not modernization.
4. **Operational burden falls.** If the target costs more to run than the source, that is
   a finding, not a detail.
5. **The customer can audit the reasoning later.** Including the options that were
   rejected, and why.

## Principles

**Evidence before recommendation.** A workload with an open blocking finding gets no
target. Saying "we don't know yet" is cheap; revisiting a funded decision is not.

**Unknown is a value.** An unknown version, dependency, or downtime budget is recorded as
unknown and owned by someone. It is never filled in to make a document look finished.

**Rejected options are part of the decision.** A comparison showing one option is a
preference. The reasoning that survives review is the reasoning that shows its working.

**Retain, retire, and replace are outcomes.** A factory that can only say "migrate" is a
sales script. Some workloads should not move, and some should stop existing.

**No claim without a basis.** No zero-downtime claim. No saving against an unmeasured
baseline. No compatibility assertion across engine families without conversion evidence.

**Conflicts stop the line.** When two sources disagree, the conflict is surfaced and a
human resolves it. The tooling does not pick a winner.

**Separation of duties.** The party that proposes does not approve. This holds for people
and for agents, without exception.

## Stakeholders

| Role | Responsibility | Holds decision rights over |
| --- | --- | --- |
| Business owner | Owns the outcome and the funding | Scope, business case, acceptance, cutover |
| Application owner | Owns the consuming applications | Application impact, dependencies, cutover |
| Database owner | Owns the estate and its health | Classification, sizing, data reconciliation, cutover |
| Security owner | Owns posture and compliance | Policy, exceptions, security acceptance, cutover |
| Operations owner | Owns run-state and incident response | Availability design, runbooks, rollback, cutover |
| Architect | Owns the target architecture | Target decisions, ADRs, playbook changes |
| Delivery lead | Owns execution | Wave composition, schedule, go / no-go facilitation |

## Decision rights

| Decision | Proposed by | Decided by | Never decided by |
| --- | --- | --- | --- |
| Engagement scope and outcomes | Engagement orchestrator | Business owner and engagement lead | Any agent |
| Workload classification | Estate assessor | Database owner | The proposing agent |
| Azure target per workload | Target architect | Architect with application owner | Target architect |
| Business case acceptance | Value advisor | Business owner | Any agent |
| Wave composition | Migration planner | Delivery lead with application owners | Any agent |
| Policy exception | Requester | Security owner and architect | The requester |
| Go / no-go for cutover | Validation engineer supplies evidence | All five owner roles | Any agent |
| Rollback trigger | Validation engineer | Delivery lead, against documented thresholds | Any agent |
| Playbook change | Any contributor | Architect owner and security owner | A single reviewer |

Two rules cut across all of the above:

- **No self-approval.** The author of an artifact may not approve it, and an agent may
  never approve an agent-authored artifact.
- **Cutover needs all five.** Business, application, database, security, and operations.
  Four is not a cutover approval.
