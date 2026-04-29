# Kain Image Style

Use this when Jake asks for a Kain / GenAIAlien image, avatar, poster, meme, parody, sticker, or social graphic.

## Reference Priority

Use the image assets in this order:

1. `assets/reference-images/core-likeness/` for Kain's actual look, mascot identity, palette, face, antennae, body shape, and brand lockup.
2. `assets/reference-images/style-examples/` for poster treatments, cosmic/simulation texture, typography scale, and social graphic composition.
3. `assets/reference-images/parody-examples/` only when Jake asks for a parody, costume, genre riff, meme, or alternate scenario.
4. `assets/reference-images/generated-scenes/` for successful scene compositions that preserve the Kain likeness across settings.

Do not use parody examples as the primary likeness source. They show how far Kain can flex while staying recognizable; they are not the default face/body reference.

Do not use generated scenes as the primary likeness source either. They are proven examples of scenario handling, mood, lighting, and composition once the core likeness is already locked.

## Stable Character Traits

Keep these traits recognizable across styles:
- Bright green alien mascot.
- Round head and small rounded body.
- Two antennae with round green bulbs.
- Oversized glossy black eyes with white highlights.
- Small friendly mouth by default.
- Thick cream or white sticker-like outline.
- Simple rounded limbs and hands.
- Purple/cosmic brand energy as the default background family.
- Playful, warm, weird, GenAI-obsessed energy.

## Brand Palette

Default colors:
- Lime/bright green body.
- Deep purple background.
- Cream/off-white display type and outlines.
- Dark teal/near-black linework.

Allowed expansion colors:
- Orange/yellow spotlight for parody posters.
- Rainbow/sparkle effects for simulation/cosmic concepts.
- Dark teal/blue horror environments.
- Red accents for horror parody only.

## Parody Rules

Kain can flex into funny scenarios while keeping the mascot truth:
- Preacher: white robe, sunglasses, microphone, big cream text, warm orange stage.
- Road-trip antihero: bucket hat, aviators, convertible, desert palette, poster typography.
- Horror riff: keep green alien silhouette but replace the face or expression with the parody element.
- Joker-style chaos: hair, makeup, purple coat, but keep antennae and glossy alien eyes.
- Simulation/cosmic: sparkles, rainbow arc, vintage poster texture, green body with digital/grid detail.

The parody should read as "Kain dressed as / riffing on the thing", not as a totally different character.

## Composition Guidance

For avatars:
- Center the face.
- Use `core-likeness/kain-core-avatar-wave.jpeg` as the primary reference.
- Keep the purple circular background and sticker outline.

For isolated full-body character generation:
- Use `core-likeness/kain-core-sticker-full-body-white-generated.png` as the primary clean full-body reference.
- Use `core-likeness/kain-core-sticker-full-body-cutout.jpeg` only as a secondary historical cutout-style reference.
- Preserve the simple standing pose language, compact body, rounded hands/feet, glossy black eyes, antennae bulbs, and thick white sticker outline.
- The checkerboard background is a cutout-style reference cue, not a required background.

For brand/title graphics:
- Use `core-likeness/kain-core-brand-lockup-full-body.jpeg`.
- Preserve the cream display type, purple field, bright green mascot, and thick outline language.

For social posters:
- Use oversized readable display text.
- Keep Kain large enough to read at thumbnail size.
- Prefer bold poster layouts over subtle realism.
- Use `style-examples/kain-style-cosmic-simulation-poster.jpeg` when the ask leans cosmic, simulation, sparkly, vintage, or public-internet poster.

For generated scenes:
- Use the core likeness references first.
- Vary setting, outfit, pose, props, lighting, and typography.
- Preserve the antennae, eye shape, green palette, and sticker outline unless Jake explicitly asks otherwise.
- Pull from parody examples only for costume, genre language, pose, poster energy, or how to bend the character without losing him.
- Pull from `generated-scenes/` to understand what "successful Kain in a world" looks like: centered/readable mascot, crisp sticker-outline identity, rich cinematic setting, playful operator energy, and no loss of the green alien silhouette.

## Reference Image Map

Core likeness references:
- `core-likeness/kain-core-avatar-wave.jpeg`: best baseline face/avatar reference; strongest source for round head, antennae, glossy eyes, friendly expression, purple circle, and sticker outline.
- `core-likeness/kain-core-sticker-full-body-white-generated.png`: best clean isolated full-body character reference; strongest source for standing proportions, plain body shape, rounded limbs, thick sticker outline, and white-background reference use.
- `core-likeness/kain-core-sticker-full-body-cutout.jpeg`: secondary historical cutout-style reference; useful for comparing body proportions, but do not copy the checkerboard background.
- `core-likeness/kain-core-brand-lockup-full-body.jpeg`: best brand/mascot lockup; use for full-body proportions, cream display type, purple/cream/green palette, and "Kain the GenAI Alien" identity.

Style examples:
- `style-examples/kain-style-cosmic-simulation-poster.jpeg`: cosmic/simulation poster treatment; use for sparkle/rainbow texture, vintage print wear, arched text, digital body detail, and big upbeat poster composition.

Parody examples:
- `parody-examples/kain-parody-chaos-joker.jpeg`: dark chaos parody; use for dramatic lighting, intense expression, costume riffing, and keeping antennae/eyes readable in a darker genre.
- `parody-examples/kain-parody-preacher-stage.jpeg`: comedy stage/parody poster; use for big readable block text, expressive costume, microphone/lectern staging, and warm spotlight palette.
- `parody-examples/kain-parody-road-trip-desert.jpeg`: cinematic road-trip parody; use for accessories, vehicle/environment integration, desert palette, and poster-style typography.
- `parody-examples/kain-parody-horror-flower-face.jpeg`: horror transformation example; use only for explicit horror/monster-style requests where Kain's green body, antennae placement, and sticker outline remain recognizable.

Generated scene examples:
- `generated-scenes/kain-scene-vegas-slots-casino.png`: successful activity scene; use for integrating Kain into a busy entertainment environment while keeping him readable.
- `generated-scenes/kain-scene-pyramid-tunnel.png`: successful exploration/adventure scene; use for flashlight, ancient-location, discovery, and mystery compositions.
- `generated-scenes/kain-scene-glacier-climb.png`: successful outdoor action scene; use for scale, cold environments, gear, and resilient but cute adventure posture.
- `generated-scenes/kain-scene-ai-command-center.png`: successful operator/control-room scene; use for AI dashboards, glowing interfaces, and curious tool-discovery energy.
- `generated-scenes/kain-scene-forbidden-library-archive.png`: successful mystical/archive scene; use for old books, secret knowledge, circuit/arcane motif blending, and conspiratorial delight.
- `generated-scenes/kain-scene-neon-saucer-storm.png`: successful kinetic sci-fi scene; use for vehicles, chaos outside/calm Kain inside, neon storm lighting, and cinematic motion.

## Likeness Guardrails

For any image generation request, keep:
- Round green head and compact green body unless Jake asks for a transformation.
- Two antennae with round green bulbs.
- Oversized glossy black eyes with bright highlights, except in explicit horror transformation requests.
- Cream/white sticker outline or clear equivalent.
- Purple/cosmic brand energy when no other setting is requested.

For parody requests:
- Keep at least three stable traits visible.
- Let clothing, props, typography, environment, and expression carry the parody.
- Avoid replacing Kain with a different character who happens to be green.
