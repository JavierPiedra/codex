# Task-specific contracts

Use only the section relevant to the requested prompt.

## Review, research, and planning

Specify the question or decision, permitted evidence, relevant date/version, and conclusion or plan artifact. Preserve read-only scope unless execution is separately authorized. Planning should expose known constraints, fixed choices, and unresolved dependencies without quietly authorizing implementation.

Require source locations or citations for material factual claims, separating direct evidence from inference. Allow an inconclusive result when evidence is inaccessible or conflicting; missing evidence is not proof of absence. If the receiving agent lacks browsing, explicitly bound the result to accessible inputs instead of requiring live research.

## Extraction and classification

Define the complete field contract: keys, types, allowed labels, unknown/null behavior, and required evidence. Any review flag or explanation mentioned in a rule must exist in that contract. Preserve caller-owned schemas; resolve a conflicting requirement without silently adding fields.

Provide an honest uncertainty path without forcing an unsupported label. Do not invent numerical confidence unless required by a defined contract; a self-reported score is not a calibrated probability.

Use schema enforcement when supported by the target host; otherwise require output validation. A valid format does not establish factual correctness.

## Summarization

Identify the audience and information that must survive compression, especially decisions, dates, quantities, owners, deadlines, caveats, and unresolved risks. Remove repetition before decision-relevant facts. Do not invent commitments, causes, or certainty to make the summary sound complete.
