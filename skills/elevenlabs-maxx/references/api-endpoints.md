# ElevenLabs API Reference — Beyond MCP & CLI

This reference covers API capabilities that are **not available** through the MCP server or CLI. Use these via the Python SDK, Node.js SDK, or direct HTTP requests.

Base URL: `https://api.elevenlabs.io`
Auth header: `xi-api-key: YOUR_API_KEY`

## Table of Contents

- [Text-to-Dialogue](#text-to-dialogue)
- [Forced Alignment](#forced-alignment)
- [Dubbing API](#dubbing-api)
- [Studio / Projects](#studio--projects)
- [Pronunciation Dictionaries](#pronunciation-dictionaries)
- [History Management](#history-management)
- [Audio Native](#audio-native)
- [Conversation Analytics](#conversation-analytics)
- [Batch Calling](#batch-calling)
- [Agent Advanced Operations](#agent-advanced-operations)
- [Knowledge Base](#knowledge-base)
- [Workspace Management](#workspace-management)
- [Webhooks](#webhooks)
- [Usage & Billing](#usage--billing)

---

## Text-to-Dialogue

Generate multi-speaker dialogue from a script. Each line maps to a different voice. Not available via MCP.

**POST** `/v1/text-to-dialogue`
**POST** `/v1/text-to-dialogue/with-timestamps` (includes character-level timing)

### Python SDK

```python
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="your-key")

audio = client.text_to_dialogue.convert(
    dialogue=[
        {"text": "Welcome to the show!", "voice_id": "JBFqnCBsd6RMkjVDRZzb"},
        {"text": "Thanks for having me.", "voice_id": "pNInz6obpgDQGcFmaJgB"},
        {"text": "Let's dive right in.", "voice_id": "JBFqnCBsd6RMkjVDRZzb"},
    ],
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128"
)

with open("dialogue.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### With Timestamps

```python
result = client.text_to_dialogue.convert_with_timestamps(
    dialogue=[
        {"text": "Hello there.", "voice_id": "voice_1"},
        {"text": "Hi!", "voice_id": "voice_2"},
    ],
    model_id="eleven_multilingual_v2"
)
# Returns audio + character-level timing data for sync
```

### curl

```bash
curl -X POST "https://api.elevenlabs.io/v1/text-to-dialogue" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "eleven_multilingual_v2",
    "dialogue": [
      {"text": "Welcome!", "voice_id": "JBFqnCBsd6RMkjVDRZzb"},
      {"text": "Thanks!", "voice_id": "pNInz6obpgDQGcFmaJgB"}
    ]
  }' --output dialogue.mp3
```

**Use cases**: Podcasts, audiobook dialogue, game cutscenes, training videos with multiple speakers.

---

## Forced Alignment

Align text to audio — get exact timestamps for when each word is spoken. Not available via MCP.

**POST** `/v1/forced-alignment`

### curl

```bash
curl -X POST "https://api.elevenlabs.io/v1/forced-alignment" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.mp3" \
  -F "text=The quick brown fox jumps over the lazy dog"
```

### Python SDK

```python
result = client.forced_alignment.create(
    file=open("audio.mp3", "rb"),
    text="The quick brown fox jumps over the lazy dog"
)
# Returns word-level timestamps: [{word: "The", start: 0.1, end: 0.3}, ...]
```

**Use cases**: Subtitle generation, karaoke timing, lip sync, audio-text synchronization.

---

## Dubbing API

Translate video/audio while preserving speaker voices. MCP has `isolate_audio` but not dubbing.

**POST** `/v1/dubbing` — Create a dubbing job
**GET** `/v1/dubbing/{dubbing_id}` — Get dubbing resource
**POST** `/v1/dubbing/{dubbing_id}/dub-segment` — Regenerate specific segments
**POST** `/v1/dubbing/{dubbing_id}/add-language` — Add target language

### Python SDK

```python
# Start dubbing job
result = client.dubbing.create(
    file=open("video.mp4", "rb"),
    target_lang="es",  # Spanish
    source_lang="en",
    num_speakers=2
)

dubbing_id = result.dubbing_id
# Poll for completion, then download dubbed file
```

### Supported Languages

32 languages including: en, es, fr, de, it, pt, ja, ko, zh, ar, hi, ru, pl, nl, sv, tr, and more.

### Limits

- **Dubbing Studio**: 500MB, 45 min
- **API**: 1GB, 2.5 hours
- Up to 9 speakers auto-detected

---

## Studio / Projects

Long-form audio production (audiobooks, podcasts). Manage projects with chapters, snapshots, and streaming.

**GET** `/v1/projects` — List all Studio projects
**DELETE** `/v1/projects/{project_id}` — Delete project
**GET** `/v1/projects/{project_id}/chapters` — List chapters
**GET** `/v1/projects/{project_id}/chapters/{chapter_id}` — Get chapter details
**DELETE** `/v1/projects/{project_id}/chapters/{chapter_id}` — Delete chapter
**GET** `/v1/projects/{project_id}/snapshots` — List project snapshots
**POST** `/v1/projects/{project_id}/snapshots/{snapshot_id}/stream` — Stream project audio
**POST** `/v1/projects/{project_id}/snapshots/{snapshot_id}/archive` — Download project audio archive
**GET** `/v1/projects/{project_id}/chapters/{chapter_id}/snapshots/{snapshot_id}` — Get chapter snapshot

### Python SDK

```python
# List projects
projects = client.studio.get_projects()
for p in projects.projects:
    print(f"{p.name} - {p.state} - {len(p.chapters)} chapters")

# Get chapters for a project
chapters = client.studio.get_chapters(project_id="proj_xxx")

# Stream project audio
audio = client.studio.stream_snapshot(
    project_id="proj_xxx",
    project_snapshot_id="snap_xxx"
)
```

**Use cases**: Audiobook production, long podcast episodes, multi-chapter content.

---

## Pronunciation Dictionaries

Custom pronunciation rules using PLS (Pronunciation Lexicon Specification) files.

**GET** `/v1/pronunciation-dictionaries` — List dictionaries
**POST** `/v1/pronunciation-dictionaries/add-from-file` — Create from PLS file
**GET** `/v1/pronunciation-dictionaries/{id}` — Get dictionary details
**POST** `/v1/pronunciation-dictionaries/{id}/remove-rules` — Remove rules

### Python SDK

```python
# Create dictionary from PLS file
dictionary = client.pronunciation_dictionaries.create_from_file(
    name="Company Terms",
    file=open("terms.pls", "rb")
)

# Use with TTS
audio = client.text_to_speech.convert(
    text="Welcome to Acme Corp",
    voice_id="voice_id",
    pronunciation_dictionary_locators=[
        {"pronunciation_dictionary_id": dictionary.id, "version_id": dictionary.latest_version_id}
    ]
)
```

### PLS File Format

```xml
<?xml version="1.0" encoding="UTF-8"?>
<lexicon version="1.0" xmlns="http://www.w3.org/2005/01/pronunciation-lexicon" alphabet="ipa" xml:lang="en-US">
  <lexeme>
    <grapheme>Acme</grapheme>
    <phoneme>ˈæk.mi</phoneme>
  </lexeme>
</lexicon>
```

**Use cases**: Brand name pronunciation, technical terms, foreign names, acronyms.

---

## History Management

Browse, download, and manage past generations. Not available via MCP.

**GET** `/v1/history` — List generated items (paginated, up to 1000)
**GET** `/v1/history/{history_item_id}/audio` — Get audio from history item
**DELETE** `/v1/history/{history_item_id}` — Delete history item
**POST** `/v1/history/download` — Download multiple items (single audio or .zip)

### Python SDK

```python
# List recent generations
history = client.history.get_all(page_size=20)
for item in history.history:
    print(f"{item.date_unix} | {item.text[:50]} | {item.character_count_change_from} chars")

# Download audio from a generation
audio = client.history.get_audio(history_item_id="xxx")

# Bulk download as zip
client.history.download(history_item_ids=["id1", "id2", "id3"])
```

**Use cases**: Audit trail, regenerating content, reviewing past outputs, cost tracking.

---

## Audio Native

Embeddable audio player for blogs and articles. Converts text content to audio with a player widget.

**POST** `/v1/audio-native` — Create embeddable audio player

### curl

```bash
curl -X POST "https://api.elevenlabs.io/v1/audio-native" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Blog Post Title",
    "body": "<p>Your article content here...</p>",
    "voice_id": "21m00Tcm4TlvDq8ikWAM"
  }'
```

Returns an embed code (HTML snippet) you can place on any webpage.

**Use cases**: Blog audio versions, accessibility, article narration.

---

## Conversation Analytics

Advanced analytics for voice agent conversations. Not available via MCP's basic `list_conversations`/`get_conversation`.

**POST** `/v1/convai/conversations/{id}/analysis` — Run analysis with evaluation criteria
**GET** `/v1/convai/conversations/messages/search` — Semantic search across transcripts
**GET** `/v1/convai/conversations/messages/text-search` — Full-text/fuzzy search
**GET** `/v1/convai/conversations/{id}/audio` — Get conversation recording
**DELETE** `/v1/convai/conversations/{id}` — Delete conversation

### Python SDK

```python
# Semantic search across all conversations
results = client.conversations.messages.search(
    text_query="refund request",
    agent_id="agent_xxx"
)

# Run analysis on a conversation
analysis = client.conversations.analysis.run(
    conversation_id="conv_xxx"
)
```

**Use cases**: QA review, training data extraction, compliance monitoring, agent performance analysis.

---

## Batch Calling

Outbound call campaigns using voice agents. MCP has `make_outbound_call` for single calls only.

**POST** `/v1/convai/batch-calling/create` — Create batch calling job
**GET** `/v1/convai/batch-calling/{id}` — Get batch status

### curl

```bash
curl -X POST "https://api.elevenlabs.io/v1/convai/batch-calling/create" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent_xxx",
    "phone_numbers": ["+1234567890", "+0987654321"],
    "caller_id": "+1555000000"
  }'
```

**Use cases**: Appointment reminders, surveys, outreach campaigns, notification calls.

---

## Agent Advanced Operations

Operations beyond what the MCP `create_agent`/`get_agent` tools provide.

**POST** `/v1/convai/agents/{id}/duplicate` — Clone an agent
**POST** `/v1/convai/agents/{id}/simulate-conversation` — Test agent with simulated user
**POST** `/v1/convai/agents/{id}/simulate-conversation/stream` — Streamed simulation
**POST** `/v1/convai/agents/{id}/calculate` — Estimate LLM token usage
**GET** `/v1/convai/agents/{id}/link` — Get shareable agent link
**POST** `/v1/convai/agents/{id}/deployments/create` — Create deployment

### Branching (Version Control for Agents)

**GET** `/v1/convai/agents/{id}/branches` — List branches
**POST** `/v1/convai/agents/{id}/branches/create` — Create branch
**PATCH** `/v1/convai/agents/{id}/branches/{branch_id}` — Update branch
**POST** `/v1/convai/agents/{id}/branches/{branch_id}/merge` — Merge branch

### Drafts

**POST** `/v1/convai/agents/{id}/drafts/create` — Create draft
**DELETE** `/v1/convai/agents/{id}/drafts` — Delete draft

### Python SDK

```python
# Duplicate an agent
new_agent = client.agents.duplicate(agent_id="agent_xxx", name="Agent Copy")

# Simulate a conversation for testing
simulation = client.agents.simulate_conversation(
    agent_id="agent_xxx",
    simulation_specification={
        "simulated_user_config": {
            "prompt": "You are a frustrated customer wanting a refund",
            "first_message": "I want my money back!"
        }
    }
)

# Get shareable link
link = client.agents.get_link(agent_id="agent_xxx")
```

---

## Knowledge Base

Create knowledge base documents programmatically (MCP can attach files, but not create from raw text).

**POST** `/v1/convai/knowledge-base/create-from-text` — Create document from text

```python
doc = client.knowledge_base.create_from_text(
    text="Your knowledge content here...",
    name="Product FAQ"
)
```

Supported formats for file upload: epub, pdf, docx, txt, html.

---

## Workspace Management

Share resources and manage access within your workspace.

**POST** `/v1/workspace/resources/share` — Grant role on a resource
**POST** `/v1/workspace/resources/unshare` — Remove access
**GET** `/v1/workspace/groups/search` — Search user groups

---

## Webhooks

Configure webhooks for async notifications (dubbing completion, etc.).

See: https://elevenlabs.io/docs/eleven-api/resources/webhooks

---

## Usage & Billing

**GET** `/v1/usage/character-stats` — Character usage statistics
**GET** `/v1/user` — Get user info
**GET** `/v1/user/subscription` — Get subscription details

### Python SDK

```python
# Get subscription info
sub = client.user.get_subscription()
print(f"Plan: {sub.tier}, Credits left: {sub.character_count}/{sub.character_limit}")

# Character usage stats
usage = client.usage.get_characters_usage_metrics()
```

---

## SDK Quick Reference

### Python SDK Methods (not exhaustive)

```
client.text_to_speech.convert()              # TTS
client.text_to_speech.convert_as_stream()    # TTS streaming
client.speech_to_text.convert()              # STT
client.text_to_dialogue.convert()            # Multi-speaker
client.text_to_dialogue.convert_with_timestamps()
client.speech_to_speech.convert()            # Voice changer
client.text_to_sound_effects.convert()       # SFX
client.music.compose()                       # Music
client.music.create_composition_plan()       # Structured music
client.forced_alignment.create()             # Align text to audio
client.audio_isolation.audio_isolation()     # Isolate vocals
client.dubbing.create()                      # Dub video/audio
client.voices.get_all()                      # List voices
client.voices.get()                          # Get voice details
client.voice_design.generate()               # Design voice
client.history.get_all()                     # Browse history
client.studio.get_projects()                 # List projects
client.pronunciation_dictionaries.list()     # List dictionaries
client.agents.create()                       # Create agent
client.agents.duplicate()                    # Clone agent
client.conversations.list()                  # List conversations
client.user.get_subscription()               # Check subscription
client.models.list()                         # List models
```

### Node.js SDK

```
npm install @elevenlabs/elevenlabs-js
```

```typescript
import { ElevenLabs } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabs({ apiKey: "your-key" });
const audio = await client.textToSpeech.convert("voice_id", {
  text: "Hello!",
  model_id: "eleven_multilingual_v2",
});
```

The Node.js SDK mirrors the Python SDK's method structure. Refer to the Python examples and translate to camelCase.

### Authentication

All requests require the `xi-api-key` header:

```bash
curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/user
```

Or via SDK:
```python
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
```

### Raw Response Access (Cost Tracking)

```python
response = client.text_to_speech.with_raw_response.convert(
    text="Hello", voice_id="voice_id"
)
char_cost = response.headers.get("x-character-count")
request_id = response.headers.get("request-id")
audio_data = response.data
```
