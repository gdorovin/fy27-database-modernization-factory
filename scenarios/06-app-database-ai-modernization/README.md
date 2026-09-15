# Scenario 06 — Application, database, and conditional AI attachment

**Prevents:** promising an intelligent outcome the data cannot support.

## The situation

A services business modernizing a long-lived application alongside its database, with a
stated ambition to put an assistant in front of customer data. Two open questions have no
answers: which system is the system of record for a customer address, and who owns customer
data quality afterwards.

| Workload | Notable |
| --- | --- |
| Customer master | Candidate system of record; ownership not agreed; GDPR scope |
| Case management | Consumed by the application; depends on Customer master; GDPR scope |
| Reporting copy | Nightly copy produced by a job; duplicates customer attributes |

## What the factory does, and why

**The database work is unremarkable, and that is the point.** Both production workloads go
to database scope. No instance-scoped dependency exists, nothing is unusual, and the
migration is the easy half of this engagement.

**Nothing in the generated output promises an AI outcome.** No document says "AI-ready",
mentions vector search, or names an assistant product. The scenario asserts their *absence*,
which is an unusual kind of test and the reason this scenario exists: the failure mode here
is enthusiasm, not error.

**The brief says what has not been measured.** Data ownership is an open question and the
baseline for it is unknown, so the executive brief states that rather than smoothing over
it. A sponsor who reads "not measured" can fund measuring it. A sponsor who reads nothing
assumes it is handled.

**Compliance scope drives real work.** Both regulated workloads are in GDPR scope, so the
wave-2 validation plan carries a control-evidence check. Evidence is collected during
validation rather than reconstructed afterwards, because reconstructed evidence is an
argument rather than a record.

**Application impact is assessed in both directions.** The decisions record that no
application change is implied by the target itself, while still requiring a review of
connection handling, retry logic, and driver versions. "No change required" and "no review
required" are different claims.

**The reporting copy is a separate question.** It duplicates customer attributes, which is
exactly the kind of derived copy where deletion obligations quietly fail. It moves in its own
wave, and the `ai-data-readiness` skill treats uncontrolled copies as a readiness blocker.

## Wave plan

| # | Wave | Contents |
| --- | --- | --- |
| 1 | Pilot | Reporting copy — downstream, pre-production, safe to fail |
| 2 | Business critical | Customer master and Case management, coupled |

## What would break this

- Any generated document claiming AI readiness.
- Naming an assistant or analytics product in a target decision.
- An executive brief that omits what has not been measured.
- Dropping the GDPR control-evidence check because the migration looked clean.
