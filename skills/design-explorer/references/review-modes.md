# Review Modes

## Explore

Use the default mode for a broad first round. The reviewer flips through every design, votes, writes notes, places pins, and draws directly on the surface.

Use it when the question is still “what feels promising?” rather than “which precise option wins?”

## Decide with round.json

Write **round.json** into the mockup directory when the alternatives and decision axis are explicit.

~~~json
{
  "schema": "design-explorer.round.v2",
  "mode": "vote",
  "matchups": [
    {
      "question": "Which density makes the queue easiest to scan?",
      "mode": "pick",
      "axis": "density",
      "chips": ["easier to scan", "less overwhelming", "more useful at a glance"],
      "options": [
        {
          "id": "mockup-compact-rail",
          "name": "Compact rail",
          "hint": "More rows and persistent filters"
        },
        {
          "id": "mockup-roomy-cards",
          "name": "Roomy cards",
          "hint": "Fewer items with stronger grouping"
        }
      ]
    }
  ]
}
~~~

Name every option and give it a plain one-line hint. Test one axis per matchup.
Option IDs must match the complete mockup filename stem. For example,
**mockup-compact-rail.html** has the option ID **mockup-compact-rail**; the
section's **data-mockup-id** is a label for the fragment and does not replace
that runtime ID.

### Pick

Use **pick** for two to ten mutually exclusive candidates. Two candidates render side by side on a wide desktop. The reviewer can choose A or B, use number keys, or press Enter on the selected option.

### Rank

Use **rank** for three to ten subtle variants where the full preference order matters. The reviewer taps candidates best-first, then confirms the order.

### Reasons

Add three to five short reaction chips such as “clearer,” “warmer,” or “easier to scan.” Write them as language the reviewer would naturally use, not as a design-team hypothesis. The reviewer may add a short free-text reason or skip reasons.

Results are written to **ballot.json** using **design-explorer.ballot.v2**. The answered round is archived and the workspace is locked against accidental re-review until explicitly unlocked.

## Workspace signals

Each resolved matchup also appends one JSON line to **signals.jsonl** inside the mockup workspace. The file records the axis, decision mode, winner or rank order, losing options, reasons, and note.

Treat this as review history for the current external workspace. Do not automatically copy it into the project repo or turn it into permanent design doctrine. Summarize durable preferences only with the user's permission.

## Choose the smallest useful instrument

- Two directions: pick, side by side.
- Three to ten variations on one axis: rank.
- One design: notes, pins, and drawings; no ballot.
- Yes or no: binary pick with unusually clear hints.
- A numeric threshold: ask directly; a visual ballot is the wrong tool.
- Several roles can coexist: rank and include a “both work” reason chip.

When the decision shape is unclear, default to a two-option pick and explain the distinction simply.
