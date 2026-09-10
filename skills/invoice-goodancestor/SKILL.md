---
name: invoice-goodancestor
description: Prepare Javier's monthly Good Ancestor invoice by collecting Clockify timer hours, reading client-filtered WakaTime project and branch hours from the API, calculating totals, and producing the exact chat-ready description block. Use for Good Ancestor invoicing, monthly invoice hours, WakaTime client summaries, Clockify monthly reports, or invoice description output.
---

# Invoice Good Ancestor

## Required Input

Require a concrete target month and year, such as `July 2026`.

Use the Browser plugin for Clockify. If Clockify requires authentication, ask Javier to log in and continue when ready. Do not request credentials.

Do not use the WakaTime UI. Read WakaTime through `scripts/wakatime_client_hours.py`, which retrieves the API key from macOS Keychain. Do not print, log, or store the API key in files.

Do not edit the Good Ancestor Google Sheet unless Javier explicitly requests that separate action.

## Configuration

Use these fixed Good Ancestor settings:

- WakaTime client ID: `018ef80e-a87c-46fe-a05b-b800113925e0`
- Keychain service: `codex.invoice-goodancestor.wakatime`
- Keychain account: current macOS user

If the key is missing, ask Javier to run:

```bash
python3 /Users/javierpiedra/.codex/skills/invoice-goodancestor/scripts/wakatime_client_hours.py --store-key
```

The script prompts for the key without echoing it.

## Ordered Workflow

### Phase 0: Date Bounds

Run `scripts/invoice_math.py` with the target month to obtain exact start and end dates.

### Phase 1: Clockify Timer Hours

1. Open `https://app.clockify.me/reports/summary` with the Browser plugin.
2. Select the exact target month and verify the visible date range.
3. Record every Clockify row related to Good Ancestor. Do not use a fixed project allowlist.
4. Use a concise invoice label for each row, for example `Meets - Good Ancestor` as `Meets` and `Planning - Good Ancestor` as `Planning`.
5. Preserve seconds when available, convert the complete duration to decimal hours, and normalize each value with `scripts/invoice_math.py`.

### Phase 2: WakaTime API Hours

Run:

```bash
python3 /Users/javierpiedra/.codex/skills/invoice-goodancestor/scripts/wakatime_client_hours.py \
  --start YYYY-MM-DD \
  --end YYYY-MM-DD \
  --client 018ef80e-a87c-46fe-a05b-b800113925e0
```

Use every non-zero project returned by the client-filtered summaries endpoint. The script then queries the same client-filtered date range once per returned project because WakaTime only includes branch data when a project filter is present. Preserve every aggregated branch and its rounded decimal hours. Do not maintain or apply a project allowlist.

Treat API errors, an absent `data` array, or an empty result as a blocking verification failure. Do not substitute cached values from an earlier invoice.

### Phase 3: Totals and Chat Report

1. Pass every normalized Clockify row and WakaTime project total to `scripts/invoice_math.py`. The helper always adds the fixed 5-hour Codex Pro subscription equivalent and 10 Research/Learn hours.
2. Print the final description block and `TOTAL` in chat immediately.
3. Do not create or edit WakaTime invoice rows or Google Sheet rows.

## Calculation Rules

- Convert complete timer durations to decimal hours before totaling.
- Round each Clockify row, WakaTime project, and branch to two decimals with half-up invoice rounding.
- Always add `Codex: 5.00` as the fixed billable equivalent of Javier's Codex Pro subscription.
- Always add `Research/Learn: 10.00` as fixed research, learning, or training time.
- Sum normalized Clockify rows, `Codex: 5.00`, `Research/Learn: 10.00`, and normalized WakaTime project hours for `TOTAL`.

## Description Format

```text
TOTAL {Sum of Normalized Timer Hours + WakaTime Project Hours}

Timer
{Clockify Label}: {Normalized Decimal Hours}

Codex: 5.00
Research/Learn: 10.00

{Project Name} - {Project Hours}
{Branch Hours} {Branch Name}
```

Repeat timer, project, and branch lines for every returned item. Preserve exact project and branch names.
