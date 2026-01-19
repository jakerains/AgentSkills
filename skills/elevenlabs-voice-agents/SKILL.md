---
name: elevenlabs-voice-agents
description: "Create and deploy ElevenLabs conversational voice agents using the CLI and API. Use when user wants to build voice agents, phone bots, customer service agents, voice assistants, or conversational AI that speaks. Triggers include requests to create voice agents, build phone systems, deploy conversational AI, create talking assistants, set up voice bots, or work with ElevenLabs agents platform. Supports full agent configuration, tools (webhook/client/MCP), knowledge bases, testing, workflows, and telephony integration."
---

# ElevenLabs Voice Agent Creation

Build and deploy conversational voice agents using the ElevenLabs CLI ("Agents as Code").

## Quick Start

```bash
# Install CLI
npm install -g @elevenlabs/cli

# Initialize project
elevenlabs agents init

# Authenticate
elevenlabs auth login

# Create agent from template
elevenlabs agents add "My Agent" --template customer-service

# Push to ElevenLabs
elevenlabs agents push
```

## CLI Command Reference

### Authentication
```bash
elevenlabs auth login              # Authenticate with API key
elevenlabs auth whoami             # Check login status
elevenlabs auth logout             # Log out
elevenlabs auth residency eu-residency  # Set EU data residency
```

### Agent Management
```bash
elevenlabs agents init             # Initialize project structure
elevenlabs agents add "Name" --template <type>  # Create from template
elevenlabs agents add --from-file config.json   # Create from JSON config
elevenlabs agents list             # List all agents
elevenlabs agents status           # Check sync status
elevenlabs agents push             # Sync local → ElevenLabs
elevenlabs agents push --dry-run   # Preview changes
elevenlabs agents pull             # Import from ElevenLabs → local
elevenlabs agents delete <id>      # Delete agent
elevenlabs agents widget <id>      # Generate embed HTML
elevenlabs agents test <id>        # Run tests
```

### Tools
```bash
elevenlabs tools add-webhook "Name" --config-path ./tool.json
elevenlabs tools add-client "Name" --config-path ./tool.json
elevenlabs tools push
elevenlabs tools pull
```

### Available Templates
| Template | Use Case |
|----------|----------|
| `customer-service` | Professional support, low temp (0.1), 30-min sessions |
| `assistant` | General purpose, balanced creativity (0.3) |
| `voice-only` | Voice interactions only, no text |
| `text-only` | Text conversations only |
| `minimal` | Essential fields for quick prototyping |
| `default` | Complete config with all options |

## Project Structure

```
your_project/
├── agents.json          # Agent registry
├── tools.json           # Tool definitions
├── tests.json           # Test configs
├── agent_configs/       # Agent JSON configs
├── tool_configs/        # Tool JSON configs
└── test_configs/        # Test configs
```

## Agent Configuration Schema

See [references/agent-config.md](references/agent-config.md) for the complete configuration schema with all fields and options.

### Minimal Config Example
```json
{
  "name": "Support Agent",
  "conversation_config": {
    "agent": {
      "prompt": {
        "prompt": "You are a helpful customer service representative.",
        "llm": "gpt-4o-mini",
        "temperature": 0.1
      },
      "first_message": "Hi! How can I help you today?",
      "language": "en"
    },
    "tts": {
      "model_id": "eleven_turbo_v2",
      "voice_id": "pNInz6obpgDQGcFmaJgB"
    }
  }
}
```

## System Prompt Best Practices

Structure prompts with clear markdown sections:

```markdown
# Personality
[Role and tone description]

# Goal
[Primary objectives - numbered steps]

# Guardrails
[Non-negotiable rules - never/always statements]

# Tools
[When and how to use each tool]

# Character Normalization
[Email: "at" → "@", "dot" → "."]
[IDs: spoken vs written formats]

# Error Handling
[Recovery procedures for tool failures]
```

**Key principles:**
- Separate instructions into clean sections with markdown headings
- Be concise - challenge each piece of information
- Emphasize critical steps: "This step is important."
- Use `# Guardrails` section (models pay extra attention to this heading)
- Include character normalization for emails, IDs, phone numbers
- Define explicit error handling for every tool

## Tools

### Webhook Tools (Server-Side API Calls)
```json
{
  "name": "lookup_order",
  "description": "Look up order status by order ID",
  "type": "webhook",
  "method": "GET",
  "url": "https://api.example.com/orders/{order_id}",
  "path_params": [
    {
      "name": "order_id",
      "type": "string",
      "description": "Order ID format: ORD-XXXXXXXX",
      "required": true
    }
  ]
}
```

### Client Tools (Frontend Events)
Register in code - agent triggers, client executes:
```python
from elevenlabs.conversational_ai.conversation import ClientTools

def show_product(parameters):
    product_id = parameters.get("product_id")
    return {"action": "navigate", "url": f"/products/{product_id}"}

client_tools = ClientTools()
client_tools.register("showProduct", show_product)
```

### MCP Tools (Model Context Protocol)
Connect to external MCP servers (Zapier, custom integrations):
```json
{
  "name": "Zapier Integration",
  "server_url": "https://mcp.zapier.com/sse",
  "approval_mode": "fine-grained"
}
```

## LLM Selection

| Model | Best For | Latency | Tool Calling |
|-------|----------|---------|--------------|
| GPT-4o / GPT-4o-mini | General purpose, balanced | Low-Med | Excellent |
| Gemini 2.5 Flash Lite | High-frequency, simple tasks | Ultra-low | Good |
| Claude Sonnet 4/4.5 | Complex reasoning, multi-step | Higher | Excellent |
| GLM-4.5-Air | Cost-effective general use | Low | Good |

**Temperature guide:**
- 0.0-0.3: Deterministic, consistent (customer service)
- 0.4-0.7: Balanced creativity
- 0.8-1.0: Creative, varied (dynamic conversations)

## Voice Configuration

```json
"tts": {
  "model_id": "eleven_turbo_v2",
  "voice_id": "pNInz6obpgDQGcFmaJgB",
  "speed": 1.0
}
```

- Browse voices at [elevenlabs.io/voice-library](https://elevenlabs.io/voice-library)
- Speed range: 0.7x to 1.2x
- Enable expressive mode for [laughs], [whispers], [slow] tags

## Knowledge Base

Add domain-specific information via API or dashboard:
```python
# Create from URL
doc = elevenlabs.conversational_ai.knowledge_base.documents.create_from_url(
    url="https://example.com/docs",
    name="Product Documentation"
)

# Reference in agent config
"knowledge_base": [{"type": "url", "name": doc.name, "id": doc.id}]
```

## Testing

### Scenario Tests (LLM Evaluation)
```json
{
  "name": "Empathy Test",
  "scenario": "User: I've been charged twice and I'm frustrated!",
  "success_criteria": [
    "Agent acknowledges frustration with empathy",
    "Agent offers to investigate",
    "Agent maintains professional tone"
  ]
}
```

### Tool Call Tests (Deterministic)
```json
{
  "expected_tool": "transfer_to_number",
  "expected_params": {
    "phone_number": { "validation": "exact", "value": "+18001234567" }
  }
}
```

### CI/CD Integration
```yaml
- name: Deploy Agents
  run: |
    npm install -g @elevenlabs/cli
    elevenlabs agents test ${{ secrets.AGENT_ID }}
    elevenlabs agents push
  env:
    ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
```

## Agent Workflows

Visual orchestration for complex multi-agent systems:

**Node Types:**
- **Subagent**: Override prompts, LLM, voice, tools for specific phases
- **Dispatch Tool**: Guaranteed tool execution with success/failure routing
- **Agent Transfer**: Hand off to different agent
- **Transfer to Number**: Escalate to human via phone
- **End**: Gracefully terminate

**Edge Types:**
- **LLM Condition**: Natural language routing ("if user mentions refund...")
- **Expression**: Programmatic conditions
- **None**: Default path

## Telephony

### Twilio Integration
Import phone numbers via dashboard, manage via CLI.

### Batch Calling (Outbound)
Upload CSV with `phone_number` column + dynamic variables:
```csv
phone_number,user_name,order_id
+15551234567,John Smith,ORD-12345
```

### SIP Trunking
Connect existing PBX infrastructure directly.

## Embedding

### Widget (Quick)
```html
<elevenlabs-convai agent-id="your-agent-id"></elevenlabs-convai>
<script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async></script>
```

### React SDK (Custom)
```jsx
import { useConversation } from '@elevenlabs/react';

const conversation = useConversation({
  clientTools: { /* ... */ },
  overrides: { agent: { firstMessage: "Hello!" } }
});

await conversation.startSession({ agentId: 'id', connectionType: 'webrtc' });
```

### Python SDK
```python
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation

conversation = Conversation(client, agent_id, audio_interface=DefaultAudioInterface())
conversation.start_session()
```

## Workflow: Build Complete Agent

1. **Initialize**: `elevenlabs agents init && elevenlabs auth login`
2. **Create config**: Generate JSON in `agent_configs/` (use template or custom)
3. **Write system prompt**: Follow prompting best practices above
4. **Add tools**: Create tool configs in `tool_configs/`
5. **Add knowledge**: Upload docs via API or dashboard
6. **Push**: `elevenlabs agents push`
7. **Test**: `elevenlabs agents test <id>`
8. **Embed**: Generate widget or use SDK

## Common Patterns

### Customer Service Agent
- Template: `customer-service`
- Temperature: 0.1 (consistent)
- Tools: order lookup, refund processing, transfer to human
- Guardrails: verify identity, escalate over $500

### Voice Assistant
- Template: `assistant`
- Temperature: 0.3 (balanced)
- First message: proactive greeting
- Multi-language: auto language detection

### Phone Bot (IVR Replacement)
- Telephony: Twilio/SIP integration
- Workflow: intake → route to specialist subagents
- Transfer: escalate to human when needed
