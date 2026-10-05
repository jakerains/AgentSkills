---
name: video-director
description: Direct and refine agent-made videos with a guided brief, reference analysis, story beats, purposeful motion, sound design, and evidence-based review. Use for product films, launch videos, UI demos, explainers, motion graphics, or requests to make an AI video feel less generic, more cinematic, or more polished. Works alongside HyperFrames, Remotion, and other renderers; includes contact sheets and frame-level critique. Use "video-director guide" to walk through creative decisions. For a narrow renderer bug or export-only request, use the renderer's own instructions.
---

# Video Director

Turn a video request into deliberate decisions about story, picture, motion, and sound. Keep the director, reference analyst, timeline author, renderer, and critic as separate passes with inspectable artifacts. These are working roles, not a requirement to spawn agents.

## Start at the right stage

Read the request, existing composition, brand documents, assets, and previous review before asking questions. Preserve the user's renderer, approved wording, visual identity, and unrelated timing.

| Request | Start here | Appropriate stopping point |
| --- | --- | --- |
| "Walk me through it" / "video-director guide" | Guided brief | The next decision or artifact the user requested |
| New film with a clear brief | References and shot list | Requested preview or exports, with review evidence |
| "This feels generic" / improve an existing film | Inspect actual frames and playback | Bounded repairs with before/after evidence |
| Style exploration only | Two small, meaningfully different directions | Reviewable frames and a recommendation |
| Small edit | Affected shot and adjacent transition | Verify the edit; do not restart production |

For a guided conversation, read [guided-brief.md](references/guided-brief.md). Ask only unanswered questions that change the result, usually one or two at a time. Recommend choices in plain language. Treat "use your judgment" as permission to choose reversible creative details and record the assumptions.

Use the existing project's production documents. If none exist, adapt these templates rather than inventing another paperwork system:

- [Brief](assets/brief-template.md): takeaway, audience, constraints, asset provenance, decisions, and progress.
- [Style guide](assets/style-guide-template.md): appearance, motion grammar, sound direction, and format behavior.
- [Shot list](assets/shotlist-template.md): viewer understanding, states, timing, assets, focal point, and cues.
- [Review](assets/review-template.md): exact artifact, observed defects, repairs, and remaining checks.

For a small film, combine the sections in one document. Preserve canonical filenames such as `DESIGN.md` when the selected renderer requires them; do not create competing style guides.

## 1. Establish what the film must communicate

Write one sentence the viewer should remember. Specify audience, intended feeling, next action if any, duration, destination, aspect ratios, viewing size, and requested deliverables.

Separate three kinds of information:

- **Facts:** real product behavior, supplied copy, actual metrics, names, logos, interface states.
- **Creative choices:** composition, choreography, camera movement, pacing, texture, and sound.
- **Unknowns:** missing assets, unverified claims, unresolved direction, or unavailable playback evidence.

Use real product assets for factual demonstrations. Record each asset's path/source, intended shot, and permission or approval basis. Reuse permission already supplied. If a required screen, logo, metric, or voice is missing, retrieve it through authorized access or ask for the missing item; continue unaffected work. Keep schematic mockups visibly identified and only use them when that treatment is allowed. Never pass a convincing invention off as product proof.

For SCORM/course films, review desktop, tablet, and larger lesson-player sizes unless the user requests otherwise. For social video, review the actual target viewing size. Do not add phone checks or vertical variants to every project by default.

## 2. Extract a visual grammar

Inspect the supplied references, not merely their descriptions. If a reference cannot be opened, mark it uninspected and work from available material without claiming to have analyzed it.

Record concrete observations: palette roles and colors, typography and scale, first focal point, spatial anchors, shot rhythm, motion character, texture, lighting/depth, and relationship to sound. Separate observed traits from proposed interpretations. Transfer the grammar; retain the user's own subjects, identity, copy, and assets.

Use existing brand rules before proposing a new look. When direction is open, choose or show up to two representative frames that differ in hierarchy and motion concept, not just color. Define the style before building the full timeline.

Read [craft.md](references/craft.md) for the details that distinguish intentional direction from default effects. Select a few appropriate signature moves; do not use every technique in one film.

## 3. Storyboard changes in understanding

Give every shot a purpose, entry state, exit state, primary focal point, and reason to last as long as it does. Specify what the viewer learns or feels that they did not know or feel before it.

For UI work, map real states and persistent objects before transitions. For narration, attach visual events to the clauses they explain. Do not depict a selection, capability, or outcome that the script and actual product do not support.

An opening, friction, reveal, proof, and close can form an arc; use only the beats this film needs. A lesson, quiet brand piece, and launch reel should not inherit the same hook or pacing formula. Remove shots whose only purpose is another effect.

Create one timing source for picture, voice, music, effects, and captions. Use integer frame boundaries at the chosen frame rate and document conversions to seconds. Separate timeline time from local shot time and media trim offsets. A timing change must update dependent cues and review samples.

Review the filled shot list before detailed animation. Use [worked-example.md](references/worked-example.md) when a state-based plan needs a concrete example.

## 4. Build representative frames, then choreography

Choose the smallest renderer that fits the project; retain an existing working renderer. Read [renderers.md](references/renderers.md) and the selected tool's available skills/docs. This skill owns creative direction and evidence; the renderer's instructions own its APIs and runtime constraints.

First build the most informative settled frame of the opening, densest shot, and closing state. Inspect actual type, assets, alignment, safe areas, hierarchy, and contrast at delivery viewing size. Resolve layout before animating it.

Then choreograph by object role: small controls can respond quickly, large surfaces can settle, cameras should preserve orientation, and headlines need stable reading time. Preserve object identity, anchor points, direction, and cause/effect through transitions. Plan entrances, attention shifts, holds, and handoffs together. Use the renderer's supported transition conventions.

Keep frames seekable from explicit time, fixed assets, configuration, and seeds. Do not make animation depend on wall clocks, unseeded randomness, prior playback, or live network responses. Check several frames in non-sequential order, including the same frame twice after different seeks.

Choose frame rate, blur, texture, and quality settings deliberately. Compare a short demanding move before adding expensive effects to the whole film. Preserve text clarity and judge the encoded result; higher settings alone do not demonstrate better motion.

## 5. Compose sound with the picture

Decide early whether the film is silent, narrated, music-led, or uses sparse effects. Use authorized music and voices. Record the actual audio file, offset, useful beats/phrase changes, effect cues, and ending resolution on the shared timeline.

Sync to audible onsets and visible contact, not merely clip start times. Let story rhythm lead when a beat grid would force awkward timing. Give voice room through music level changes, quieter passages, and restrained effects. Silence is a valid choice; not every movement needs a whoosh or click.

If narration changes, recheck duration, caption timing, visual emphasis, and downstream cues. Check the film with picture and sound, with picture alone, and by listening without picture when audio is part of the intent. If listening is unavailable, report that limit; waveform or loudness measurements do not establish a successful listening review.

## 6. Critique evidence and make local repairs

Read [review.md](references/review.md). Inspect representative stills before a costly full export, then watch a rough playback in motion. Capture every major beat and a short frame strip around fast transitions; also inspect the densest shot, first frame, final readable state, and actual final frame.

For an existing or requested rendered cut, the bundled [review_frames.py](scripts/review_frames.py) creates timestamped contact sheets, source frames, and a source fingerprint. It needs Python 3, Pillow, FFmpeg, and ffprobe. Resolve the script relative to this installed skill, not a hardcoded user directory.

```bash
python3 /path/to/video-director/scripts/review_frames.py out/rough.mp4 \
  --times 0,1.5,4,7.25 --strip-at 4 --radius 3 --out reviews/r01-wide
```

If the renderer workflow calls for preview-only work, capture preview frames and review playback there; do not export an MP4 merely to feed this helper. Distinguish preview evidence from encoded-video evidence.

Judge the rendered result without defending its intent. Identify up to three highest-impact defects per repair pass. Give each a timestamp/frame, observable evidence, viewer consequence, and smallest useful fix. Repair those sections, recapture affected moments and adjacent transitions, and retain before/after evidence. Fix factual errors and broken readability before ornamental polish.

Repeat only while material defects remain and the requested time/budget permits. If two passes fail to improve the same defect, change the approach or surface the specific blocker. Do not loop indefinitely or stop because a file exists. A lack of visual/audio access is an explicit review gap, not a pass.

## 7. Recompose, deliver, and leave a reusable record

Create only requested variants. Share story, assets, and tokens, but give each aspect ratio its own layout and focal-point path; adjust density, camera path, and timing where needed. Avoid blindly cropping the wide version. Review every delivered variant independently.

Deliver the requested preview/exports, representative poster or cover, editable source, asset inventory, render/preview command, and review evidence appropriate to the task. Do not re-export for an export-free review request. Keep large intermediates out of source control and follow the project's media storage conventions.

Record tool versions, exact source revision or file hashes, render parameters, artifact paths, and checks actually performed. A source edit invalidates affected evidence; regenerating one poster does not qualify an older video. Distinguish technical checks, visual inspection, listening, and owner acceptance.

End with the result, what was checked, and any specific remaining decision. Do not claim owner approval, publication, or completion of unperformed checks.

## Checkpoints and autonomy

| Checkpoint | Evidence required to advance |
| --- | --- |
| Direction | Takeaway, inspected references, asset inventory, identified gaps |
| Plan | Concrete visual identity, purposeful shot list, shared cue plan |
| Representative frames | Actual captures showing hierarchy and layout |
| Rough playback | Motion review, beat contact sheet, transition strips |
| Repair | Timestamped defects, local changes, replacement evidence |
| Delivery | Requested variants, audio review if applicable, reproducible source and honest status |

Treat these as evidence checkpoints. Advance within the user's authorization without requesting repeated approvals. Pause for an explicitly requested review, a consequential unanswered choice, missing required facts/assets, or an action outside the task's authority. Present concrete work and one specific decision when input is needed. Do not invent mandatory owner sign-offs for every stage.
