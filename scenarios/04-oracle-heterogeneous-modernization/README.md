# Scenario 04 — Oracle heterogeneous modernization

**Prevents:** treating a conversion percentage as a compatibility verdict.

## The situation

A manufacturer under Oracle licensing and audit pressure. Three schemas of differing
complexity, one of them behind a vendor-supported plant application whose support terms
nobody has reviewed. The customer has asked for an honest disposition per system rather than
a programme that assumes everything moves.

| Workload | Conversion assessed against | Result |
| --- | --- | --- |
| Order management | PostgreSQL Flexible Server (Oracle-to-PostgreSQL conversion tooling; SSMA has no PostgreSQL path) | 812 automatic, 133 manual, 20 errors |
| Finance ledger | Azure SQL Managed Instance (SSMA for Oracle) | 498 automatic, 76 manual, 12 errors |
| Plant maintenance | *Nothing* | No assessment exists |

## What the factory does, and why

**Three schemas, three different answers.** Order management goes to PostgreSQL, Finance
ledger to instance-scoped SQL, Plant maintenance keeps its engine and moves to Oracle-managed
infrastructure inside Azure. There is no estate-wide Oracle answer, and forcing one is how
the difficult schema sinks the whole programme.

**A conversion result does not transfer between destinations.** Order management was assessed
against PostgreSQL, so *only* PostgreSQL is comparable for it. Managed Instance is blocked
with the reason stated. This is the scenario's sharpest assertion: without it, a tie-break
could recommend a destination nobody ever assessed, and the comparison would look just as
confident.

**No assessment means no *conversion* recommendation.** Every cross-engine destination for
Plant maintenance is blocked, because recommending one for unread PL/SQL behind a
vendor-supported application would be a guess with a score attached. What remains is compared
honestly: Oracle Database@Azure keeps the engine, removes the hardware and support risk, and
outscores retention. The decision record says in as many words that it is a relocation and a
licensing decision, not a modernization of the engine, and that regional availability and
commercial terms are account-team inputs with a date on them.

**Keeping the engine is the fallback, never the default.** For the two schemas whose
conversion *has* been assessed, Oracle Database@Azure is compared, scored below the assessed
destination, and recorded as rejected with the reason: the engagement has invested in leaving
the engine, and keeping it would retain the licence position that investment exists to change.

**The failure mode is named explicitly.** The generated documents state that automatic
compatibility is not claimed, and that a conversion percentage describes tool output only.
That phrasing exists because "84% automatic" is the number that gets quoted in a steering
pack, and the 133 objects needing hand-work are the number that decides the timeline.

**Conversion implies code change, which implies testing.** Both moving schemas carry
`conversion_required`, a `refactor` disposition, a conversion task in the plan, and — in the
validation plan — a business validation check where named users exercise agreed scenarios and
compare results. Nothing else substitutes for that.

## Wave plan

| # | Wave | Contents |
| --- | --- | --- |
| 1 | Pilot | Order management |
| 2 | Business critical | Finance ledger, Plant maintenance |

Plant maintenance moves without conversion; its plan has no conversion task and its
validation plan has no converted-behaviour check, because nothing was converted. Which wave
it lands in follows from its risk rank; read `migration-waves.md` rather than this table if
the two ever disagree.

## What would break this

- Recommending a target that was never assessed for that schema.
- Recommending a cross-engine destination for Plant maintenance.
- Recommending Oracle Database@Azure over a destination whose conversion was assessed.
- The phrase "fully compatible" appearing anywhere.
- A plan without a conversion task or business validation.
