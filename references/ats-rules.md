# ATS and PDF release rules

The release checks verify text extraction, reading order, required identity fields, page count, font embedding, and supported keyword presence. They cannot reproduce every employer's ATS or prove ranking.

## Layout contract

- Use one logical column and standard headings.
- Keep contact information in the document body, not a header/footer object.
- Use visible text labels for email, phone, GitHub, LinkedIn, and portfolio links.
- Avoid photographs, icons as labels, charts, progress bars, decorative tables, and text boxes.
- Use conventional dates such as `Jan 2024 – Present`.
- Keep essential information as selectable text.
- Embed fonts and include Unicode-to-text mapping.
- Never add invisible keywords, white text, repeated keyword blocks, or misleading alternate text.

## Release gates

Block release for compilation failure, exceeded page limit, sparse extraction, missing identity fields, missing/out-of-order headings, replacement glyphs, unembedded fonts, claim-verification errors, or material disagreement between structured content and extracted text.

Warn for long lines, dense bullets, genuine skill gaps, ambiguous dates, URLs present only as annotations, or a sparse final page within the requested limit.

Submit PDF when accepted and extraction is clean. If the application explicitly requests DOCX, follow that instruction.

