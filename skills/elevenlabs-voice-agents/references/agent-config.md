# Agent Configuration Reference

Complete schema for ElevenLabs agent configuration files.

## Full Configuration Schema

```json
{
  "name": "Agent Name",
  "conversation_config": {
    "agent": {
      "prompt": {
        "prompt": "System prompt with markdown sections...",
        "llm": "gpt-4o-mini",
        "temperature": 0.1,
        "knowledge_base": [
          {
            "type": "url|file|text",
            "name": "Document Name",
            "id": "kb_document_id"
          }
        ]
      },
      "first_message": "Hi! How can I help you today?",
      "language": "en",
      "tools": []
    },
    "tts": {
      "model_id": "eleven_turbo_v2",
      "voice_id": "pNInz6obpgDQGcFmaJgB",
      "speed": 1.0,
      "audio_format": {
        "format": "pcm",
        "sample_rate": 44100
      }
    },
    "asr": {
      "model": "nova-2-general",
      "language": "auto"
    },
    "conversation": {
      "max_duration_seconds": 1800,
      "text_only": false,
      "client_events": ["user_transcript", "agent_response"]
    }
  },
  "platform_settings": {
    "widget": {
      "conversation_starters": [
        "I need help with my order",
        "Billing question",
        "Technical support"
      ],
      "branding": {
        "primary_color": "#FFE01B",
        "logo_url": "https://example.com/logo.png"
      }
    },
    "authentication": {
      "required": false
    }
  },
  "tags": ["production", "customer-service"]
}
```

## Field Reference

### Agent Configuration

| Field | Type | Description |
|-------|------|-------------|
| `prompt.prompt` | string | System prompt (markdown recommended) |
| `prompt.llm` | string | LLM model identifier |
| `prompt.temperature` | float | 0.0-1.0, lower = more deterministic |
| `prompt.knowledge_base` | array | Attached knowledge documents |
| `first_message` | string | Agent's opening line |
| `language` | string | ISO code: en, es, fr, de, etc. |
| `tools` | array | Tool configurations |

### TTS Configuration

| Field | Type | Description |
|-------|------|-------------|
| `model_id` | string | `eleven_turbo_v2`, `eleven_multilingual_v2` |
| `voice_id` | string | Voice ID from voice library |
| `speed` | float | 0.7-1.2, speaking rate multiplier |

### ASR Configuration

| Field | Type | Description |
|-------|------|-------------|
| `model` | string | `nova-2-general` (default) |
| `language` | string | `auto` for detection, or ISO code |

### Conversation Settings

| Field | Type | Description |
|-------|------|-------------|
| `max_duration_seconds` | int | Max call length (1800 = 30 min) |
| `text_only` | bool | Disable voice, text chat only |
| `client_events` | array | Events to emit to client |

## Supported LLMs

### ElevenLabs Native
- `glm-4.5-air` - Cost-effective, low latency
- `qwen3-30b-a3b`
- `gpt-oss-120b`

### OpenAI
- `gpt-5`, `gpt-5-mini`, `gpt-5-nano`
- `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`
- `gpt-4o`, `gpt-4o-mini` ← **Recommended starting point**
- `gpt-4-turbo`, `gpt-3.5-turbo`

### Anthropic
- `claude-sonnet-4.5`, `claude-sonnet-4` ← **Best for complex reasoning**
- `claude-haiku-4.5`
- `claude-3.7-sonnet`, `claude-3.5-sonnet`, `claude-3-haiku`

### Google
- `gemini-2.5-flash`, `gemini-2.5-flash-lite` ← **Lowest latency**
- `gemini-2.0-flash`, `gemini-2.0-flash-lite`

## Tool Configuration

### Webhook Tool Schema
```json
{
  "name": "tool_name",
  "description": "Clear description of when to use this tool",
  "type": "webhook",
  "method": "GET|POST|PUT|DELETE",
  "url": "https://api.example.com/endpoint/{path_param}",
  "headers": {
    "Authorization": "Bearer ${API_KEY_SECRET}"
  },
  "path_params": [
    {
      "name": "path_param",
      "type": "string",
      "description": "Parameter description with format example",
      "required": true
    }
  ],
  "query_params": [
    {
      "name": "query_param",
      "type": "string",
      "description": "Optional query parameter",
      "required": false
    }
  ],
  "body_params": [
    {
      "name": "body_field",
      "type": "string|number|boolean|object",
      "description": "Request body field",
      "required": true
    }
  ]
}
```

### Client Tool Schema
```json
{
  "name": "client_tool_name",
  "description": "Trigger client-side action",
  "type": "client",
  "parameters": [
    {
      "name": "param_name",
      "type": "string",
      "description": "Parameter description",
      "required": true
    }
  ],
  "wait_for_response": true
}
```

### System Tools (Built-in)
- `transfer_to_number` - Transfer to phone number
- `agent_transfer` - Transfer to another agent
- `end_call` - Gracefully end conversation

## Popular Voice IDs

| Voice | ID | Style |
|-------|-----|-------|
| Rachel | `21m00Tcm4TlvDq8ikWAM` | Neutral, professional |
| Adam | `pNInz6obpgDQGcFmaJgB` | Deep, warm |
| Antoni | `ErXwobaYiN019PkySvjV` | Young, energetic |
| Bella | `EXAVITQu4vr4xnSDxMaL` | Soft, gentle |
| Domi | `AZnzlk1XvdvUeBnXmlld` | Strong, confident |
| Elli | `MF3mGyEYCl7XYWbV9V6O` | Young, clear |

Browse full library: [elevenlabs.io/voice-library](https://elevenlabs.io/voice-library)

## Example Configurations

### Customer Service Agent
```json
{
  "name": "Customer Support",
  "conversation_config": {
    "agent": {
      "prompt": {
        "prompt": "# Personality\nYou are a friendly, professional customer service representative for Acme Corp.\n\n# Goal\n1. Verify customer identity using email\n2. Look up order with `getOrderStatus` tool\n3. Resolve issue or escalate if needed\n\n# Guardrails\nNever share customer data without verification. This step is important.\nNever process refunds over $500 without supervisor approval.\nIf customer becomes abusive, offer supervisor escalation.\n\n# Tools\n## getOrderStatus\nUse when customer asks about their order. Always call before providing order info.\n\n# Character Normalization\nEmail: \"at\" → \"@\", \"dot\" → \".\"\n\n# Error Handling\nIf tool fails: \"I'm having trouble accessing that. Let me try again.\"",
        "llm": "gpt-4o-mini",
        "temperature": 0.1
      },
      "first_message": "Thank you for calling Acme Support. My name is Alex. How can I help you today?",
      "language": "en",
      "tools": [
        {
          "name": "getOrderStatus",
          "type": "webhook",
          "method": "GET",
          "url": "https://api.acme.com/orders/{order_id}",
          "description": "Look up order status by order ID"
        }
      ]
    },
    "tts": {
      "model_id": "eleven_turbo_v2",
      "voice_id": "pNInz6obpgDQGcFmaJgB"
    },
    "conversation": {
      "max_duration_seconds": 1800
    }
  },
  "tags": ["customer-service", "production"]
}
```

### Technical Support Agent
```json
{
  "name": "Tech Support",
  "conversation_config": {
    "agent": {
      "prompt": {
        "prompt": "# Personality\nYou are a patient, methodical technical support specialist.\n\n# Goal\n1. Verify customer identity\n2. Identify affected service and severity\n3. Run diagnostics with `runDiagnostic` tool\n4. Provide step-by-step resolution or escalate\n\n# Guardrails\nAlways run diagnostics before suggesting solutions. This step is important.\nNever guess—base recommendations on diagnostic results.\nEscalate to engineering if issue persists after 2 attempts.\n\n# Error Handling\nIf diagnostic fails after 2 retries, escalate: \"Let me connect you with our engineering team.\"",
        "llm": "claude-sonnet-4",
        "temperature": 0.2
      },
      "first_message": "Hi, this is tech support. What issue are you experiencing?",
      "language": "en"
    },
    "tts": {
      "model_id": "eleven_turbo_v2",
      "voice_id": "ErXwobaYiN019PkySvjV"
    }
  }
}
```

### Appointment Scheduler
```json
{
  "name": "Appointment Scheduler",
  "conversation_config": {
    "agent": {
      "prompt": {
        "prompt": "# Personality\nYou are an efficient, friendly appointment scheduler.\n\n# Goal\n1. Collect customer name and phone number\n2. Understand appointment type needed\n3. Check availability with `checkAvailability` tool\n4. Book appointment with `scheduleAppointment` tool\n5. Confirm details and send reminder\n\n# Guardrails\nAlways confirm date/time before booking.\nNever double-book time slots.\n\n# Character Normalization\nPhone: Collect as spoken, convert to +1XXXXXXXXXX format\nDates: Confirm day of week with date",
        "llm": "gpt-4o-mini",
        "temperature": 0.1
      },
      "first_message": "Hi! I can help you schedule an appointment. What type of appointment do you need?",
      "language": "en"
    },
    "tts": {
      "model_id": "eleven_turbo_v2",
      "voice_id": "MF3mGyEYCl7XYWbV9V6O"
    }
  }
}
```
