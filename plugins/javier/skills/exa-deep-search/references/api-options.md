# Search API options

Audited on 2026-10-11 against Exa's official
[OpenAPI specification](https://exa.ai/docs/exa-spec.yaml),
[Search reference](https://exa.ai/docs/reference/search), and
[Deep Search guide](https://exa.ai/docs/search/deep-search).
This skill covers `/search` in `deep` and `deep-reasoning`. Other API endpoints
and search modes are outside its scope.

## Complete requests

Use `search --request-file <request.json>` for all options below. JSON uses the
API's **camelCase** names, rather than the Python SDK's snake_case names. Do not
combine a request file with the positional query or the API shortcut flags.
Local controls (`--retries`, `--timeout`, `--beta`, `--dry-run`) may accompany it.
Without explicit values, the helper supplies `type: deep`, `numResults: 10`,
and `contents: {highlights: true}`. Explicit contents, including `{}` or `null`,
are preserved. Optional API fields may be `null` where the specification allows
it; `type` must select a deep mode. Unknown fields fail before authentication.

```json
{
  "query": "Compare recent original studies on testing existing projects built with AI coding agents. Define expected outcomes independently and distinguish benchmark success from defect detection and CI duration. Provide a synthesis of no more than 700 words, with dates, original links, limitations, and model-specific evidence gaps.",
  "type": "deep-reasoning",
  "numResults": 10,
  "startPublishedDate": "2026-04-11T06:00:00.000Z",
  "endPublishedDate": "2026-10-12T05:59:59.999Z",
  "outputSchema": {"type": "text"},
  "contents": {"highlights": true, "maxAgeHours": 0}
}
```

Validate offline with `search --request-file <request.json> --dry-run`. This
prints the validated request and local controls, without reading the key or
calling Exa. Remove `--dry-run` only for an authorized paid search. Never place
credentials in the request file.

## Search, filtering, and synthesis

| Field | Accepted value and behavior |
| --- | --- |
| `query` | Required nonempty research question; whitespace-only input is rejected. |
| `type` | `deep` or `deep-reasoning`; defaults to `deep`. |
| `numResults` | Integer 1–100. Controls returned sources, not the number of internal searches. |
| `additionalQueries` | Array of 1–10 nonempty alternative research directions. |
| `includeDomains`, `excludeDomains` | Up to 1,200 strings each. Supports hostnames, path prefixes, and wildcard subdomains. |
| `startPublishedDate`, `endPublishedDate` | Publication bounds as ISO date-times with timezone, including fractional seconds. Start must not follow end. |
| `category` | Known values: `company`, `publication`, `news`, `personal site`, `financial report`, `people`. Custom string hints are also accepted. `company`/`people` reject dates and `excludeDomains`. |
| `moderation` | Boolean controlling unsafe-content filtering. |
| `userLocation` | Two-letter country string, `{country}`, or `{latitude, longitude}` with optional `country`. Coordinates must appear together: latitude −90–90, longitude −180–180. |
| `objective` | Broader research goal, at most 4,096 characters. |
| `systemPrompt` | Instructions for generated output and source selection. |
| `userIdentifier` | Opaque identifier, 1–64 letters, digits, underscores, or hyphens. Exa requires this to contain no personal information. |
| `outputSchema` | `{type: "text", description?: "..."}` or an object JSON Schema. Requests synthesis with field-level citations and confidence. |
| `stream` | Boolean. With `outputSchema`, requests SSE; otherwise Exa returns JSON. The helper consumes the stream and prints one completed JSON result. |
| `contents` | Nested options in the next table. |

Object output schemas may use JSON Schema keywords, property definitions,
required fields, and `additionalProperties`. Exa limits the entire schema to
10 properties and two nesting levels below the root; properties inside array
items count too. A root property containing an array of objects is allowed;
an object nested inside those item objects is too deep. Every array must define
`items`. The helper checks JSON Schema syntax and these documented limits.
Exa remains responsible for enforcing its supported synthesis behavior.

```json
{
  "type": "object",
  "properties": {
    "studies": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "finding": {"type": "string"},
          "limitation": {"type": "string"}
        },
        "required": ["title", "finding", "limitation"]
      }
    }
  },
  "required": ["studies"],
  "additionalProperties": false
}
```

## Content options

All fields here belong inside `contents`. See the official
[content guide](https://exa.ai/docs/contents/quickstart) and
[Highlights guide](https://exa.ai/docs/search/highlights).

| Field | Accepted value and behavior |
| --- | --- |
| `text` | Boolean or object with the following extraction settings. |
| `text.maxCharacters` | Integer 1–1,000,000 per result. |
| `text.includeHtmlTags` | Boolean. |
| `text.verbosity` | `compact`, `standard`, or `full`. |
| `text.includeSections`, `text.excludeSections` | Arrays drawn from `header`, `navigation`, `banner`, `body`, `sidebar`, `footer`, `metadata`. Section classification is best effort. |
| `highlights` | Boolean or object with the following excerpt settings. |
| `highlights.query` | Custom query to guide excerpt selection. |
| `highlights.maxCharacters` | Integer 1–1,000,000; incompatible with dynamic highlights or highlight verbosity. |
| `highlights.dynamic` | Boolean, beta opt-in required even when explicitly false. `true` shares the context budget across results. |
| `highlights.verbosity` | `low`, `medium`, or `high`; beta opt-in required. |
| `summary` | Object with optional `query` and `schema`. `schema` is a JSON Schema for each page summary, distinct from whole-search `outputSchema`. |
| `extras` | Object with `links`, `imageLinks`, `richImageLinks`, `richLinks`, `codeBlocks`. Each is an integer 0–1,000. |
| `maxAgeHours` | Integer −1–720: −1 cache only, 0 fresh fetch, positive values bound cache age. Omitting it permits fallback fetching. |
| `livecrawlTimeout` | Integer 1–90,000 milliseconds. Distinct from the helper's transport timeout. |
| `subpages` | Integer 0–100; actual crawl count may be lower. |
| `subpageTarget` | String 1–100 characters or up to 100 such strings. |

Use `maxAgeHours: 0` when text rendering settings must apply to a fresh fetch.
For beta highlights, explicitly pass
`--beta dynamic-highlights-2026-08-28`; the helper sends the documented
`Exa-Beta` header. It never enables paid beta features implicitly.

## Incompatible and deprecated options

`contents.snapshotAsOf` is documented for historical retrieval, but Exa
[Snapshot Search](https://exa.ai/docs/search/snapshot) excludes both deep modes.
`compliance: "hipaa"` requires an enabled Enterprise account and supports only
instant/fast search, per the [HIPAA guide](https://exa.ai/docs/admin/security/hipaa).
Both produce `UNSUPPORTED_OPTION` here. The helper does not change modes.

Deprecated fields fail validation: top-level `startCrawlDate`, `endCrawlDate`,
`includeText`, `excludeText`, `context`; content `context`, `livecrawl`,
`crawledBeforeDate`; highlights `numSentences`, `highlightsPerUrl`. Use current
publication filters, content selection, freshness, and character budgets.
Snapshot aliases cannot enable historical retrieval in deep mode.

## Responses, streams, and errors

Results retain their metadata, publication dates, text, highlights, summaries,
extras, subpages, and any structured entities returned by Exa. Synthesis retains
text or object `output.content` and `output.grounding`. `searchTime` is Exa's
server-reported milliseconds and may omit synthesis time. `costDollars` is the
API-reported estimated USD cost, preserved without estimating missing values.

SSE handles `text-delta`, `grounding`, `results`, `stream-reset`, `done`, and
`error`. Interim deltas are not printed; the authoritative `done` output is used
after any reset. This prevents incomplete or superseded synthesis from becoming
a completed answer and allows credential redaction across chunk boundaries.
Missing completion, malformed events, or stream errors stop without replay.
`stream: true` without an output schema retains Exa's documented JSON behavior
for the same selected deep mode.

Local transport timeout is 1–300 seconds per socket operation (default 120).
Retries are 0–2, only for HTTP 429/500/502/503/504; delay is bounded at 30 seconds.
Timeouts, transport uncertainty, invalid responses, and in-stream errors never
trigger a second request. See Exa's [error reference](https://exa.ai/docs/admin/error-codes).

The bundled [request schema](search-request.schema.json) derives its shapes and
bounds from the audited OpenAPI document. It restricts modes, removes deprecated
fields, accepts documented custom category hints, and rejects unknown options.
Cross-field restrictions are enforced in the helper. Re-audit official docs
before changing this contract; do not relax validation to silence an API error.
