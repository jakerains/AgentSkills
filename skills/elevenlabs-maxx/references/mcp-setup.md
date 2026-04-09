# ElevenLabs MCP Server Setup & Reference

Complete guide to installing, configuring, and using the ElevenLabs MCP server with AI coding agents.

## Table of Contents

- [Installation](#installation)
- [Configuration Options](#configuration-options)
- [Troubleshooting](#troubleshooting)
- [Complete Tool Reference](#complete-tool-reference)

## Installation

The MCP server is distributed via PyPI as `elevenlabs-mcp`. Requires `uv` (Python package manager).

### Prerequisites

1. **API Key**: Get one at https://elevenlabs.io/app/settings/api-keys (free tier: 10k credits/month)
2. **uv**: Install with `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Claude Code

Add to your project's `.mcp.json` (project-level) or `~/.claude/settings.json` (global):

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

Or add interactively:
```bash
claude mcp add ElevenLabs -- uvx elevenlabs-mcp
```

Then set the env var in your shell or `.env`:
```bash
export ELEVENLABS_API_KEY="your-api-key"
```

### Claude Desktop

Go to Claude > Settings > Developer > Edit Config > `claude_desktop_config.json`:

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

Windows users: enable "Developer Mode" in Claude Desktop (Help menu > Enable Developer Mode).

### Cursor / Windsurf / Other MCP Clients

```bash
pip install elevenlabs-mcp
python -m elevenlabs_mcp --api-key=YOUR_KEY --print
```

Paste the output JSON into your client's MCP configuration.

## Configuration Options

### Output Mode (`ELEVENLABS_MCP_OUTPUT_MODE`)

Controls how generated audio files are returned:

| Mode | Behavior | Best For |
|------|----------|----------|
| `files` (default) | Save to disk, return file paths | Local development |
| `resources` | Return as base64 MCP resources | Cloud/serverless, no disk access |
| `both` | Save to disk AND return as resources | Maximum flexibility |

```json
{
  "env": {
    "ELEVENLABS_API_KEY": "your-key",
    "ELEVENLABS_MCP_OUTPUT_MODE": "files"
  }
}
```

### Base Path (`ELEVENLABS_MCP_BASE_PATH`)

Where generated files are saved. Defaults to `~/Desktop`.

```json
{
  "env": {
    "ELEVENLABS_MCP_BASE_PATH": "/Users/you/Projects/audio-output"
  }
}
```

### Data Residency (`ELEVENLABS_API_RESIDENCY`)

Enterprise only. Set region for data processing. Defaults to `"us"`.

## Troubleshooting

### "spawn uvx ENOENT"

The system can't find `uvx`. Get its absolute path and use that:

```bash
which uvx
# e.g., /usr/local/bin/uvx
```

Update config:
```json
{
  "command": "/usr/local/bin/uvx"
}
```

### Timeouts on Voice Design / Audio Isolation

Some operations (voice design, audio isolation) take longer to process. This can cause timeouts in MCP Inspector dev mode but should work fine in Claude Desktop/Code clients.

### Tools Not Appearing

1. Verify the API key is valid: `curl -H "xi-api-key: YOUR_KEY" https://api.elevenlabs.io/v1/user`
2. Check the MCP server is running: look for `elevenlabs-mcp` in your process list
3. Restart your MCP client after config changes

## Complete Tool Reference

### Audio Generation

| Tool | Description |
|------|-------------|
| `text_to_speech` | Convert text to speech. Params: text, voice_name/voice_id, model_id, stability, similarity_boost, style, speed, output_format, language_code |
| `speech_to_speech` | Transform audio to a different voice. Params: input_file_path, voice_id/voice_name, model_id |
| `text_to_sound_effects` | Generate sound effects from text descriptions. Params: text, duration_seconds (0.5-30), loop, prompt_influence |
| `compose_music` | Generate music from a prompt. Params: prompt, music_length_ms (10s-5min) |
| `create_composition_plan` | Create structured music with sections, styles, lyrics. Params: prompt (for AI-generated plan) |

### Voice Management

| Tool | Description |
|------|-------------|
| `search_voices` | Search your voice library. Params: search, sort |
| `search_voice_library` | Search the public voice library. Params: search, page_size |
| `get_voice` | Get details about a specific voice. Params: voice_id |
| `voice_clone` | Clone a voice from audio samples. Params: name, files[], description |
| `text_to_voice` | Design a new voice from text description. Params: voice_description |
| `create_voice_from_preview` | Save a voice preview to your library. Params: voice_id, voice_name |

### Transcription

| Tool | Description |
|------|-------------|
| `speech_to_text` | Transcribe audio to text. Params: input_file_path, diarize, language_code, tag_audio_events, timestamps_granularity |

### Audio Processing

| Tool | Description |
|------|-------------|
| `isolate_audio` | Remove background noise, isolate vocals. Params: input_file_path |
| `play_audio` | Play an audio file through speakers. Params: file_path |

### Conversational AI Agents

| Tool | Description |
|------|-------------|
| `create_agent` | Create a new voice agent. Params: name, prompt, first_message, voice_id/voice_name, model, language, tools |
| `get_agent` | Get agent configuration. Params: agent_id |
| `list_agents` | List all your agents |
| `add_knowledge_base_to_agent` | Attach documents to an agent. Params: agent_id, file_path/url/text |
| `list_conversations` | List conversations for an agent. Params: agent_id |
| `get_conversation` | Get conversation details/transcript. Params: conversation_id, agent_id |
| `make_outbound_call` | Call a phone number with an agent. Params: agent_id, phone_number |
| `list_phone_numbers` | List available phone numbers |

### Account

| Tool | Description |
|------|-------------|
| `check_subscription` | View plan, credits, usage |
| `list_models` | List all available models |

## What MCP Can't Do

The following require direct API calls (see [api-endpoints.md](api-endpoints.md)):

- Text-to-Dialogue (multi-speaker dialogue)
- Forced Alignment (sync text to audio timing)
- Studio/Projects (long-form audiobooks with chapters)
- Pronunciation Dictionaries (custom word pronunciations)
- History management (browse/delete/download past generations)
- Dubbing (translate video/audio to other languages)
- Batch Calling (outbound call campaigns)
- Audio Native (embeddable audio players)
- Workspace management (sharing, user groups)
- Conversation analytics (smart search, analysis)
- Webhook configuration
- WhatsApp / SIP trunk integration
