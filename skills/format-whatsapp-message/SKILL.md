---
name: format-whatsapp-message
description: Compose, rewrite, or convert copy-ready WhatsApp chat messages using WhatsApp-native text formatting. Use when Javier requests a WhatsApp message, asks to adapt Markdown for WhatsApp, or needs literal formatting markers preserved for copying into WhatsApp.
---

# Format WhatsApp Message

Produce a message that can be copied directly into WhatsApp without Markdown syntax being misinterpreted.

## Choose the operation

- **Convert:** Preserve the wording and change only the formatting.
- **Compose:** Write and format a new message for the stated audience and purpose.
- **Rewrite:** Improve both the wording and formatting.

Infer the operation from the request. If Javier asks only for formatting, do not rewrite the content.

## Use WhatsApp-native syntax

| Intent | Syntax |
| --- | --- |
| Bold | `*text*` |
| Italic | `_text_` |
| Strikethrough | `~text~` |
| Inline code | `` `text` `` |
| Multiline monospace | Wrap the text in three backticks |
| Bulleted list | `- item` |
| Numbered list | `1. item` |
| Quote | `> text` |

## Convert unsupported Markdown

- Convert `# Title` and other headings to standalone `*Title*` lines.
- Convert `**bold**` to `*bold*`.
- Convert `[label](https://example.com)` to `label: https://example.com`.
- Convert tables to short labeled lines or lists.
- Replace horizontal rules with a blank line.
- Simplify deeply nested lists or formatting.
- Do not emit unsupported Markdown heading, table, or named-link syntax.

Preserve URLs, identifiers, commands, facts, and the requested language. Do not add emojis unless requested or already present.

## Optimize for WhatsApp

- Use short paragraphs and blank lines for mobile readability when composing or rewriting.
- Use bold standalone lines for section headings.
- Avoid decorative formatting that does not improve scanning.
- Keep formatting markers balanced and directly adjacent to their text.
- Keep WhatsApp Business API template constraints out of scope unless explicitly requested.

## Return copy-ready text

Return only the message unless Javier asks for explanation or alternatives. Place it in a plain fenced code block so the literal WhatsApp markers remain copyable. If the message contains a three-backtick monospace block, use a four-backtick outer fence.

Example source:

```markdown
# Deployment update

The **preview is ready**.

- Verify login
- Test jobs
```

Return:

```text
*Deployment update*

The *preview is ready*.

- Verify login
- Test jobs
```
