# Conversational Voice Agents

Build and deploy AI voice agents with ElevenLabs Agents Platform and CLI.

## Architecture

The Agents Platform coordinates 4 core components:
1. **Speech-to-Text (ASR)**: Fine-tuned recognition
2. **Language Model**: Your choice of LLM (or custom)
3. **Text-to-Speech (TTS)**: Low-latency voice synthesis
4. **Turn-taking Model**: Proprietary conversation timing

## CLI Quick Start

### Installation
```bash
npm install -g @elevenlabs/cli
```

### Initialize & Authenticate
```bash
elevenlabs agents init
elevenlabs auth login
```

### Create Agent
```bash
# From template
elevenlabs agents add "Support Bot" --template customer-service

# From existing config
elevenlabs agents add --from-file my-agent.json
```

### Deploy
```bash
# Preview changes
elevenlabs agents push --dry-run

# Push to ElevenLabs
elevenlabs agents push
```

## CLI Command Reference

### Authentication
```bash
elevenlabs auth login              # Authenticate
elevenlabs auth whoami             # Check status
elevenlabs auth logout             # Log out
elevenlabs auth residency eu-residency  # Set EU data residency
```

### Agent Management
```bash
elevenlabs agents init             # Initialize project
elevenlabs agents add "Name" --template <type>
elevenlabs agents list             # List all agents
elevenlabs agents status           # Check sync status
elevenlabs agents push             # Sync to ElevenLabs
elevenlabs agents pull             # Import from ElevenLabs
elevenlabs agents delete <id>      # Delete agent
elevenlabs agents widget <id>      # Generate embed HTML
elevenlabs agents test <id>        # Run tests
```

### Tool Management
```bash
elevenlabs tools add-webhook "Name" --config-path ./tool.json
elevenlabs tools add-client "Name" --config-path ./tool.json
elevenlabs tools push
elevenlabs tools pull
elevenlabs tools delete <tool_id>
```

### Testing
```bash
elevenlabs tests add "Test Name" --template basic-llm
elevenlabs tests push
```

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

## Templates

| Template | Description | Temperature |
|----------|-------------|-------------|
| `customer-service` | Professional support | 0.1 |
| `assistant` | General purpose | 0.3 |
| `voice-only` | Voice interactions only | 0.3 |
| `text-only` | Text conversations only | 0.3 |
| `minimal` | Quick prototyping | 0.3 |
| `default` | All options | 0.3 |

## Agent Configuration Schema

### Minimal Config
```json
{
  "name": "My Agent",
  "conversation_config": {
    "agent": {
      "prompt": {
        "prompt": "You are a helpful assistant.",
        "llm": "gpt-4o-mini",
        "temperature": 0.3
      },
      "first_message": "Hi! How can I help?",
      "language": "en"
    },
    "tts": {
      "model_id": "eleven_turbo_v2",
      "voice_id": "pNInz6obpgDQGcFmaJgB"
    }
  }
}
```

### Full Config
```json
{
  "name": "Customer Support",
  "conversation_config": {
    "agent": {
      "prompt": {
        "prompt": "System prompt here...",
        "llm": "gpt-4o-mini",
        "temperature": 0.1,
        "knowledge_base": [
          {"type": "url", "name": "Docs", "id": "kb_123"}
        ]
      },
      "first_message": "Thanks for calling. How can I help?",
      "language": "en",
      "tools": []
    },
    "tts": {
      "model_id": "eleven_turbo_v2",
      "voice_id": "pNInz6obpgDQGcFmaJgB",
      "speed": 1.0
    },
    "asr": {
      "model": "nova-2-general",
      "language": "auto"
    },
    "conversation": {
      "max_duration_seconds": 1800,
      "text_only": false
    }
  },
  "platform_settings": {
    "widget": {
      "conversation_starters": ["Help with order", "Billing question"],
      "branding": {
        "primary_color": "#FFE01B"
      }
    }
  },
  "tags": ["production", "customer-service"]
}
```

## Supported LLMs

### Recommended
| Model | Best For | Latency |
|-------|----------|---------|
| `gpt-4o-mini` | General purpose | Low |
| `gpt-4o` | Complex tasks | Medium |
| `gemini-2.5-flash-lite` | High-frequency, simple | Ultra-low |
| `claude-sonnet-4` | Complex reasoning | Higher |

### All Supported
- **OpenAI**: gpt-5, gpt-5-mini, gpt-4.1, gpt-4o, gpt-4o-mini
- **Anthropic**: claude-sonnet-4.5, claude-sonnet-4, claude-haiku-4.5
- **Google**: gemini-2.5-flash, gemini-2.5-flash-lite
- **ElevenLabs Native**: glm-4.5-air, qwen3-30b-a3b

### Temperature Guide
| Range | Use Case |
|-------|----------|
| 0.0-0.3 | Customer service, transactional |
| 0.4-0.6 | Balanced conversations |
| 0.7-1.0 | Creative, varied responses |

## Tool Types

### Webhook Tools (Server-Side)
```json
{
  "name": "lookup_order",
  "description": "Look up order by ID",
  "type": "webhook",
  "method": "GET",
  "url": "https://api.example.com/orders/{order_id}",
  "path_params": [
    {
      "name": "order_id",
      "type": "string",
      "description": "Order ID (ORD-XXXXXXXX)",
      "required": true
    }
  ],
  "headers": {
    "Authorization": "Bearer ${API_KEY}"
  }
}
```

### Client Tools (Frontend)
```python
from elevenlabs.conversational_ai.conversation import ClientTools

def show_product(parameters):
    product_id = parameters.get("product_id")
    return {"action": "navigate", "url": f"/products/{product_id}"}

client_tools = ClientTools()
client_tools.register("showProduct", show_product)
```

### MCP Tools
```json
{
  "name": "Zapier Integration",
  "server_url": "https://mcp.zapier.com/sse",
  "approval_mode": "fine-grained"
}
```

### System Tools (Built-in)
- `transfer_to_number`: Transfer to phone number
- `agent_transfer`: Transfer to another agent
- `end_call`: Gracefully end conversation

## Knowledge Base

Add documents via API or dashboard:
```python
doc = elevenlabs.conversational_ai.knowledge_base.documents.create_from_url(
    url="https://example.com/docs",
    name="Product Documentation"
)

# Reference in agent config
"knowledge_base": [{"type": "url", "name": doc.name, "id": doc.id}]
```

Supported formats: epub, pdf, docx, txt, html

## Testing

### Scenario Tests (LLM Evaluation)
```json
{
  "name": "Empathy Test",
  "scenario": "User: I've been charged twice!",
  "success_criteria": [
    "Agent acknowledges frustration",
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
    "phone_number": {"validation": "exact", "value": "+18001234567"}
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

Visual orchestration for multi-agent systems:

### Node Types
- **Subagent**: Override prompts, LLM, voice for phases
- **Dispatch Tool**: Guaranteed execution with routing
- **Agent Transfer**: Hand off to different agent
- **Transfer to Number**: Escalate to human
- **End**: Terminate gracefully

### Edge Types
- **LLM Condition**: Natural language routing
- **Expression**: Programmatic conditions
- **None**: Default path

## Telephony Integration

### Twilio
Import phone numbers via dashboard, manage via CLI.

### Batch Calling
```csv
phone_number,user_name,order_id
+15551234567,John Smith,ORD-12345
```

### SIP Trunking
Connect existing PBX infrastructure.

## Embedding

### Widget (Quick)
```html
<elevenlabs-convai agent-id="your-agent-id"></elevenlabs-convai>
<script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async></script>
```

### React SDK
```jsx
import { useConversation } from '@elevenlabs/react';

const conversation = useConversation({
  clientTools: { /* ... */ },
  overrides: { agent: { firstMessage: "Hello!" } }
});

await conversation.startSession({
  agentId: 'id',
  connectionType: 'webrtc'
});
```

### Python SDK
```python
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation

conversation = Conversation(
    client,
    agent_id,
    audio_interface=DefaultAudioInterface()
)
conversation.start_session()
```

## MCP Tools for Agents

```
mcp__ElevenLabs__create_agent
- name: "My Agent"
- first_message: "Hi! How can I help?"
- system_prompt: "You are a helpful assistant."
- voice_id: "cgSgspJ2msm6clMCkdW9"
- llm: "gemini-2.0-flash-001"
- temperature: 0.5

mcp__ElevenLabs__list_agents
mcp__ElevenLabs__get_agent
- agent_id: "agent_123"

mcp__ElevenLabs__add_knowledge_base_to_agent
- agent_id: "agent_123"
- knowledge_base_name: "Product Docs"
- url: "https://docs.example.com"

mcp__ElevenLabs__make_outbound_call
- agent_id: "agent_123"
- agent_phone_number_id: "phone_456"
- to_number: "+15551234567"

mcp__ElevenLabs__list_conversations
- agent_id: "agent_123"

mcp__ElevenLabs__get_conversation
- conversation_id: "conv_789"
```

## Best Practices

1. **Prompting**: Use clear markdown sections (# Personality, # Guardrails, # Tools)
2. **Temperature**: Keep low (0.1-0.3) for customer service
3. **Error Handling**: Define tool failure procedures explicitly
4. **Testing**: Create scenario tests for edge cases
5. **Monitoring**: Track conversations with analytics dashboard
