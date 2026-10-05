# Picture, motion, and sound craft

Use this as a selection menu and diagnostic reference. Apply techniques to the film's purpose; adding more techniques is not the objective.

## Contents

- [Attention and meaning](#attention-and-meaning)
- [Typography and composition](#typography-and-composition)
- [Motion with weight](#motion-with-weight)
- [Continuity and transitions](#continuity-and-transitions)
- [UI performance](#ui-performance)
- [Sound and rhythm](#sound-and-rhythm)
- [Texture and finishing](#texture-and-finishing)
- [Common repairs](#common-repairs)

## Attention and meaning

- Give each beat one dominant subject. Stage secondary information after attention has landed.
- Put the promise or tension into a visible event: a real result, an unexpected comparison, a specific constraint. Avoid an empty logo pre-roll unless brand recognition is the intended opening.
- Vary density and energy. A busy reveal needs somewhere quiet to land. A hold is useful when someone is reading, comparing, or understanding a result.
- Keep narration, captions, headline, and interface from demanding four separate reading tasks. Let picture demonstrate what the voice explains; use on-screen copy for essential emphasis.
- Test whether removing a decorative layer improves the message. Keep an accent because it reinforces identity, hierarchy, or emotion.

## Typography and composition

- Design at the actual delivery aspect ratio and review at the intended display size. Pixel sizes alone do not establish readability.
- Use a stable type scale, measured line lengths, deliberate wrapping, and optical alignment. Check real strings with real loaded fonts.
- Start reading time when the text becomes stable and legible, not when its entrance begins. Read it at an unhurried pace while also following the picture.
- Protect important copy from captions, logos, UI controls, and platform overlays. Record safe areas for the actual destination rather than assuming one universal inset.
- Make a dense dashboard readable by isolating the relevant real region, using a detail view, or staging information. Shrinking the whole dashboard rarely communicates the proof.
- Align recurring baselines and anchors across shots. Preserve generous negative space where the eye must rest.
- Use tabular figures for changing numeric columns when available. Check that digit changes do not jiggle the layout. Do not animate unsupported metrics to imply measurement.
- Inspect the frame where the most content coexists and halfway through transitions; clean settled frames can hide collisions.

## Motion with weight

Define motion by object role, distance, and meaning. Record the chosen behavior in the project's style guide, then reuse it consistently.

| Object | Useful starting behavior | Failure to watch for |
| --- | --- | --- |
| Small control | Quick response, short travel, little overshoot | Bouncing makes an ordinary click feel like a toy |
| Panel or window | Controlled acceleration and a readable settle | The container and its contents drift at unrelated speeds |
| Headline | Clear arrival, stable hold | Most of its screen time is spent moving |
| Camera | Smooth move that preserves an anchor | Moving camera and moving UI compete for attention |
| Data mark | Change tied to the represented quantity | Elastic motion suggests a value overshot its actual result |
| Character/mascot | Consistent performance and intentional secondary action | Extra gestures compete with the explanatory moment |

Use springs where settling or playfulness makes sense. Use precise curves where control and accuracy matter. Preserve a recognizable motion vocabulary; do not randomize easing to prove variety.

For stronger movement, consider anticipation, acceleration, contact, settle, and a small secondary response. Use only the phases the action needs. Stagger by hierarchy or causality rather than a uniform delay on every item.

Make speed legible: a large camera move needs more time or fewer competing elements. Inspect peak travel as well as endpoints. Diagnose strobing by comparing source frame rate, distance per frame, preview performance, and the encoded file before adding blur.

## Continuity and transitions

- Establish an anchor that survives: the same field, panel edge, object, color accent, or spatial relation.
- Choose each transition's job: reveal a consequence, change scale, connect related objects, shift time, or reset attention.
- Preserve direction and screen geography unless disorientation is intentional. Watch for a target switching sides during a camera move.
- Morph between understandable states of the same object. Do not use a shape match that obscures a factual interface change.
- Plan overlap, z-order, and entrance timing as one handoff. Check the outgoing frame, midpoint, and first readable incoming frame.
- Avoid blank gaps, double exposure of unrelated headlines, and end-of-shot fades that leave nothing for a transition to use.
- Use a cut, wipe, match move, or dissolve when it has a purpose and the selected renderer's authoring rules support it. Honor HyperFrames-specific transition rules when that skill is active.
- Let the last readable state work as a cover. If the film intentionally ends on black, export the preceding designed cover separately and still inspect the true last frame.

## UI performance

Capture exact screens and states before animating them. Record any redactions or explicitly permitted simplifications. Preserve labels, enabled/disabled states, data, and interaction sequence.

Choreograph the cursor as an actor with intent: move toward a target, briefly establish hover when useful, press on visible contact, then let the real result appear. Place click sound at contact. Avoid a cursor already resting on the target throughout the setup or sweeping aimlessly between actions.

Keep the relationship between input and response legible. Allow enough latency to see the causal chain without making the demo tedious. Do not accelerate a loading state in a way that makes an unsupported performance claim.

When using crops or recreated layers of an approved real screen, maintain a route back to the whole product. Distinguish explanatory magnification from controls that actually exist. Avoid fake toggles, fabricated success states, and illustrative graphs presented as live data.

## Sound and rhythm

- Analyze the actual track, including pickup, first downbeat, phrase boundaries, energy changes, and ending tail. Do not assume a track begins on its first downbeat or holds one exact tempo.
- Place a few important visual events against musical accents. Avoid forcing every scene change to equal intervals.
- Use sound to make a material or action believable. Reserve larger impacts for larger changes; repeating the same impact removes hierarchy.
- Align the audible transient with the visible event. Leading silence inside an effect file can make identical clip timestamps sound late.
- Leave headroom and protect speech with level changes or ducking. Listen on the intended playback device or a reasonable substitute; check mono if it matters to distribution.
- Check voice pacing, breaths, pronunciation, caption grouping, and whether the final words are cut short. Resolve the ending with the music rather than stopping the file abruptly.
- Measure loudness and true peak against the project's delivery target; do not impose one LUFS number on every platform. Measurements complement listening.
- Listen without picture for an intentional beginning, development, and resolution. Then watch muted to test whether the image communicates the essential idea or needs captions.

## Texture and finishing

Use grain, light, shadow, depth, and blur in service of hierarchy and the chosen material. Inspect at output resolution: fine noise, thin rules, soft gradients, and tiny type can fail after compression.

Avoid a full-frame moving background that becomes the loudest subject. Use layered depth sparingly, especially behind instructional UI. Do not conceal weak composition under atmosphere.

Test a short difficult segment before enabling expensive render features. Compare the same frames and motion with one setting changed at a time. Retain a clean reference encode if making compressed delivery variants, and inspect the delivered encode for banding, ringing, lost detail, and audio tail damage.

## Common repairs

| Observed result | Likely useful change |
| --- | --- |
| Feels like separate slides | Carry one object or anchor through the handoff; show an actual state change |
| Everything has equal importance | Delay secondary action; lower background energy; simplify one beat |
| Looks expensive but says little | Replace an ornamental shot with evidence of the central claim |
| Feels rushed despite a long duration | Increase stable reading time and remove competing motion |
| Feels slow despite constant motion | Shorten setup, sharpen the reveal, or remove purposeless shots |
| All shots feel identical | Vary information scale, density, and rhythm while preserving the visual grammar |
| Preview feels smooth, export does not | Inspect actual frame cadence and delivery encode before changing choreography |
| Sound feels pasted on | Fix a few key contacts, shape dynamics, and give the ending a resolution |

Do not ban centered text, gradients, fades, cards, or springs as categories. Reject unexamined repetition and mismatches between treatment and meaning.
