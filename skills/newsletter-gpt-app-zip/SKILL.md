---
name: newsletter-gpt-app-zip
description: Create a zip archive of the newsletter-gpt repository by including only files that are not ignored by `.gitignore` using Git ignore rules. Use when asked to package this repo for upload as `newsletter_gpt_app`, or when a clean distributable snapshot of `/Users/javierpiedra/Desktop/goodancestor/newsletter-gpt` is required.
---

# Newsletter Gpt App Zip

## Overview

Create `newsletter_gpt_app.zip` at the repository root from files that are
not ignored by `.gitignore`. Use the bundled script for deterministic,
repeatable packaging.

## Workflow

1. Verify the target repository path is
   `/Users/javierpiedra/Desktop/goodancestor/newsletter-gpt` unless the user
   requests a different path.
2. Run:
   `python3 newsletter-gpt-app-zip/scripts/create_newsletter_gpt_zip.py`
3. Confirm the output archive exists at:
   `/Users/javierpiedra/Desktop/goodancestor/newsletter-gpt/newsletter_gpt_app.zip`
4. Report file count and output size from the script output.

## Constraints

- Build the include set from:
  `git -C <repo> ls-files -c -o --exclude-standard -z`
- Exclude the output archive path so reruns do not self-include the zip.
- Overwrite existing `newsletter_gpt_app.zip` atomically.
- Keep archive paths relative to repository root.

## Script

Use `scripts/create_newsletter_gpt_zip.py` with optional flags:

- `--repo-root` to override repository directory.
- `--output` to override output zip path.
