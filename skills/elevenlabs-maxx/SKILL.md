---
name: elevenlabs-maxx
description: "Complete ElevenLabs AI audio platform: text-to-speech (TTS), speech-to-text (STT/Scribe), voice cloning, voice design, sound effects, music generation, text-to-dialogue (multi-speaker), dubbing, voice changer, voice isolator, forced alignment, and conversational voice agents. Covers three interfaces: MCP tools (24 tools for direct agent use), Agents CLI (@elevenlabs/cli), and Python/Node SDK for API-only features. Use when working with audio generation, voice synthesis, transcription, audio processing, building voice-enabled applications, or any ElevenLabs integration. Triggers: generate speech, clone voice, transcribe audio, create sound effects, compose music, dub video, change voice, isolate vocals, build voice agent, multi-speaker dialogue, align text to audio, ElevenLabs API/SDK/CLI/MCP setup."
---

# ElevenLabs AI Audio Platform

Three ways to use ElevenLabs from an AI agent:

| Interface | Install | Best For |
|-----------|---------|----------|
| **MCP Server** | `uvx elevenlabs-mcp` | Direct tool calls from agent (24 tools) |
| **Agents CLI** | `npm i -g @elevenlabs/cli` | Voice agent dev workflow |
| **Python/Node SDK** | `pip install elevenlabs` | API-only features, scripting |

## Quick Reference

| Capability | MCP Tool | SDK Method | Notes |
|-----------|----------|------------|-------|
| Text-to-Speech | `text_to_speech` | `client.text_to_speech.convert()` | |
| Speech-to-Text | `speech_to_text` | `client.speech_to_text.convert()` | Scribe v2, 90+ languages |
| Voice Cloning | `voice_clone` | — | Instant: 30s audio, Pro: 30min |
| Voice Design | `text_to_voice` | `client.voice_design.generate()` | Creates 3 previews |
| Sound Effects | `text_to_sound_effects` | `client.text_to_sound_effects.convert()` | 0.5-30 seconds |
| Music | `compose_music` | `client.music.compose()` | 10s-5min |
| Voice Changer | `speech_to_speech` | `client.speech_to_speech.convert()` | |
| Audio Isolation | `isolate_audio` | `client.audio_isolation.audio_isolation()` | |
| Voice Agents | `create_agent` | `client.agents.create()` | Also via CLI |
| **Text-to-Dialogue** | — | `client.text_to_dialogue.convert()` | **API only** |
| **Dubbing** | — | `client.dubbing.create()` | **API only**, 32 langs |
| **Forced Alignment** | — | `client.forced_alignment.create()` | **API only** |
| **Studio/Projects** | — | `client.studio.get_projects()` | **API only**, audiobooks |
| **History** | — | `client.history.get_all()` | **API only** |
| **Pronunciation Dicts** | — | `client.pronunciation_dictionaries.list()` | **API only** |

Items marked **API only** are not available through MCP or CLI — use the Python/Node SDK or curl. See [references/api-endpoints.md](references/api-endpoints.md).

## Setup

### API Key

```bash
export ELEVENLABS_API_KEY="your-api-key"
```

Get one at https://elevenlabs.io/app/settings/api-keys (free tier: 10k credits/month).

### MCP Server (Recommended for AI Agents)

For Claude Code, add to `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "ElevenLabs": {
      "command": "uvx",
      "args": ["elevenlabs-mcp"],
      "env": {
        "ELEVENLABS_API_KEY": "your-api-key"
      }
    }
  }
}
```

Or add interactively: `claude mcp add ElevenLabs -- uvx elevenlabs-mcp`

Optional env vars:
- `ELEVENLABS_MCP_BASE_PATH` — where files are saved (default: `~/Desktop`)
- `ELEVENLABS_MCP_OUTPUT_MODE` — `files` (default), `resources`, or `both`

For full setup (Claude Desktop, Cursor, Windsurf, troubleshooting): see [references/mcp-setup.md](references/mcp-setup.md).

### SDK Installation

```bash
# Python
pip install elevenlabs

# TypeScript/Node
npm install @elevenlabs/elevenlabs-js
```

### Agents CLI

```bash
npm install -g @elevenlabs/cli
elevenlabs auth login
```

See [references/cli-guide.md](references/cli-guide.md) for full CLI reference.

## Text-to-Speech (TTS)

### MCP

```
mcp__ElevenLabs__text_to_speech
- text: "Your text here"
- voice_name: "Rachel" (or voice_id)
- model_id: "eleven_multilingual_v2"
- stability: 0.5, similarity_boost: 0.75
- speed: 1.0 (range: 0.7-1.2)
```

### Python SDK

```python
from elevenlabs.client import ElevenLabs
from elevenlabs import play

client = ElevenLabs(api_key="your-key")

audio = client.text_to_speech.convert(
    text="Hello world!",
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # George
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128"
)
play(audio)
```

### Models

| Model | Latency | Languages | Best For |
|-------|---------|-----------|----------|
| `eleven_multilingual_v2` | ~500ms | 29 | High quality, long-form |
| `eleven_flash_v2_5` | ~75ms | 32 | Real-time, agents |
| `eleven_turbo_v2_5` | ~250ms | 32 | Balanced quality/speed |
| `eleven_v3` | Higher | 70+ | Emotional, dramatic |

For voice settings, output formats, speed control, and pronunciation dictionaries: see [references/tts-models.md](references/tts-models.md).

## Speech-to-Text (Scribe)

### MCP

```
mcp__ElevenLabs__speech_to_text
- input_file_path: "/path/to/audio.mp3"
- diarize: true
- language_code: "eng" (or auto-detect)
```

### Python SDK

```python
result = client.speech_to_text.convert(
    file=open("audio.mp3", "rb"),
    model_id="scribe_v2",
    diarize=True,
    tag_audio_events=True
)
print(result.text)
```

Features: 90+ languages, word-level timestamps, speaker diarization (up to 48 speakers), keyterm prompting, entity detection (56 types), realtime mode (~150ms). See [references/stt-scribe.md](references/stt-scribe.md).

## Voice Cloning & Design

### Clone (MCP)

```
mcp__ElevenLabs__voice_clone
- name: "My Voice"
- files: ["/path/to/sample1.mp3", "/path/to/sample2.mp3"]
- description: "Professional male voice"
```

Requirements: **Instant** — 30+ seconds clean audio. **Professional** — 30+ minutes (Creator+ plan).

### Design from Description (MCP)

```
mcp__ElevenLabs__text_to_voice
- voice_description: "A warm, friendly male voice with a slight British accent"
```

Creates 3 previews. Save with `create_voice_from_preview`.

## Sound Effects

```
mcp__ElevenLabs__text_to_sound_effects
- text: "Heavy wooden door creaking open slowly"
- duration_seconds: 3.0 (0.5-30)
- loop: false
```

Prompting tips and examples: see [references/sound-effects.md](references/sound-effects.md).

## Music Generation

```
mcp__ElevenLabs__compose_music
- prompt: "Upbeat electronic track with driving synths, 120 BPM"
- music_length_ms: 60000 (10s-5min)
```

For composition plans, genre examples, and lyrics: see [references/music-generation.md](references/music-generation.md).

## Voice Changer (Speech-to-Speech)

```
mcp__ElevenLabs__speech_to_speech
- input_file_path: "/path/to/recording.mp3"
- voice_id: "target_voice_id"
```

Preserves whispers, laughs, emotional cues. 29 languages.

## Audio Isolation

```
mcp__ElevenLabs__isolate_audio
- input_file_path: "/path/to/noisy_audio.mp3"
```

Removes background noise. Supports audio/video up to 500MB / 1 hour.

## Text-to-Dialogue (API Only)

Multi-speaker dialogue — each line mapped to a different voice. Not available via MCP.

```python
audio = client.text_to_dialogue.convert(
    dialogue=[
        {"text": "Welcome to the show!", "voice_id": "JBFqnCBsd6RMkjVDRZzb"},
        {"text": "Thanks for having me.", "voice_id": "pNInz6obpgDQGcFmaJgB"},
    ],
    model_id="eleven_multilingual_v2"
)
```

Also available with timestamps: `client.text_to_dialogue.convert_with_timestamps()`. See [references/api-endpoints.md](references/api-endpoints.md).

## Dubbing (API Only)

Translate video/audio while preserving speaker voices. 32 languages, up to 9 speakers, 1GB files.

```python
result = client.dubbing.create(
    file=open("video.mp4", "rb"),
    target_lang="es",
    source_lang="en",
    num_speakers=2
)
```

See [references/dubbing.md](references/dubbing.md).

## Conversational Voice Agents

### MCP Tools

```
mcp__ElevenLabs__create_agent         # Create agent
mcp__ElevenLabs__get_agent            # Get config
mcp__ElevenLabs__list_agents          # List all
mcp__ElevenLabs__add_knowledge_base_to_agent  # Attach docs
mcp__ElevenLabs__make_outbound_call   # Call a phone number
mcp__ElevenLabs__list_conversations   # View conversations
mcp__ElevenLabs__get_conversation     # Get transcript
mcp__ElevenLabs__list_phone_numbers   # Available numbers
```

### CLI Workflow

```bash
elevenlabs agents init
elevenlabs auth login
elevenlabs agents add "Support Bot" --template customer-service
# Edit agent_configs/support-bot.json
elevenlabs agents push
```

### API-Only Agent Features

Via SDK only: duplicate agents, simulate conversations, branching/version control, deployments, conversation analytics (semantic search, text search, analysis). See [references/api-endpoints.md](references/api-endpoints.md#agent-advanced-operations).

For full agent guide (config schema, tools, prompting, telephony, embedding): see [references/voice-agents.md](references/voice-agents.md).
For prompt engineering: see [references/agent-prompting.md](references/agent-prompting.md).

## Voice Library

### Search Your Voices

```
mcp__ElevenLabs__search_voices
- search: "professional narrator"
```

### Search Public Library

```
mcp__ElevenLabs__search_voice_library
- search: "deep male"
- page_size: 10
```

### Popular Voices

| Voice | ID | Style |
|-------|-----|-------|
| Rachel | 21m00Tcm4TlvDq8ikWAM | Neutral, professional |
| Adam | pNInz6obpgDQGcFmaJgB | Deep, warm |
| George | JBFqnCBsd6RMkjVDRZzb | British, warm |
| Bella | EXAVITQu4vr4xnSDxMaL | Soft, gentle |

Browse 10,000+ voices: https://elevenlabs.io/voice-library

## Account

```
mcp__ElevenLabs__check_subscription   # Plan, credits, usage
mcp__ElevenLabs__list_models          # Available models
mcp__ElevenLabs__play_audio           # Play audio file
```

## Reference Documentation

| Topic | File |
|-------|------|
| **MCP Setup & Tools** | [references/mcp-setup.md](references/mcp-setup.md) |
| **API-Only Endpoints** | [references/api-endpoints.md](references/api-endpoints.md) |
| **CLI Guide** | [references/cli-guide.md](references/cli-guide.md) |
| TTS Models & Parameters | [references/tts-models.md](references/tts-models.md) |
| Speech-to-Text (Scribe) | [references/stt-scribe.md](references/stt-scribe.md) |
| Sound Effects Prompting | [references/sound-effects.md](references/sound-effects.md) |
| Music Generation | [references/music-generation.md](references/music-generation.md) |
| Voice Agents (Full Guide) | [references/voice-agents.md](references/voice-agents.md) |
| Agent Prompting Guide | [references/agent-prompting.md](references/agent-prompting.md) |
| Dubbing Guide | [references/dubbing.md](references/dubbing.md) |

## Pricing

- **TTS**: Per character (Flash models 50% cheaper)
- **STT**: Per hour of audio
- **Sound Effects**: 40 credits/second
- **Music**: Per generation
- **Dialogue**: Per character across all speakers
- Full pricing: https://elevenlabs.io/pricing

### Concurrency Limits

| Plan | Multilingual v2 | Flash/Turbo | STT |
|------|-----------------|-------------|-----|
| Free | 2 | 4 | 8 |
| Starter | 3 | 6 | 12 |
| Creator | 5 | 10 | 20 |
| Pro | 10 | 20 | 40 |
| Scale | 15 | 30 | 60 |
