# API and tool integration

## API templates and runtime settings

Keep stable application rules in the host's appropriate instruction message and variable task data separate. For pasteable agent prompts, plain sections suffice. Do not invent message-role support or duplicate policies the host already enforces.

Include runtime notes only when requested or necessary for integration. Verify the exact model and host in current official documentation before supplying configuration parameters or supported values. API parameters, Codex settings, and UI labels are not interchangeable. Label untested configurations as candidates, not optimal settings; do not recommend a different model or effort solely because a task is difficult.

## Tools and repeated workflows

Name only available tools or verified discovery mechanisms. Specify the retrieval target, authorized actions, retained evidence, completion condition, and a proportional retry or no-progress boundary. Do not repeat an unchanged failure indefinitely or reread completed results without a concrete need.

Use existing deterministic utilities or code for mechanical filtering, sorting, joins, arithmetic, and validation when they reduce work. Do not assume Programmatic Tool Calling is available. When explicitly supported and useful, bound its processing stage and retain the evidence needed for judgment. Keep approvals and meaning-dependent decisions outside mechanical processing.
