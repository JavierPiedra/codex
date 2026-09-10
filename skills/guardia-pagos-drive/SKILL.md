---
name: guardia-pagos-drive
description: Register payment receipts in Javier's Guardia Javier Piedra Perea Google Sheet and Donativos Papa Drive folder. Use when Javier asks Codex to review, upload, link, or register a pago, comprobante, recibo, donativo, aportación, or proof-of-payment photo in that sheet, especially entries for the Gastos tab and Comprobante column.
---

# Guardia Pagos Drive

Use this skill to register payment receipts in Javier's Google Sheet `Guardia Javier Piedra Perea` using the Google Drive/Sheets connector when available.

## Source Of Truth

- Spreadsheet: `1_VNqUYaRSQlsksbkh4aAUirSV5paQ9X9E2-SFzAIR18`
- Target tab: `Gastos`, `sheetId: 1836833154`
- Receipt folder: `Personal > Donativos Papa`, folder id `1pMNYkHnIFRuAsIGmVuGBbcMJ23LLsMDf`
- Header row `Gastos!A1:K1`: `Fecha`, `Día`, `Categoría`, `Concepto`, `Ingreso`, `Egreso`, `Efectivo`, `Paso por cuenta`, `Quién pagó`, `Comprobante`, `Notas`
- Day lookup tab: `Dias Semana`

## Safety

- If Javier says not to move, touch, edit, or do anything, stay read-only and explain the intended steps.
- Before writing, re-read the target row and confirm it is blank.
- Do not overwrite an existing row unless Javier names that row.
- Do not invent ambiguous fields. Ask one focused question if payer, category, income/expense direction, or target row is unclear.
- If the connector cannot upload an attached image to Drive, or Drive reports missing edit permission, ask Javier for a Drive file link and continue from that link.
- Never use the stale named range `Dias_Sem` for new rows; it can produce `#NAME?`.

## Workflow

1. Ground the Sheet with metadata, then read `Gastos!A1:K1` plus recent rows.
2. Verify the receipt file:
   - If Javier provided a Drive link, read file metadata and confirm whether it is in `Donativos Papa`.
   - If Javier provided only an attachment and upload is available, upload it to `Donativos Papa` with a descriptive filename.
   - If upload is unavailable or permission is missing, stop and ask for a Drive link.
3. Choose the target row:
   - Default to the first blank row after the current data.
   - Re-read the candidate row before writing.
4. Build row `A:K`:
   - `A Fecha`: date from the comprobante.
   - `B Día`: `=VLOOKUP(WEEKDAY(A{row}),'Dias Semana'!A:B,2,false)`.
   - `C Categoría`: use existing categories such as `Cuidador`, `Medicamentos`, `Insumos`, `Doctor`, or `Otros`; ask if unclear.
   - `D Concepto`: short payment concept, for example `AVION PERU`.
   - `E Ingreso` or `F Egreso`: set exactly one unless Javier says otherwise.
   - `G Efectivo`: boolean.
   - `H Paso por cuenta`: boolean.
   - `I Quién pagó`: payer name.
   - `J Comprobante`: Drive hyperlink. Prefer `=HYPERLINK("{url}","{url}")` when writing through the Sheets API.
   - `K Notas`: concise traceability details such as clave de rastreo, referencia, hora, and source notes.
5. Write in one Sheets `batchUpdate`:
   - Copy `PASTE_FORMAT` from the previous row over `A:K`.
   - Update the row values.
6. Verify after writing:
   - Re-read `Gastos!A{row}:K{row}` with formatted, effective, user-entered, and hyperlink values.
   - Confirm `B Día` is not `#NAME?`.
   - Confirm `J Comprobante` points to the expected Drive file.
   - If verification fails, fix only the failing cell or cells and verify again.

## Prior Pattern

For the Angel Romero / Avion Peru payment on 2026-05-25, the correct pattern was `Categoría=Otros`, `Concepto=AVION PERU`, `Ingreso=2000`, `Efectivo=FALSE`, `Paso por cuenta=TRUE`, and `Quién pagó=Angel Romero`.
