# Diagrams

Diagram source lives in the Markdown page it illustrates, as Mermaid, so it cannot drift
away from the prose that explains it.

| Diagram | Page |
| --- | --- |
| Modernization lifecycle, with approval gates | [README](../../../README.md) |
| Repository architecture | [README](../../../README.md), [overview](../overview.md) |
| Evidence and artifact flow | [README](../../../README.md), [artifact flow](../artifact-flow.md) |
| Agent orchestration | [README](../../../README.md), [agent architecture](../agent-architecture.md) |
| Layer dependency map | [overview](../overview.md) |
| Pipeline stages | [overview](../overview.md) |
| Skill map | [skill architecture](../skill-architecture.md) |
| Handoff sequence | [agent architecture](../agent-architecture.md) |
| Status lifecycle | [artifact flow](../artifact-flow.md) |
| Conflict handling | [artifact flow](../artifact-flow.md) |
| Ingestion boundary | [security architecture](../security-architecture.md) |
| Approval gates | [risk and approvals](../../governance/risk-and-approvals.md) |

## Why inline rather than separate files

A diagram in its own file drifts. Someone changes the implementation, updates the prose,
and does not open the `.mmd` file three directories away. The result is a diagram that is
confidently wrong, which is worse than none because readers believe it.

Inline Mermaid renders on GitHub and in VS Code, diffs as text, and sits directly under the
paragraph that would have to change with it.

## Conventions

- Keep them small. A diagram with thirty nodes is a wall, not an explanation.
- A diagram earns its place by showing something prose cannot: a cycle, a fan-out, a gate.
- Colour carries meaning, consistently:

  | Fill | Means |
  | --- | --- |
  | `#fff3cd` amber | A human gate |
  | `#f8d7da` red | A failure path |
  | `#d4edda` green | A human actor |
  | `#e2e3e5` grey | A non-editing agent |

- Update the diagram in the same change as the implementation. A stale diagram is a defect.

## This directory

Reserved for diagram source that cannot be inline — an exported image for a slide, or a
rendering that Mermaid cannot express. Nothing needs it yet, and the convention has an
obvious home for when something does.
