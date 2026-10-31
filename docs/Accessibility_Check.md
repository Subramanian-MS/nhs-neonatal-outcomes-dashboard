# Accessibility check (default light theme)

WCAG AA requires a contrast ratio of at least 4.5:1 for normal text.

| Pair | Foreground | Background | Ratio | Result |
|---|---|---|---|---|
| Green cell text (better than benchmark) | #1d5a34 | #a9d8b8 | 5.15 | Pass |
| Orange cell text (behind benchmark) | #7a3a07 | #f3ae7b | 4.58 | Pass |
| Table heading | #ffffff | #16285a | 14.14 | Pass |
| Body text on page | #2b3552 | #eef0f3 | 10.61 | Pass |
| Muted text on white | #5d6780 | #ffffff | 5.65 | Pass |
| Muted text on page | #5d6780 | #eef0f3 | 4.95 | Pass |
| Amber-dark text on white | #7d6400 | #ffffff | 5.68 | Pass |
| Green text on white | #3f7d4f | #ffffff | 4.93 | Pass |
| Highlight blue on white | #3f64b9 | #ffffff | 5.62 | Pass |
| Ink on benchmark average row | #16285a | #c4cad8 | 8.61 | Pass |

Not relying on colour alone: every coloured table cell also carries a printed value and a directional triangle (`▲` = above the National NICU average, `▼` = below); chart bars carry value labels and a key; hovering gives the exact gap in percentage points and the NHS ODS / ODN metadata.
Keyboard navigation: every table row is focusable (`tabindex="0"`) with a visible focus ring (`outline: 3px solid var(--hl)`) and can be selected using the `Enter` key.
