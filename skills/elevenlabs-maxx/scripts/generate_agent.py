#!/usr/bin/env python3
"""
Generate ElevenLabs agent configuration files.

Usage:
    python generate_agent.py <name> [--template <template>] [--output <path>]

Templates: customer-service, assistant, voice-only, text-only, minimal
"""

import json
import argparse
import re
from pathlib import Path

TEMPLATES = {
    "minimal": {
        "name": "{name}",
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": "You are a helpful assistant.",
                    "llm": "gpt-4o-mini",
                    "temperature": 0.3
                },
                "first_message": "Hi! How can I help you today?",
                "language": "en"
            },
            "tts": {
                "model_id": "eleven_turbo_v2",
                "voice_id": "pNInz6obpgDQGcFmaJgB"
            }
        }
    },
    "customer-service": {
        "name": "{name}",
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": """# Personality

You are a friendly, professional customer service representative.

# Goal

1. Greet customer warmly
2. Understand their issue
3. Resolve or escalate appropriately

# Guardrails

Never share customer data without verification.
Always confirm actions before taking them.
If unsure, offer to escalate to a supervisor.

# Tone

Keep responses concise (2-3 sentences).
Be empathetic and patient.
Confirm understanding before acting.""",
                    "llm": "gpt-4o-mini",
                    "temperature": 0.1
                },
                "first_message": "Thank you for calling. My name is Alex. How can I help you today?",
                "language": "en"
            },
            "tts": {
                "model_id": "eleven_turbo_v2",
                "voice_id": "pNInz6obpgDQGcFmaJgB"
            },
            "conversation": {
                "max_duration_seconds": 1800
            }
        },
        "tags": ["customer-service"]
    },
    "assistant": {
        "name": "{name}",
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": """# Personality

You are a helpful, knowledgeable AI assistant.

# Goal

Answer questions accurately and helpfully.
Provide clear explanations.
Admit when you don't know something.

# Tone

Conversational but professional.
Adapt complexity to user's level.
Be concise unless detail is requested.""",
                    "llm": "gpt-4o-mini",
                    "temperature": 0.3
                },
                "first_message": "Hello! I'm your AI assistant. What can I help you with?",
                "language": "en"
            },
            "tts": {
                "model_id": "eleven_turbo_v2",
                "voice_id": "pNInz6obpgDQGcFmaJgB"
            }
        },
        "tags": ["assistant"]
    },
    "voice-only": {
        "name": "{name}",
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": "You are a voice assistant. Keep responses brief and conversational.",
                    "llm": "gpt-4o-mini",
                    "temperature": 0.3
                },
                "first_message": "Hi there! How can I help?",
                "language": "en"
            },
            "tts": {
                "model_id": "eleven_turbo_v2",
                "voice_id": "pNInz6obpgDQGcFmaJgB"
            },
            "conversation": {
                "text_only": False
            }
        }
    },
    "text-only": {
        "name": "{name}",
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": "You are a text-based assistant. Provide helpful, well-formatted responses.",
                    "llm": "gpt-4o-mini",
                    "temperature": 0.3
                },
                "first_message": "Hello! How can I assist you today?",
                "language": "en"
            },
            "tts": {
                "model_id": "eleven_turbo_v2",
                "voice_id": "pNInz6obpgDQGcFmaJgB"
            },
            "conversation": {
                "text_only": True
            }
        }
    }
}

def slugify(name: str) -> str:
    """Convert name to filename-safe slug."""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '_', slug)
    slug = slug.strip('_')
    return slug

def generate_config(name: str, template: str = "minimal") -> dict:
    """Generate agent configuration from template."""
    if template not in TEMPLATES:
        raise ValueError(f"Unknown template: {template}. Available: {', '.join(TEMPLATES.keys())}")
    
    config = json.loads(json.dumps(TEMPLATES[template]))  # Deep copy
    
    # Replace {name} placeholder
    def replace_name(obj):
        if isinstance(obj, dict):
            return {k: replace_name(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_name(item) for item in obj]
        elif isinstance(obj, str):
            return obj.replace("{name}", name)
        return obj
    
    return replace_name(config)

def main():
    parser = argparse.ArgumentParser(description="Generate ElevenLabs agent configuration")
    parser.add_argument("name", help="Agent name")
    parser.add_argument("--template", "-t", default="minimal", 
                       choices=list(TEMPLATES.keys()),
                       help="Template to use")
    parser.add_argument("--output", "-o", help="Output file path (default: agent_configs/<slug>.json)")
    parser.add_argument("--print", "-p", action="store_true", help="Print to stdout instead of file")
    
    args = parser.parse_args()
    
    config = generate_config(args.name, args.template)
    config_json = json.dumps(config, indent=2)
    
    if args.print:
        print(config_json)
    else:
        if args.output:
            output_path = Path(args.output)
        else:
            output_dir = Path("agent_configs")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{slugify(args.name)}.json"
        
        output_path.write_text(config_json)
        print(f"✅ Created agent config: {output_path}")

if __name__ == "__main__":
    main()
