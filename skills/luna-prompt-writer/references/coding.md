# Coding implementation handoffs

Unless the user assigns a different role, the orchestrator investigates and chooses the design; Luna implements and verifies the approved contract. Permit ordinary local coding decisions within that contract. If a missing architectural decision changes the implementation, identify it instead of assigning Luna an implicit redesign.

Include the approved behavior, relevant files or verified discovery anchors, allowed scope, invariants, acceptance cases, and appropriate checks. Retain technical decisions that prevent incorrect implementation even when they require a longer prompt. Require the smallest coherent change under applicable repository instructions; do not weaken tests to manufacture a pass.

Use supplied or verified test commands. Otherwise instruct Luna to locate established checks in repository configuration. Distinguish checks that passed, failed, or could not run; tests do not establish manual QA, deployment, or runtime behavior.

Define the entire authorized completion point. If the request includes implementation, running it, inspecting the result, and fixing failures, include those outcomes rather than stopping at a first draft. Reuse valid evidence for unchanged work and rerun affected checks after fixes.

Preserve permission already given for in-scope work. Distinguish local edits from remote writes, deployment, destructive operations, and scope changes according to the user's actual authorization. Keep any explicitly required action-time approval checkpoint.

For a repair loop, stop when new evidence requires an unapproved design or scope decision, or when another attempt would repeat the same failure without a new cause-specific hypothesis. Report the blocker, evidence, attempted remedy, and decision needed. Do not invent a universal retry count or broaden the workstream to avoid reporting a blocker.
