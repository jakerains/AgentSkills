# ElevenLabs CLI Guide

The ElevenLabs CLI provides two main interfaces: the **Python SDK CLI** (pip) for general audio operations, and the **Agents CLI** (npm) for voice agent development.

## Table of Contents

- [Python SDK CLI](#python-sdk-cli)
- [Agents CLI](#agents-cli)
- [Which CLI to Use](#which-cli-to-use)

---

## Python SDK CLI

Installed via the Python SDK. General-purpose audio operations.

### Install

```bash
pip install elevenlabs
```

### Authentication

```bash
# Set API key as environment variable
export ELEVENLABS_API_KEY="your-key"

# Or pass directly to commands
```

The Python SDK is primarily used as a library (see [api-endpoints.md](api-endpoints.md)), but the `elevenlabs` package also installs a `play` utility for audio playback:

```python
from elevenlabs import play
from elevenlabs.client import ElevenLabs

client = ElevenLabs()
audio = client.text_to_speech.convert(text="Hello", voice_id="JBFqnCBsd6RMkjVDRZzb")
play(audio)
```

Requires `mpv` and/or `ffmpeg` for playback:
```bash
# macOS
brew install mpv ffmpeg

# Ubuntu
sudo apt install mpv ffmpeg
```

---

## Agents CLI

The dedicated CLI for building, testing, and deploying ElevenLabs voice agents. This is the primary CLI tool.

### Install

```bash
npm install -g @elevenlabs/cli
```

### Authentication

```bash
elevenlabs auth login              # Browser-based OAuth login
elevenlabs auth whoami             # Check current user
elevenlabs auth logout             # Log out
elevenlabs auth residency <region> # Set data residency (enterprise)
```

### Project Setup

```bash
# Initialize a new agents project
elevenlabs agents init

# Creates:
# agents.json    — agent registry
# tools.json     — tool definitions
# tests.json     — test configs
# agent_configs/ — agent JSON configs
# tool_configs/  — tool JSON configs
# test_configs/  — test configs
```

### Agent Commands

```bash
# Create agent from template
elevenlabs agents add "My Bot" --template customer-service

# Create from existing config file
elevenlabs agents add --from-file config.json

# List all agents
elevenlabs agents list

# Check sync status (local vs remote)
elevenlabs agents status

# Push local changes to ElevenLabs
elevenlabs agents push

# Preview push without applying
elevenlabs agents push --dry-run

# Pull remote agents to local
elevenlabs agents pull

# Delete an agent
elevenlabs agents delete <agent-id>

# Generate embed widget HTML
elevenlabs agents widget <agent-id>

# Run agent tests
elevenlabs agents test <agent-id>
```

### Tool Commands

```bash
# Add a webhook tool
elevenlabs tools add-webhook "Tool Name" --config-path ./tool.json

# Add a client tool (frontend-triggered)
elevenlabs tools add-client "Tool Name" --config-path ./tool.json

# Sync tools
elevenlabs tools push
elevenlabs tools pull

# Delete tool
elevenlabs tools delete <tool-id>
```

### Test Commands

```bash
# Add a test
elevenlabs tests add "Test Name" --template basic-llm

# Push tests
elevenlabs tests push
```

### Templates

| Template | Use Case | Temperature |
|----------|----------|-------------|
| `customer-service` | Support bots, order tracking | 0.1 |
| `assistant` | General purpose helper | 0.3 |
| `voice-only` | Voice-first interactions | 0.3 |
| `text-only` | Text chat only | 0.3 |
| `minimal` | Quick prototyping | 0.3 |
| `default` | Full options exposed | 0.3 |

### Typical Workflow

```bash
# 1. Setup
elevenlabs agents init
elevenlabs auth login

# 2. Create agent
elevenlabs agents add "Support Bot" --template customer-service

# 3. Edit config in agent_configs/support-bot.json

# 4. Add tools
elevenlabs tools add-webhook "Check Order" --config-path ./tools/check-order.json
elevenlabs tools push

# 5. Test locally
elevenlabs agents push --dry-run
elevenlabs agents test <agent-id>

# 6. Deploy
elevenlabs agents push

# 7. Embed
elevenlabs agents widget <agent-id>
```

For full agent configuration schema, tool types, prompting guide, and telephony integration, see [voice-agents.md](voice-agents.md).

---

## Which CLI to Use

| Task | Tool |
|------|------|
| Generate speech from text | Python SDK (library) or MCP |
| Transcribe audio | Python SDK (library) or MCP |
| Clone a voice | MCP or Python SDK |
| Create/manage voice agents | **Agents CLI** (`@elevenlabs/cli`) |
| Deploy agents to production | **Agents CLI** |
| Add agent tools/webhooks | **Agents CLI** |
| Test agent conversations | **Agents CLI** |
| Dub video, generate SFX, music | Python SDK (library) or MCP |
| Anything not in MCP/CLI | Python SDK (library) — see [api-endpoints.md](api-endpoints.md) |

The MCP server (see [mcp-setup.md](mcp-setup.md)) is usually the best choice when working inside an AI coding agent, since tools are called directly. Use the Agents CLI for agent development workflows, and the Python/Node SDK for everything else.
