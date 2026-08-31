# Capture, Mobile Review, and Presentations

## Capture contract

Submitting a round captures every design in the active review scope, including untouched and unvoted designs.

- **captures/<id>.png** is the visual source of truth. Pins and drawings are burned into the image over a capture-only ten-percent grid.
- **annotations.json** links each image and HTML snapshot to structured pin targets and drawing coordinates.
- **feedback.md** is the readable review summary.
- **captures/<id>.html** is the searchable DOM fallback with scripts, embeds, event handlers, executable URLs, navigation, forms, autoplay, and editing disabled.

The mockups render as same-origin srcdoc frames. Markup uses content-relative coordinates so it stays attached while zooming or fitting. Capture lazy-loads the bundled html2canvas 1.4.1 build from the local server.

Inspect the PNG before interpreting a pin. The image explains where the reviewer pointed; the JSON explains which element was targeted and what they said.

## Phone and tablet review

Use **--tailnet** only when the reviewer needs another device. The server keeps its loopback listener and adds a second listener on the machine's Tailscale address.

The remote surface has no authentication. Anyone on that tailnet who can reach the machine can read the mockups and submit review data. Use a trusted personal tailnet and stop the server afterward.

Touch mode activates automatically for coarse pointers and can be forced with **?touch=1** or disabled with **?touch=0**.

- Swipe between designs with the native scroll-snap pager.
- Vote from the bottom controls.
- Open a design full size in a new tab for native pinch and pan.
- Place pins from the overflow menu.
- Drawing remains desktop-only.

Designs are laid out at a true desktop width and scaled uniformly, so a phone review does not accidentally judge a responsive mobile reflow.

## Guided presentations

An advanced workspace may include **presentation.json** with schema **design-explorer.presentation.v3**. It can define ordered stops, local narration audio, timed spotlights, side-by-side comparisons, feedback gates, and inline pick or rank votes.

Use a presentation only when the order or explanation is part of what the reviewer must understand. Plain comparison is faster for ordinary layout choices.

Presentation audio must be local files under the workspace's **audio/** directory. Do not add transcription, microphone capture, model calls, or remote narration services.

## Convergence

Use shrinking rounds:

1. Explore six to ten meaningfully different directions.
2. Turn the ordering, reasons, notes, and markup into explicit preference hypotheses.
3. Generate a smaller set of new variants based on those hypotheses plus one controlled challenger.
4. Stop when the reviewer's ordering matches the prediction or after four rounds.

Do not call a direction converged because it merely survived several rounds. Explain the evidence and remaining uncertainty.
