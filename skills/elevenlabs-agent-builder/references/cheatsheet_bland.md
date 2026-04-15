# Bland AI → ElevenLabs Migration Cheat Sheet

A practical guide for Bland AI users migrating to ElevenLabs Conversational AI.

---

## Quick Vocabulary Translation

| Bland AI | ElevenLabs Equivalent | Notes |
|----------|----------------------|-------|
| Web Agent | Agent | Same concept |
| Inbound Phone Agent | Agent + Phone Number | Bland ties prompt to phone; EL separates them |
| Prompt | System Prompt | Main agent instructions |
| First Sentence | First Message | Opening line |
| Tools (Custom Tools) | Tools (System + Custom) | EL has built-in system tools too |
| Model (base/turbo) | LLM Model | EL uses standard model names |
| Voice | Voice | Pick from EL voice library |
| Webhook | Webhook Tool | Post-call or mid-call data push |
| Dynamic Data | Webhook / Pre-call Data | External data sources |
| Pathways | Workflow | Visual conversation flow |
| Transfer (blind) | Blind Transfer / Phone Transfer Node | One-way transfer |
| Transfer (warm) | Conference Transfer | Agent stays on line |
| Analysis Schema | Data Collection | Structured data extraction |
| max_duration | (Agent Settings) | Call duration limit |
| interruption_threshold | (Agent Settings) | How easily caller can interrupt |

---

## Architecture Differences

### Bland AI Approach
Bland uses a **flat agent model**: a single prompt with optional tools, pathways (visual flow), and dynamic data. Web agents and inbound agents share a similar config but are managed separately.

Key Bland features:
- **Pathways**: Visual conversation builder (similar to EL workflows)
- **Custom Tools**: Mid-call API calls for actions
- **Analysis Schema**: Post-call data extraction into structured JSON
- **Dynamic Data**: Pull external data into the conversation
- **Transfer**: Blind or warm transfers to human agents

### ElevenLabs Approach
ElevenLabs uses a **workflow-based model**: agents have a graph of nodes connected by edges with conditions.

Key differences:
- **Workflows are first-class**: Multi-node graphs with conditional routing
- **Edge conditions**: Natural language conditions determine node transitions
- **System tools**: Built-in tools for transfer, end call, etc.
- **Data Collection**: Define fields once, collect across the entire conversation
- **One edge per node pair**: A single edge handles both forward and backward transitions

---

## Migrating Agent Types

### Simple Bland Agent (Prompt + Voice)
The simplest Bland agent — just a prompt and voice — maps directly:

**Bland:**
```json
{
  "prompt": "You are a friendly receptionist...",
  "voice": "maya",
  "model": "base",
  "first_sentence": "Hello! How can I help you today?"
}
```

**ElevenLabs:**
- Create an agent with a Start node
- Set System Prompt = Bland's `prompt`
- Set First Message = Bland's `first_sentence`
- Pick a voice from the EL library

### Bland Agent with Pathways
Bland Pathways map to ElevenLabs Workflows:

| Bland Pathway Element | ElevenLabs Equivalent |
|----------------------|----------------------|
| Start node | Start Node (auto-created) |
| Dialogue node | Agent Node |
| Transfer node | Phone Transfer Node |
| End node | End Node |
| Branch/condition | Edge Conditions |

**Key gotcha**: In ElevenLabs, you can only have ONE edge between any pair of nodes. Use forward/backward conditions on that single edge for bidirectional flows.

### Bland Agent with Tools
Bland custom tools map to ElevenLabs webhook tools:

**Bland tool:**
```json
{
  "name": "book_appointment",
  "description": "Book an appointment for the caller",
  "url": "https://api.example.com/book",
  "method": "POST",
  "headers": {"Authorization": "Bearer xxx"},
  "body": {"name": "{{name}}", "date": "{{date}}"}
}
```

**ElevenLabs tool:**
- Create a webhook tool
- URL: same endpoint
- Method: same
- Headers: same
- Body schema: define the expected parameters
- The LLM will call it when appropriate based on the description

### Bland Agent with Analysis Schema
Bland's analysis schema extracts structured data post-call. In ElevenLabs, use **Data Collection**:

**Bland:**
```json
{
  "analysis_schema": {
    "caller_name": "The name of the person calling",
    "appointment_date": "When they want to schedule",
    "reason": "Why they're calling"
  }
}
```

**ElevenLabs Data Collection:**
| Field | Description | Type | Required |
|-------|-------------|------|----------|
| caller_name | The caller's full name | string | Yes |
| appointment_date | Requested appointment date | string | Yes |
| reason | Reason for calling | string | No |

---

## Migrating Common Patterns

### Pattern 1: Inbound Phone Agent
**Bland**: Prompt + voice attached directly to a phone number via `/v1/inbound/{number}`

**ElevenLabs**:
1. Create an Agent with system prompt and voice
2. Assign a phone number to the agent in the dashboard
3. The phone number routes to the agent

### Pattern 2: Transfer to Human
**Bland**: Use transfer tool or pathway transfer node

**ElevenLabs** (two options):
- **Phone Transfer Node**: Terminal node, no fallback if transfer fails
- **transfer_to_number System Tool** (recommended): Gives fallback — if transfer fails, agent can apologize and retry or take a message

### Pattern 3: Dynamic Data (External Context)
**Bland**: `dynamic_data` array with URLs that are fetched before/during the call

**ElevenLabs**:
- Use **webhook tools** for mid-call data fetching
- Use **pre-call webhook** to inject data before the conversation starts
- Reference external data via `{{variable}}` syntax (only works for webhook-provided data)

### Pattern 4: Multi-language Agent
**Bland**: Set `language` parameter (e.g., "ENG", "SPA")

**ElevenLabs**:
- Select language in agent settings
- Pick a voice that supports the target language
- System prompt should specify the language

---

## Transfer Mapping

| Bland Transfer Type | ElevenLabs Equivalent |
|--------------------|----------------------|
| `blind` | Blind Transfer (Phone Transfer Node) |
| `warm` | Conference Transfer |

### Important Differences
- Bland allows transfer mid-prompt with tools
- ElevenLabs Phone Transfer Nodes are terminal — no edges out
- For transfer + fallback, use `transfer_to_number` system tool instead

---

## Voice Mapping

Bland uses named voices (e.g., "maya", "josh"). ElevenLabs has a different voice library. There's no direct 1:1 mapping, but the migration tool will select a sensible default ElevenLabs voice.

If you need a specific voice quality, browse the ElevenLabs voice library after migration.

---

## Webhook/Tool Migration

### Bland Tool Format
```json
{
  "name": "check_order",
  "description": "Look up order status",
  "url": "https://api.example.com/orders/{{order_id}}",
  "method": "GET",
  "headers": {"Authorization": "Bearer xxx"}
}
```

### ElevenLabs Tool Format
- **Type**: Webhook
- **Name**: check_order
- **Description**: Look up order status
- **URL**: https://api.example.com/orders/{order_id}
- **Method**: GET
- **Headers**: Authorization: Bearer xxx
- **Parameters**: order_id (string, required)

**Key difference**: Bland uses `{{variable}}` template syntax in URLs/body. ElevenLabs defines parameters as a schema and the LLM fills them in.

---

## What Doesn't Migrate Automatically

1. **Phone numbers** — You'll need to set up new numbers in ElevenLabs
2. **Call history/logs** — Historical data stays in Bland
3. **Dynamic data URLs** — Recreate as webhook tools
4. **Encrypted keys** (Twilio integration) — Re-configure in ElevenLabs
5. **Pathway visual layout** — The workflow logic migrates but node positioning is auto-generated
6. **Voicemail detection** — Handle in ElevenLabs agent settings

---

## Migration Checklist

### Setup
- [ ] Created new agent in ElevenLabs
- [ ] Set system prompt (from Bland's `prompt`)
- [ ] Set first message (from Bland's `first_sentence`)
- [ ] Selected a voice

### Workflow
- [ ] Created workflow nodes matching Bland pathway (if applicable)
- [ ] Set up edge conditions for routing
- [ ] Configured Phone Transfer nodes or transfer tools
- [ ] Added End nodes

### Tools & Data
- [ ] Migrated custom tools → webhook tools
- [ ] Set up Data Collection fields (from analysis_schema)
- [ ] Configured webhooks for post-call data

### Testing
- [ ] Tested main conversation flow
- [ ] Tested transfer scenarios
- [ ] Tested tool invocations
- [ ] Tested edge cases and error handling
