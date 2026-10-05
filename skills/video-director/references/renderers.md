# Renderer integration

Keep creative decisions portable and runtime instructions specific. Discover the selected renderer's skills in the current host; paths and skill names vary by installation. Do not install a second renderer, replace an existing project, or edit global skills simply to apply this workflow.

## Shared contract

Represent the film through fixed assets, style tokens, shot states, timing, format configuration, and seeds. Each frame must be obtainable from its frame number/time without first playing the film. Resolve fonts and media before capture using the renderer's supported readiness mechanism.

Pick one frame rate and one conversion rule for authored cues. Record local versus absolute time and trim offsets explicitly. Generate picture and sound placement from the same cue data. Pin the project's toolchain through its existing package workflow; record versions rather than forcing this reference's historical versions.

Check seeking out of order in the source composition. Repeating a frame after a distant seek should preserve visible state. Decoding frames from an MP4 only checks that MP4, not the source's seekability.

## HyperFrames

Read the available `hyperframes` authoring skill and its required typography and multi-scene transition references; use its CLI skill for actual commands. The user's installed plugin supplies the runtime contract.

- Reuse `DESIGN.md` or `visual-style.md` as that skill requires. Put director-level motion and sound decisions in the same canonical style source.
- Build hero layouts before GSAP motion. Let CSS establish settled positions and use the runtime's timed composition/clip model.
- Follow paused, registered, synchronously built timelines and finite duration/repeats. Let the framework control media playback.
- Respect its scene-transition policy, including entrances and outgoing content remaining available to the transition. Do not translate a general suggestion for a cut or exit tween into an incompatible HyperFrames composition.
- Keep voice/music/effects on its supported audio tracks and share cue timestamps with picture. Follow the installed skill's video/audio separation rules.
- Run the available lint, validate, layout/inspect, and choreography checks required by that version. Verify CLI help and any bundled animation-map script path before invoking; do not assume a `skills/` directory exists inside the film project.
- Treat successful checks as technical evidence. Inspect the selected frames and actual playback separately.

Public contract: [HyperFrames deterministic rendering](https://hyperframes.app/docs/2-concepts/4-determinism). Confirm version-specific details from the project's tools and official docs.

## Remotion

Read the available `remotion-best-practices` router, then its creation/markup, timing, audio, and review/rendering guidance as relevant. Preserve source editing and Studio interactivity conventions from the installed version.

- Drive visual state from the frame number and configuration; use the documented animation primitives for that version. Distinguish local scene frames from root frames.
- Use seeded randomness with stable inputs. Do not drive authored video motion with wall-clock timers, CSS transitions, or playback-dependent state.
- Keep individually editable clips and scene structure compatible with the current plugin; do not freeze an older markup pattern into this skill.
- Share cue data between motion, audio placement, and captions; account for local timing offsets once.
- Register requested output formats as appropriately designed compositions/parameters. Derive total duration consistently, including transition overlaps and the audio ending.
- Capture representative frames through the documented Studio/still tools, then inspect continuous playback and sound.

The installed Remotion plugin inspected for this skill defaults to **interactive Studio preview** for general create/edit requests and reserves final rendering for an explicit render/export/MP4 request. Honor the active plugin's workflow. A contact-sheet requirement is not a reason to force a movie export. When the user has already explicitly requested exports, proceed without asking again.

Official references: [frame-based fundamentals](https://www.remotion.dev/docs/the-fundamentals), [seeded randomness](https://www.remotion.dev/docs/random), and [still compositions](https://www.remotion.dev/docs/still). Use the current rendering documentation for CLI/API details.

## Other renderers and mixed media

Apply the same brief, asset truth, shot plan, sound cues, and critique to Canvas, SVG, 3D, footage, or generated video. Use real footage/generated media where a procedural approach poorly fits organic performance. Treat such media as fixed, versioned assets in the timeline; do not imply their generation is deterministic.

Preserve the project's existing capture interface. Explain a renderer choice through the film's needs, editing workflow, reuse, or asset support. Do not attribute cinematic quality to a framework without a controlled comparison.

## Provenance of this workflow

The user supplied the article beginning "Everybody is sharing videos made with Claude Opus 5.5" on 2026-10-04. Its five-role studio, ten production steps, and bounded critique loop informed this skill. No author or original publication URL was supplied; do not invent one. Model-release claims in the article are not dependencies or verified facts of this skill.

Adaptations: evidence checkpoints rather than universal approval prompts; destination-specific viewing checks; optional requested format variants; preview-compatible review; no mandated renderer or frame rate. Technical integration was checked against the installed HyperFrames and Remotion skills and official documentation on 2026-10-04. No renderer-based film has been produced merely by creating this skill.
