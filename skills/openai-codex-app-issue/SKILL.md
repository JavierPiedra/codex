---
name: openai-codex-app-issue
description: Draft privacy-safe, copy-pasteable content for the official OpenAI Codex App bug form. Use when Javier wants to report a Codex desktop bug or organize its reproduction and diagnostics; never publish without a separate request.
---

# OpenAI Codex App Issue

Generate concise, evidence-based field sections for
`https://github.com/openai/codex/issues/new?template=1-codex-app.yml`.
This skill produces content only. Creating or submitting a GitHub issue needs a
separate explicit request.

## Fields and evidence

Prepare a suggested title, Codex App version, subscription, platform, issue,
reproduction steps, expected behavior, and additional information. Version,
subscription, issue description, and reproduction steps are required by the
current form; mark missing values and ask only for facts needed to make the
report useful.

Extract only observed details: affected surface, actual and expected behavior,
smallest reliable reproduction, frequency, first occurrence/regression,
visible errors, and relevant session or usage information. Distinguish facts
from hypotheses and write `Unknown` when evidence is absent.

For permitted read-only macOS inspection, use:

```bash
defaults read /Applications/Codex.app/Contents/Info CFBundleShortVersionString
defaults read /Applications/Codex.app/Contents/Info CFBundleVersion
uname -mprs
sw_vers
```

For Windows, use the command required by the official form:

```powershell
"$([Environment]::OSVersion | ForEach-Object VersionString) $(if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" })"
```

Use the About dialog when bundle metadata is unavailable. Never guess the
subscription.

## Reproduction and redaction

Write numbered steps from a clean state. Include the starting page/panel,
exact actions and inputs, divergence point, restart/new-task/repository effects,
and the smallest non-sensitive example. Include code only when it is required.

Before output, remove names, email addresses, account identifiers, private
repository/company/customer/project names, username-bearing paths, unrelated
prompts/source/logs/URLs/IDs, tokens, keys, and unrelated screenshot context.
Keep a session ID only when relevant to OpenAI diagnostics and Javier has not
asked to omit it. Prefer text over screenshots; if a screenshot is necessary,
state the crop and redaction boundary.

Check that actual and expected behavior are distinct, reproduction is
deterministic or marked intermittent, factual claims have evidence, available
errors are fully included after redaction, title names the symptom and surface,
and no root-cause theory is presented as fact. If required information is
missing, include it only in the `Missing information` section.

## Output

Read [templates/issue-output.md](./templates/issue-output.md) and return its
sections in the same order. Each heading must be followed by a `text` code fence
containing only the value for that GitHub field. Keep the fields independently
copy-pasteable; do not combine the report into one code fence or put commentary
inside a field.

If Javier asks for a duplicate check and GitHub read access is available,
search `openai/codex` using the affected surface, visible symptom, and exact
error text. Report likely matches separately. Do not comment, react, create an
issue, or publish the draft without explicit authorization.

If Javier later explicitly asks to publish, reread the final visible form,
verify that its fields have not changed, show or summarize the sanitized
content, and submit only within that active request.
