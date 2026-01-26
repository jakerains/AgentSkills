# Music Generation (Eleven Music)

Generate studio-grade music with natural language prompts.

## Overview

Eleven Music creates complete songs or instrumentals in any style from text prompts. Cleared for commercial use including film, TV, podcasts, ads, and games.

**Features:**
- Complete genre/style/structure control
- Vocals or instrumental only
- Multilingual lyrics
- Edit individual sections
- 10 seconds to 5 minutes

## Basic Usage

### MCP Tool
```
mcp__ElevenLabs__compose_music
- prompt: "Upbeat electronic track with driving synths, 120 BPM"
- music_length_ms: 60000
```

### Composition Plan (Advanced)
```
mcp__ElevenLabs__create_composition_plan
- prompt: "Energetic rock song with guitar solos"
- music_length_ms: 180000
```

Then use the plan with `compose_music`:
```
mcp__ElevenLabs__compose_music
- composition_plan: {plan from above}
```

## Composition Plan Schema

For precise control over song structure:

```json
{
  "positive_global_styles": ["rock", "energetic", "guitar-driven"],
  "negative_global_styles": ["electronic", "slow"],
  "sections": [
    {
      "section_name": "intro",
      "duration_ms": 15000,
      "positive_local_styles": ["building", "drums only"],
      "negative_local_styles": ["vocals"],
      "lines": []
    },
    {
      "section_name": "verse1",
      "duration_ms": 30000,
      "positive_local_styles": ["melodic", "guitar riff"],
      "negative_local_styles": [],
      "lines": ["First line of lyrics", "Second line here"]
    },
    {
      "section_name": "chorus",
      "duration_ms": 25000,
      "positive_local_styles": ["powerful", "full band"],
      "negative_local_styles": [],
      "lines": ["Chorus lyrics go here"]
    }
  ]
}
```

### Section Fields

| Field | Description |
|-------|-------------|
| `section_name` | Intro, verse, chorus, bridge, outro, etc. |
| `duration_ms` | Length of section in milliseconds |
| `positive_local_styles` | Styles to include in this section |
| `negative_local_styles` | Styles to avoid in this section |
| `lines` | Lyrics for this section (empty for instrumental) |

### Global vs Local Styles

- **Global styles**: Apply to entire song (genre, mood, tempo)
- **Local styles**: Apply to specific section (intensity, instrumentation)

## Prompting Guide

### Basic Prompts
```
"Chill lo-fi hip hop beat for studying"
"Epic orchestral trailer music"
"Acoustic folk song about traveling"
"80s synthwave with driving bassline"
```

### Detailed Prompts
```
"Upbeat indie pop song, female vocals,
jangly guitars, 120 BPM, summer vibes,
verse-chorus-verse-chorus-bridge-chorus structure"
```

### Genre Examples

**Electronic:**
```
"Deep house track, 122 BPM, rolling bassline,
atmospheric pads, subtle vocal chops"
```

**Rock:**
```
"Heavy rock anthem, powerful drums,
distorted guitars, soaring chorus, arena-ready"
```

**Classical:**
```
"Romantic piano piece, Chopin-inspired,
melancholic yet hopeful, rubato timing"
```

**Hip Hop:**
```
"Trap beat, 140 BPM, 808 bass,
crisp hi-hats, dark atmospheric melody"
```

**Jazz:**
```
"Smooth jazz, walking bass,
brushed drums, mellow saxophone lead"
```

### Instrumental vs Vocals

**Instrumental only:**
```
"Instrumental ambient electronic, no vocals"
```

**With vocals:**
```
"Pop song with female vocals about summer love"
```

**Specify vocal style:**
```
"R&B track, soulful male vocals, falsetto in chorus"
```

## Editing Sections

After generating, you can:
1. Regenerate specific sections
2. Modify lyrics for a section
3. Change style for a section
4. Adjust section duration

This allows iterative refinement without regenerating the entire track.

## Style Keywords

### Moods
- Energetic, calm, melancholic, uplifting
- Dark, bright, mysterious, triumphant
- Nostalgic, futuristic, romantic, aggressive

### Tempo/Feel
- Fast, slow, moderate, driving
- Groovy, steady, syncopated, rubato

### Instrumentation
- Piano, guitar, synth, strings
- Drums, bass, brass, woodwinds
- Electronic, acoustic, orchestral

### Production
- Lo-fi, polished, raw, overproduced
- Vintage, modern, retro, futuristic
- Minimalist, layered, dense, sparse

## Supported Languages

Eleven Music can generate vocals in multiple languages:
- English
- Spanish
- German
- Japanese
- French
- And more

Specify in prompt:
```
"J-pop song with Japanese vocals"
"Spanish flamenco with traditional singing"
```

## Duration Limits

| Limit | Value |
|-------|-------|
| Minimum | 10 seconds (10,000 ms) |
| Maximum | 5 minutes (300,000 ms) |

For longer tracks:
- Generate sections separately
- Combine in a DAW
- Use consistent style prompts

## Output Format

- **Format**: MP3
- **Quality**: 44.1kHz, 128-192kbps
- **Additional formats**: Coming soon

## Commercial Usage

Eleven Music is cleared for:
- Film and television
- Podcasts and audio content
- Social media videos
- Advertisements
- Video games

See [elevenlabs.io/music-terms](https://elevenlabs.io/music-terms) for full terms by plan.

## Best Practices

### Prompt Writing
1. Start broad, then refine
2. Include genre, mood, tempo
3. Specify instrumentation
4. Describe desired energy arc

### Iteration Workflow
1. Generate initial track
2. Identify sections to improve
3. Create composition plan for precision
4. Regenerate specific sections
5. Export final version

### Quality Tips
- More specific prompts = more predictable results
- Use negative styles to avoid unwanted elements
- Section-by-section control for complex arrangements
- Generate multiple variations, pick the best

## Pricing

Music generation is billed per generation based on duration.
See [elevenlabs.io/pricing](https://elevenlabs.io/pricing) for current rates.

### Concurrency Limits by Plan

| Plan | Music Concurrency |
|------|------------------|
| Free | 0 |
| Starter | 2 |
| Creator | 2 |
| Pro | 2 |
| Scale | 5 |
| Business | 5 |
