# Review rendered evidence

## Identify the exact candidate

Record source revision/hash, renderer/version, composition, dimensions, FPS, duration, asset revision, output path, and capture context. Label preview captures, a rough encode, and final delivery separately. Tie every review to the actual candidate inspected.

## Inspect in increasing cost order

1. **Representative stills:** opening, densest shot, proof, and closing state at intended viewing size.
2. **Contact sheet:** each major story beat; assess hierarchy, identity, color/type consistency, and whether the story is visible.
3. **Transition strips:** frames before, during, and after the fastest moves and handoffs; inspect overlap, clipping, continuity, and blank frames.
4. **Motion playback:** watch continuously at normal speed. Stills cannot establish pacing, smoothness, or a successful transition.
5. **Sound review:** listen, watch with sound, and watch muted. Inspect cue contacts, narration clarity, caption sync, dynamics, and ending.
6. **Delivery review:** inspect every requested aspect ratio and the exact final encode, including first/last frames, expected audio tracks, duration, and format.

For a transition, sample around its start, midpoint, and completion. A seven-frame strip around the start alone does not cover a long transition. Also inspect the last readable cover if the final frame intentionally fades out.

## Generate evidence from a video

Use `scripts/review_frames.py` relative to the installed skill root. Requires Python 3, Pillow, FFmpeg, and ffprobe on the active environment. Check available dependencies before installing anything; renderer-provided frame capture is also valid.

```bash
python3 /path/to/video-director/scripts/review_frames.py out/rough.mp4 \
  --times 0,2.2,5.6,9.3,12.8 \
  --strip-at 5.2,5.6,6 --radius 3 --out reviews/r01-wide
```

`--times` are seconds from the first displayed video frame. The helper selects the nearest actual frame timestamp, not an assumed constant frame rate. `--strip-at` adds adjacent decoded frames around each anchor. First and last frames are always included. With no selections, it samples twelve moments across the video.

Outputs:

- `contact-sheet.png`: a compact overview with decoded frame indices and timestamps.
- `frames/*.png`: full-resolution selected frames for close inspection.
- `strip-00.png`, etc.: separate labeled sheets for each transition anchor.
- `manifest.json`: video hash, stream metadata, requested times, selected frames, actual timestamps, and extraction commands.

Use a fresh output directory for each candidate; the helper refuses to replace existing evidence. Missing dependencies, invalid times, missing video frames, and oversized selections fail with a useful message. This helper does not listen, assess visual quality, prove direct source seeking, or validate an export. A contact sheet must actually be opened and reviewed.

For preview-only work, use the renderer's seek and screenshot tools to capture equivalent evidence without making a video export. For blurry or sparse sheets, open the corresponding source frames at the actual viewing size.

After modifying the helper, run its behavioral checks with `python3 scripts/test_review_frames.py` from the skill directory. The checks use lossless fixtures with known pixels and constant/variable frame timing, and verify that existing evidence survives a refused overwrite.

## Critic pass

Set aside the prompt and implementation explanation while judging visible/audible output. Use the brief only to establish the intended claim, audience, and constraints.

Rate each applicable dimension as **fails**, **needs work**, or **works**, with a timestamp and reason. Use **not checked** for unavailable evidence; do not turn it into a favorable score. Numbers are optional communication aids, not objective quality measurements.

| Dimension | Test |
| --- | --- |
| Opening | Does the first meaningful beat establish relevance, tension, or a clear promise? |
| Truth and story | Do real assets support the claim, and does every shot advance understanding? |
| Readability | Can the viewer read while following the action at intended display size? |
| Hierarchy | Is it clear where to look after each event? |
| Continuity | Can the viewer follow object identity, cause/effect, scale, and location? |
| Motion | Do speed, weight, easing, and holds fit the subject without stutter or collisions? |
| Sound | Are speech, effects, music, captions, and picture connected and comfortably balanced? |
| Finish | Are the cover, ending, safe areas, encoding, and requested variants deliberate and intact? |

## Write actionable defects

Use this shape:

```text
ID: R1-02
Evidence: r01-wide/frames/frame-000312.png; 5.200s; proof panel
Observed: The heading covers the result value during the incoming panel move.
Consequence: The proof cannot be read at its first emphasis beat.
Local repair: Delay the heading entrance until the panel settles; preserve the cue.
Recheck: Panel entrance, midpoint, settled proof, and next transition at normal speed.
Status: Open / repaired and rechecked / unresolved
```

Avoid "make it pop," "more premium," or speculation without an observed defect. Repair up to three high-impact issues per pass. Preserve unrelated approved work. A structure problem can justify changing several shots, but explain that causal link before expanding the repair.

## Stop conditions and final status

Stop when applicable checks have evidence, material defects are resolved, and the requested output exists. Do not keep polishing because another effect is available. If access, time, or repeated unsuccessful repairs prevents completion, identify the precise missing check or decision and preserve the candidate for continuation.

Use separate status lines for technical checks, visual review, listening, and owner acceptance. Keep final-owner acceptance pending unless the user actually gives it. Revisit affected evidence after any source, asset, timing, or encode change.
