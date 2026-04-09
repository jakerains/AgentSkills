# Sound Effects Generation

Create cinematic sound effects from text descriptions.

## Overview

The ElevenLabs sound effects API generates high-quality audio effects from text prompts with precise control over timing, style, and complexity.

**Use Cases:**
- Film & trailer sound design
- Game audio and interactive media
- Foley and ambient sounds
- Video content production
- Music production elements

## Basic Usage

### MCP Tool
```
mcp__ElevenLabs__text_to_sound_effects
- text: "Heavy wooden door creaking open slowly"
- duration_seconds: 3.0
- loop: false
```

### Python SDK
```python
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="your-api-key")

audio = client.sound_effects.convert(
    text="Glass shattering on concrete floor",
    duration_seconds=2.5,
    prompt_influence=0.5
)

# Save to file
with open("shatter.mp3", "wb") as f:
    f.write(audio)
```

## Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| `duration_seconds` | 0.5-30 | Length of generated audio |
| `loop` | true/false | Enable seamless looping |
| `prompt_influence` | 0-1 | How strictly to follow prompt |

### Duration
- **Default**: Automatically determined from prompt
- **Range**: 0.1 to 30 seconds
- **Cost**: 40 credits per second when specified

### Looping
- Creates seamless audio that can repeat indefinitely
- Perfect for ambient sounds, background textures
- Great for: rain, wind, crowds, machinery hums

### Prompt Influence
- **High (0.7-1.0)**: Literal interpretation
- **Low (0.0-0.3)**: Creative variations added

## Prompting Guide

### Simple Effects
Use clear, concise descriptions:
- "Glass shattering on concrete"
- "Heavy wooden door creaking open"
- "Thunder rumbling in the distance"
- "Car engine starting and idling"
- "Footsteps on gravel path"

### Complex Sequences
Describe the sequence of events:
- "Footsteps on gravel, then a metallic door opens"
- "Wind whistling through trees, followed by leaves rustling"
- "Sword being drawn, then clashing with another blade"
- "Keyboard typing, mouse click, then notification sound"

### Layered Sounds
Combine multiple elements:
- "Busy cafe: espresso machine, conversations, dishes clinking"
- "Forest at night: crickets, owl hooting, distant stream"
- "Office ambiance: HVAC hum, keyboards, muffled phone"

### Musical Elements
Generate musical components:
- "90s hip-hop drum loop, 90 BPM"
- "Vintage brass stabs in F minor"
- "Atmospheric synth pad with subtle modulation"
- "Punchy kick drum with tight attack"
- "Crisp hi-hat pattern, 16th notes"

## Audio Terminology

Use these terms to enhance prompts:

| Term | Description |
|------|-------------|
| **Impact** | Collision sounds, from taps to crashes |
| **Whoosh** | Movement through air, fast to slow |
| **Ambience** | Background environmental sounds |
| **One-shot** | Single, non-repeating sound |
| **Loop** | Repeating audio segment |
| **Stem** | Isolated audio component |
| **Braam** | Big, brassy cinematic hit (trailers) |
| **Glitch** | Malfunction, jittering sounds (sci-fi) |
| **Drone** | Continuous textured sound (suspense) |
| **Riser** | Sound that builds in pitch/intensity |
| **Stinger** | Short dramatic accent |
| **Foley** | Everyday sound effects (footsteps, doors) |
| **Atmos** | Atmospheric background sound |

## Examples by Category

### Cinematic
```
"Epic orchestral hit with brass and timpani"
"Tension riser building to dramatic impact"
"Sci-fi energy beam charging and firing"
"Horror stinger with dissonant strings"
```

### Nature
```
"Gentle rain on a tin roof"
"Ocean waves crashing on rocky shore"
"Wind howling through mountain pass"
"Crackling campfire with popping embers"
```

### Urban
```
"City traffic with horns and engines"
"Subway train arriving at platform"
"Busy restaurant kitchen"
"Construction site with jackhammer"
```

### Mechanical
```
"Hydraulic press engaging and releasing"
"Old clock ticking with occasional chime"
"Computer hard drive spinning up"
"Steam engine starting and running"
```

### UI/Digital
```
"Notification chime, bright and friendly"
"Error buzz, short and urgent"
"Success sound, uplifting completion"
"Button click, satisfying mechanical"
```

### Gaming
```
"Power-up collection, sparkly and rewarding"
"Health pickup, refreshing heal sound"
"Weapon reload, metallic and precise"
"Level complete fanfare"
```

## Best Practices

### Prompt Writing
1. **Be specific**: "Heavy wooden door" vs "door"
2. **Include materials**: "Metal clang" vs "impact sound"
3. **Describe movement**: "Slowly creaking" vs "opening"
4. **Add context**: "In large empty room" for reverb

### Workflow
1. Generate multiple variations
2. Use lower prompt_influence for creative options
3. Combine generated sounds in DAW
4. Layer with other elements

### Technical Tips
- Start with slightly longer duration, trim later
- Use looping for seamless ambient tracks
- Lower prompt_influence for background sounds
- Higher prompt_influence for specific SFX

## Output Formats

| Format | Quality | Notes |
|--------|---------|-------|
| MP3 | 44.1kHz, 128-192kbps | Default |
| WAV | 48kHz | Industry standard (non-looping only) |

WAV downloads at 48kHz are industry standard for film, TV, video, and game audio.

## Limitations

- **Max duration**: 30 seconds per generation
- **For longer**: Generate multiple and combine, or use looping
- **Not optimized for**: Isolating vocals from music
- **May vary**: Complex sequences might need multiple attempts

## Pricing

- **40 credits per second** when duration is specified
- Automatically determined duration: Varies by prompt
- See [elevenlabs.io/pricing](https://elevenlabs.io/pricing)
