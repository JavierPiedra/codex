# Problem Statement Template

Use this as the default shape unless the user wants a different format.

## Default File Placement

- Write the document to a Markdown file in the current project by default.
- If the user supplied a path, use that path.
- Otherwise follow the project's existing convention for planning, specs, or
  notes.
- If there is no clear convention, use a root-level filename such as
  `problem-statement-<initiative-slug>.md`.

## Template

```md
# {Initiative Title}

Read first:
- {project planning or process docs, if they exist}
- {relevant product or operating docs, if they exist}
- {referenced issue notes or discussion artifacts}

## Problem Statement

{Describe the actual pain in product or engineering terms. Lead with the user
impact, response-time problem, quality gap, or contract confusion that matters.
Do not lead with a technical invariant that is functioning correctly.}

## Current Behavior to Verify

- {Concrete behavior that should be verified in the current workflow or system}
- {Observed contract shape today}
- {Known artifacts that define the current behavior}

## Desired Direction

- {Requirement already decided by the user}
- {Quality bar the new design must preserve or improve}
- {User-visible behavior that should result}
- {Important specialized output or external API targeting requirement}

## Locked Decisions

- {Decision the user already made and Pro should not reopen}
- {Explicit out-of-scope item}
- {Intentional simplicity constraint}

## Questions Pro Must Resolve

List only questions explicitly delegated to Pro by the owner.

1. {Higher-order design or contract question}
2. {Lifecycle/state-model question}
3. {Quality-preservation or failure-handling question}
4. {Cross-surface or downstream side-effect question}

## Constraints

- {Keep it simple}
- {Respect project guidance}
- {Preserve safety and correctness}
- {Do not block user-facing flow if that is a fixed requirement}

## Out of Scope

- {Adjacent workflow or edit flow not owned by this PRD}
- {Broader redesigns that are not required to solve the current problem}

## Expected PRD Outcome

Pro should produce a PRD that defines:
- {new request flow}
- {state/readiness model}
- {process, job, or automation behavior if applicable}
- {quality and contract decisions}
- {validation, rollout, and rollback requirements}
```

## Checklist

- Does the problem statement describe the real pain rather than an expected
  invariant?
- Were all material owner decisions resolved before drafting or explicitly
  delegated to Pro?
- Are all user-decided behaviors encoded as requirements instead of open
  questions?
- Are the remaining questions high-level enough that Pro can design the right
  solution?
- Did you inspect downstream side effects for any state, workflow, or contract
  change?
- Are ambiguous terms defined inline?
- If there is contract drift, did you name the exact stale source artifact?
- If multiple issues are bundled together, is the shared initiative clear and
  the scope still tight?

## Patterns From Successful Refinement

- Move low-level design forks out of the question list when the user wants Pro
  to solve the architecture.
- Turn blunt user corrections into locked decisions or desired-direction bullets.
- Pull in downstream behavior whenever shared states or labels are reused.
- Clarify exact numeric or contract expectations when docs are stale or vague.
- Separate internal failure handling from user-facing behavior when those should
  not be coupled.
