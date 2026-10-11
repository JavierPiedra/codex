# External Daybreak review handoff

Use when the main session cannot create the required native Daybreak reviewer.
Print the complete prompt in one copyable code block in the main chat; do not
only save a file or link to these instructions. Javier chooses the new or
existing Daybreak session and pastes the prompt there. Do not create or change
that session's model on his behalf.

Resolve the actual originating thread ID from the active session/tool context.
Never invent it or confuse it with a job, agent, or PR ID. If unavailable, ask
Javier for that one missing identifier before presenting a ready-to-send prompt.
Include the host ID when available. Fill the review target from inspected state:
repository, accessible checkout or PR, exact base and head SHA, and relevant
source pointers. For an uncommitted review use an immutable patch and hash;
identify any later commit that must be checked for equivalence.

Replace the fields below with actual context; omit irrelevant fields. Include
the accepted Goal and constraints directly, rather than depending on the other
session having inherited this conversation. Keep secrets, signed URLs, tokens,
and unnecessary personal or clinical data out of the handoff.

## Prompt template

```text
Act as the independent, read-only Daybreak reviewer for this Goal. Javier will
run this review in the Daybreak session he selected. Report the runtime/mode
information you can actually observe; do not infer it from this prompt.

Originating session: [actual thread ID]
Originating host: [actual host ID, if available]
Repository and review location: [repository; accessible checkout and/or PR URL]
Exact review target: [base SHA -> head SHA, or immutable patch path and hash]

Accepted Goal and acceptance criteria:
[Concrete outcome and criteria, including authoritative amendments]

Scope and governing sources:
[Permitted review scope, exclusions, relevant AGENTS.md/contracts/docs]

Evidence supplied by the orchestrator:
[Checks and results; label simulated, reported, live, and unrun evidence]

Review the exact target for correctness, contract compliance, security,
operational behavior, unnecessary complexity, and missing acceptance evidence.
Use targeted read-only inspection. Do not edit files, modify Git/PR/issue state,
merge, deploy, mutate data, call live providers, or launch additional agents.
Do not treat a missing artifact or inaccessible target as approval: report
precisely what is missing. Reuse this session for subsequent re-review.

Include your actual reviewer thread ID and host ID if available so the
originating session can return corrections to this same review session. State
when those identifiers are unavailable rather than inventing them.

Return a verdict with the exact reviewed SHA/hash, actionable findings with
file/line and consequence, checks you actually performed, supplied evidence you
did not independently verify, and unresolved acceptance gaps. Separate defects
from optional preferences. Do not claim runtime observations you cannot verify.

Send that full verdict back to the originating session [actual thread ID]
using the available cross-session messaging tool (in Codex:
send_message_to_thread, with that threadId and the originating hostId if known).
This handoff explicitly authorizes that review-result message only. Also show
the verdict here. If the tool is unavailable or sending fails, state that it
was not delivered and print the complete verdict so Javier can paste it into
the originating session. Never claim delivery without a successful tool result.
```

## Receiving the review

Correlate the verdict with the originating Goal and the exact reviewed artifact.
Record whether the reviewer session was designated by Javier or its Daybreak
mode was independently observed; do not require inaccessible native metadata
from a manually selected session. If code changed, send the delta and new head
to the same reviewer before treating approval as current. Consolidate findings
for the existing writer. A pending handoff does not authorize bypassing review,
merging, deployment, or Goal completion.
