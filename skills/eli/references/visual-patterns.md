# Visual patterns and delivery

Read this for a visual page or interactive walkthrough. Use the light visual defaults below unless the user selects another treatment. Adapt the composition to the teaching point and respect supplied branding and existing project context.

## Contents

- [Default: polished, light, and visually led](#default-polished-light-and-visually-led)
- [Large SVG scenes, with purpose](#large-svg-scenes-with-purpose)
- [Motion and optional helper skills](#motion-and-optional-helper-skills)
- [Start with the teaching point, not the controls](#start-with-the-teaching-point-not-the-controls)
- [Choose a visual pattern](#choose-a-visual-pattern)
- [Worked design: a fictional rate-limit walkthrough](#worked-design-a-fictional-rate-limit-walkthrough)
- [Visual meaning and narrative](#visual-meaning-and-narrative)
- [Accessible and readable by design](#accessible-and-readable-by-design)
- [Match the current environment](#match-the-current-environment)
- [Validate what the result claims to do](#validate-what-the-result-claims-to-do)

## Default: polished, light, and visually led

Use a clean ElevenLabs/Eleven Academy-inspired direction for ordinary visual requests as well as guide-created outputs. A supplied brand or explicit style choice takes precedence. These portable presets do not certify official brand compliance.

- **Light foundation:** white and off-white surfaces, graphite text, delicate rules, generous whitespace. A useful ElevenLabs-derived base is white `#FFFFFF`, off-white `#FAFAFA`, graphite `#1E1916`, and divider `#E0DEDC`. Use cream `#F5F3F1` locally within objects, not as an overall beige wash. Keep light styling even when the device prefers dark mode. Do not add a theme toggle unless requested.
- **Academy illustration (default):** neutral surrounds, white/paper objects, graphite outlines, small cream areas, and restrained terracotta emphasis. Make one connection, current edit, or meaningful focus carry the accent. Avoid sepia, amber glow, gradients, shadows, and filters inside the teaching drawing. Keep real company and agent identity colors intact.
- **ElevenLabs editorial:** strong, spacious typography on a light base, with large vector scenes or relevant atmospheric media. Let imagery carry color while interface controls remain restrained. Apply current brand rules for actual branded work; avoid adding generic colored UI panels in the name of branding.
- **Minimal light:** precise monochrome diagrams, spare labels, and the same strong scale and whitespace. This is also a useful custom choice for technical reference material.
- **Typography:** use supplied KMR Waldenburg fonts where available and permitted; otherwise use a clean local sans-serif fallback such as Inter, Helvetica Neue, or the system font. Use sentence case, a clear two-weight hierarchy, readable body text, and large uncomplicated headings. Do not fetch a remote font silently or make a missing brand font block the explanation.
- **Composition:** make the main SVG a substantial teaching stage, roughly half of a desktop opening section or a full-width scene below a short introduction. Let the relationship be visible before the supporting paragraphs. Follow with a small number of purposeful sections, each with one point. Avoid tiny decorative icons, rows of interchangeable cards, excessive badges, and dashboard chrome.
- **Controls:** use a small set of familiar controls beside the state they affect. Preserve the existing host's real components when building inside Academy; the standalone default does not authorize replacing course UI. A standalone explainer may use ordinary accessible HTML controls without importing the Academy app.

Use genuine supplied logos and agent assets when needed; do not redraw them or add an ElevenLabs wordmark to an unrelated explanation merely to evoke the look. Brand inspiration changes the visual treatment, not the identity of the content.

## Large SVG scenes, with purpose

Before drawing, identify what the learner should see and what a mistaken reading would be. Choose a spatial relationship that teaches it: a bracket for a rule applying across replies, a boundary for a limit, a shared base for a dependency, or aligned cases for a comparison. Labels support that relationship; they should not be the only thing explaining it.

Make the primary object the largest meaningful shape. Reserve space for labels before routing connectors. Use clear silhouettes, balanced negative space, consistent outline families, rounded line endings, and a small number of distinctive details. Group related objects; keep stable anchors across states. A large generic symbol floating above paragraphs does not meet the visual brief.

Use inline SVG with a responsive `viewBox`, scoped styles, unique IDs, and an accessible title/description or equivalent nearby text. Keep labels readable at the actual rendered size; enlarge the stage or reduce detail before shrinking text. Include meaningful text equivalents. Do not encode unsupported quantities in shape size, distance, or animation speed.

## Motion and optional helper skills

Animate to explain sequence, change, or comparison. Draw a connector only after both endpoints exist; reveal labels as readable units; use movement to preserve correspondence between states. Avoid decorative loops, floating shapes, glowing backgrounds, and letter-by-letter label reveals. A complete static composition is preferable when motion adds no teaching value.

Use these helpers only when available and relevant, while preserving the selected brief:

| Helper | Apply to the explainer | Keep within scope |
|---|---|---|
| svg-animation | Stroke reveals, purposeful path motion, transitions, and deterministic seeking | Prefer inline CSS, SMIL, or browser JavaScript for offline output; do not add a CDN merely because a helper example uses one |
| SVG Logo Designer | Distinctive silhouettes, simple symbols, negative space, clean scalable paths | Create the needed illustration or requested mark; do not generate an unrequested logo concept/variation package or redesign an existing identity |
| elevenlabs-brand | Actual ElevenLabs name, typography, palette, identity, and media treatment | Use current supplied assets and guidelines; do not claim the portable preset alone is exact compliance |
| academy-illustrations | Balanced drawing grammar, teaching relationships, cue-based reveals, real course host integration | Reuse the actual host and shared parts in Academy; keep a generic standalone explainer independent of that codebase |

Without helpers, use the standards in this reference. Never install skills or fetch a brand kit just to finish an ELI explanation. Required project assets may still need the user to supply them if inaccessible; a stylistic inspiration does not require identity assets.

For animated standalone HTML, use one coherent clock for each coordinated scene. Provide deterministic seeking such as `?t=N` so start, middle, and settled frames can be inspected; make seeking rebuild the same state in both directions. Do not mix unsynchronized CSS timers with a separate JavaScript playback clock. In a host with an existing animation/narration clock, use it instead.

Honor reduced motion with a complete readable composition and instant meaningful state changes. Never leave stroke-dashoffset hiding the diagram when motion is disabled. Provide pause/replay or step controls when needed; a static preference still permits useful controls that change state without animation.

## Start with the teaching point, not the controls

Privately identify what the learner should notice, which relationship must become visible, and what the picture cannot faithfully represent. Select the smallest visual that can carry that explanation. Avoid presenting this planning as a lengthy design questionnaire.

A static picture is appropriate when the important relationship is spatial or can be read at a glance. Animation is useful when a change over time matters. Interaction is useful when a learner's action can expose a rule or test a prediction. A static request does not need to be upgraded into an application.

For each guided phase, establish **one point**, **one visual demonstration**, and **one takeaway**. The phase count follows the subject; it is not a fixed requirement. Orient the learner before exposing controls. Make the next action obvious and optional detail visibly secondary.

## Choose a visual pattern

| Pattern | Show | A useful action, when needed | Avoid |
|---|---|---|---|
| Follow an item | One object changing across real stages | Step the item through a hand-off and show the new state | Moving dots whose position has no explained meaning |
| Matched comparison | Two cases with the same baseline and one relevant difference | Toggle the changed condition or align the two views | Unequal scales or changing several factors without explanation |
| Boundary explorer | A rule below, at, and above its threshold | Change one input and reveal the condition and result | A slider that implies continuous behavior for a discontinuous rule |
| Parts to whole | What contributes to an outcome or a number | Change a supported input while retaining labels, units, and definition | Areas, lengths, or counts that imply unsupported quantities |
| Analogy to reality | A familiar scene and its specific counterparts | Reveal the mapping, then a real-world case | An illustration with no explicit connection back to the subject |
| Conditional path | How a condition changes permission or consequence | Choose a scenario and highlight the applicable rule | Invented branches or hidden exceptions |
| Evidence map | Established facts, attributed claims, implications, and unknowns | Reveal sources or compare supported accounts | Causal arrows for relationships that are only chronological |

Use diagrams to show relationships and tables when exact comparison is the point. Do not default to paragraphs in attractive boxes. A card can carry context, but it is not automatically an explanatory visual.

## Worked design: a fictional rate-limit walkthrough

**Demo facts:** a toy service accepts at most three requests in each fixed ten-second window, starting at time zero. Additional requests in that window are rejected, not queued. Completion of a request does not restore allowance. The demo does not automatically retry rejected requests. This is one fictional policy, not a statement about real APIs.

**Teaching target:** allowance belongs to a time window, not to the number of jobs currently running.

| Phase | Demonstration | Takeaway |
|---|---|---|
| Orient | Show the current ten-second window and three labeled allowance positions. State the toy rule. | The rule limits accepted starts within this window. |
| Use the allowance | Let the learner send requests. Update accepted count and remaining allowance with every accepted request. | Each accepted request uses one place in the current window. |
| Cross the limit | The next request is visibly rejected with an adjacent reason, while accepted count stays at three. | An extra request is rejected under this demo's rule, not held for later. |
| Change the window | Advance the demo clock to the next boundary. Reset the window counter without silently resending rejected requests. | A new window supplies a new allowance. |
| Transfer | Show completed jobs and the window count as distinct concepts, or contrast a batch just before and just after a boundary. | Completion and window reset are different events. |

Suitable controls are **Send request**, **Advance demo time**, and **Reset**, introduced only when useful. A simulated clock avoids imposing a real ten-second wait. Label it as simulated time. Text must report the current window, accepted count, remaining allowance, and reason for rejection; color alone cannot do this.

A possible optional prediction asks whether finishing a job restores allowance. Provide a revealable explanation and a skip path. The main demonstration must remain complete without answering it.

The point is not to copy this interface for every topic. Preserve the relationship between action, state, and explanation when designing a different concept.

## Visual meaning and narrative

Place labels next to the objects they describe. Use stable names across phases. Keep key reference objects in place when possible so the learner can see what changed. Distinguish diagrammatic size from measured quantity; label a conceptual illustration when its geometry is not data.

Show the analogy, then show its mapping. Put any limitation that would change the central meaning on the main path. Secondary nuance can use an expandable note. Do not hide the caveat that makes a visually appealing claim false.

Use motion to reveal causality or sequence, not to imply an unverified cause. Let the learner pause, replay, or step through meaningful motion. If removing the animation removes the explanation entirely, supply a static sequence or equivalent state descriptions.

## Accessible and readable by design

Use readable type, clear hierarchy, adequate contrast, and layouts that work at smaller widths. Keep controls operable by keyboard with visible focus and descriptive labels. Use semantic headings and native controls where appropriate. Put meaningful text equivalents beside diagrams; decorative images do not need elaborate descriptions.

Give status changes understandable text, not just color. Avoid changing screen-reader focus on every small update; announce important outcomes without overwhelming the user. Support reduced-motion preferences while preserving the conceptual sequence. Do not require hover, audio, dragging, or precise timing as the only way to learn the point. Caption explanatory audio if present.

A responsive page can reflow instead of shrinking an unreadable desktop diagram. Preserve relationships and reading order in the smaller layout. A check can be skipped without losing navigation or the concluding takeaway.

## Match the current environment

Use capabilities, not a fixed platform-name map. A built-in visual workspace may have required tools, content constraints, or design guidance; follow the actual host's contract. HTML can be shown in that workspace or supplied as a file. Reuse existing project conventions when the user is working in a project.

Without a suitable workspace, prefer one standalone HTML file using embedded CSS, JavaScript, and visuals. Inline SVG and ordinary browser elements can support many explanations without a framework. Do not make a CDN, remote font, module import, fetched JSON file, local server, or API key an invisible requirement. A source link the reader can optionally open is not itself a runtime dependency.

A requested advanced feature can justify a library or a project build. Explain necessary dependencies and verify the resulting delivery rather than promising that every single-file output is offline-capable. Never embed secrets in a client-side page. Do not contact services, add analytics, persist personal data, install packages, or publish externally merely to make an explanation work.

When file creation is unavailable, provide the complete HTML code and brief save/open instructions, with an honest statement about testing limits. Do not promise a native canvas or a hosted site from the platform name alone.

## Validate what the result claims to do

When tools permit, render the actual output and exercise the beginning, end, repeat actions, reset, and important boundary conditions. Inspect animated start, middle, settled, replay, and backward-seek states, not just the finished picture. Check whether the displayed explanation agrees with the state and with the source rules. Test keyboard access and responsive layouts; prioritize desktop and tablet for Academy/SCORM output. Review reduced-motion behavior and textual equivalents. Inspect console errors and required network requests when possible.

Review visual quality separately from technical correctness: the chosen light treatment remains light, the primary SVG is prominent, labels have room, connectors do not clip or cross unrelated objects, the composition teaches the relationship, and the result reflects the interview choices. A technically valid SVG is not proof of a polished design.

For a claimed self-contained file, check its actual dependencies, not just its extension. Inspect external script and style references, images and CSS URLs, imports, embedded-frame sources, and network calls. A library may initiate requests even when its entry script is bundled. Separate this technical check from judging whether a human learned the idea.

Without runtime tools, inspect the code and describe that as inspection, not an executed browser test. After delivery, provide the real file or workspace reference and any essential limitations. Do not repeat the entire lesson in chat.
