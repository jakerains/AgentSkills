---
name: elevenlabs-agent-builder
description: Build, validate, and deploy ElevenLabs Conversational AI voice agents from any source material. Use whenever someone wants to create a voice agent, phone bot, IVR agent, or conversational AI on ElevenLabs. Also use when migrating from Retell, Vapi, Bland, or other voice platforms. Triggers on ElevenLabs agent JSON, voice agent architecture, agent deployment, agent validation, knowledge base prep for voice agents, fixing agent errors, or building phone/web voice bots. Even casual mentions like 'build me a phone bot' or 'convert this Retell agent' should trigger this skill.
---

# ElevenLabs Conversational AI Agent Builder

Build production-ready ElevenLabs voice agents from any source: natural language descriptions, call scripts, SOPs, documentation, competitor configs (Retell/Vapi/Bland), or existing ElevenLabs agents.

## Skill Structure

```
elevenlabs-agent-builder/
├── SKILL.md                           ← You are here (workflow + routing)
├── scripts/
│   ├── validate_el_json.py            ← Pre-deployment structural validator
│   ├── deploy_with_tools.py           ← Deploy agent + tools + KB + tests
│   ├── deploy_kb.py                   ← Upload knowledge base articles
│   └── update_agent.py                ← PATCH an existing agent
└── references/
    ├── reference.md                   ← Schema bible: JSON structure, nodes, edges, tools, RAG, V3
    ├── architecture_framework.md      ← 5-phase pipeline, split-point assessment, model selection
    ├── edge_failures.md               ← Why edges fail (mechanical + config + platform pitfalls)
    ├── pipeline.md                    ← Single-pass analyze + generate prompt
    ├── correct_prompt.md              ← Fix validation/deployment errors (E-codes + B-codes)
    ├── prepare_kb.md                  ← Knowledge base article design for RAG
    ├── cheatsheet_retell.md           ← Retell → ElevenLabs migration mapping
    ├── cheatsheet_vapi.md             ← Vapi → ElevenLabs migration mapping
    └── cheatsheet_bland.md            ← Bland → ElevenLabs migration mapping
```

## When to Read Which Reference

**ALWAYS read before generating any agent JSON:**
- `references/reference.md` — the schema bible. Every constraint, node type, edge type, tool format, and the complete payload structure lives here.

**Read based on task:**

| Task | Read These |
|------|-----------|
| Building any agent | `reference.md` + `architecture_framework.md` |
| Complex agent (5+ tools, routing forks, high-risk tools) | Above + `edge_failures.md` |
| Migrating from Retell | Above + `cheatsheet_retell.md` |
| Migrating from Vapi | Above + `cheatsheet_vapi.md` |
| Migrating from Bland | Above + `cheatsheet_bland.md` |
| Fixing agent errors | `correct_prompt.md` + `reference.md` (Common Errors section) |
| Preparing a knowledge base | `prepare_kb.md` + `reference.md` (Knowledge Base section) |
| Quick single-pass generation | `pipeline.md` (self-contained analyze+generate) |

---

## Core Workflow

### Step 1 — Read + Classify

When the user provides source material:

1. **Identify input type:**
   - Competitor JSON — look for `states[]`, `nodes[]`, `assistant`, `pathway`, `conversation_config`
   - SOP / documentation — step-by-step procedures, decision trees
   - Natural language — paragraphs describing what the agent should do
   - Transcripts — call recordings to pattern-extract from
   - Existing ElevenLabs agent — refinement or modification

2. **Read the ENTIRE source material.** Do not skim.

3. **Read the appropriate reference files** from the routing table above.

4. **Apply the PREPARE phase** (details in `architecture_framework.md`):
   - Competitor: flatten prompts, extract tools with schemas, distill duplicates, strip platform transition mechanics
   - SOP/docs: extract procedures, expand gaps (what fields? what if verification fails? error paths?)
   - Natural language: clarify with targeted questions — max 2-3 at a time
   - Transcripts: pattern-extract recurring phases, formalize into instructions + tool defs

5. **Determine complexity:**

| Simple | Complex |
|--------|---------|
| Fewer than 5 tools | 5+ tools |
| Under 1500 words combined instructions | Over 1500 words |
| No data-driven routing forks | Data-driven routing forks |
| Linear flow | Multiple branches |
| Low-risk tools only | High-risk tools (booking, cancellation, payment) |

### Step 2a — Simple Path (one-pass)

For simple agents:

1. Present brief inline summary: "Building a [purpose] agent. [N] tools. [Single node / N nodes]. [LLM model]. [TTS model]."
2. Generate ElevenLabs agent JSON (same response or next). If ambiguities exist, ask the user (max 2-3 questions) then generate.
3. Validate → output.

### Step 2b — Complex Path (one-stop)

For complex agents:

1. **Present full analysis:**
   - Agent purpose and communication mode (telephony-Twilio, telephony-SIP, web widget)
   - Tools identified — names, types, schemas if known
   - Key business rules and flow requirements
   - Split-point assessment — for each candidate: routing type (DATA/JUDGMENT/SCOPING), wrong-routing cost (L/M/H), failed-transition cost (L/M/H), decision (SPLIT/DON'T SPLIT)
   - Proposed architecture — node map, tools per node
   - LLM + TTS model recommendation with rationale
   - Questions / ambiguities needing user input

2. Say: "Review the proposed architecture. Type 'continue' to generate, or adjust anything."

3. **STOP AND WAIT** for user response.

4. After confirmation: generate ElevenLabs agent JSON.

5. Validate → output.

### Step 3 — Generate

Before writing any JSON, read `references/reference.md` for the full payload structure and constraints. Read `references/architecture_framework.md` for model selection and telephony patterns.

**Generation checklist:**

1. Map phases to nodes — only create node boundaries where assessment said SPLIT; merge everything else into single override_agent nodes with labeled internal phases
2. Write root prompt — personality, tone, guardrails ONLY. No flow descriptions.
3. Write node prompts — `# Goal`, `# Instructions`, `# Tools`, `# Boundaries`, `# Exit`
4. Create edges — ONE edge per node pair (see Duplicate Edge Prevention below)
5. Scope tools — `tool_ids: []` at root, `additional_tool_ids` per node
6. Add boundary instructions — every node says what it should NOT do
7. Tighten edge conditions — reference tool results + verbal confirmations
8. Include system tools — always `end_call`; add others as needed
9. Set first_message — match communication mode
10. Select models — LLM + TTS per architecture_framework.md guidance
11. Design knowledge base if applicable — see `references/prepare_kb.md`
12. Add post-call analysis — data collection (5-15 fields) + evaluation criteria (3-5)
13. Set dynamic variable defaults — ALL must have defaults or upload fails

#### ⚠️ The #1 Deployment Error: Duplicate Edges

You can ONLY have ONE edge between any two nodes. Forward AND backward directions go on the SAME edge object.

```json
// WRONG — TWO edges between same nodes = "Duplicate edge found" error
"edge-router-to-handler": {"source": "router", "target": "handler", ...}
"edge-handler-to-router": {"source": "handler", "target": "router", ...}

// CORRECT — ONE edge with both directions
"edge-router-handler": {
  "source": "router",
  "target": "handler",
  "forward_condition": {"type": "llm", "label": "...", "condition": "..."},
  "backward_condition": {"type": "llm", "label": "...", "condition": "..."}
}
```

**Pre-generation:** List ALL unique node pairs needing connections. For each: one-way or bidirectional? Create exactly ONE edge per pair. Report: "Analyzed X unique node pairs, Y require bidirectional edges."

**Post-generation:** Scan all edges. If any two have swapped source/target → DUPLICATE. Merge into one with backward_condition. Report: "Duplicate edge check: Scanned X edges. No duplicates." or fix if found.

#### Other Critical Constraints

- `tool_ids: []` at root; use `additional_tool_ids` per node (tools accumulate — can't remove base tools)
- Edge conditions must reference tool results and verbal confirmations, not vague states
- No self-loops (put looping behavior in prompts)
- Terminal nodes (phone_number, end) cannot have outgoing edges
- backward_condition must be LLM type — NEVER unconditional (infinite loop)
- Start node key must be `"start_node"`
- Transfer types: only `"blind"`, `"conference"`, or `"sip_refer"`
- Webhook URLs must be static — no `{{variable}}` in paths
- Turn mode: only `"turn"` or `"silence"` (never `"conversational"`)

#### Edge Condition Quality

| Good (observable + concrete) | Bad (vague + speculatable) |
|------------------------------|---------------------------|
| "'client_lookup' tool returned a matching record" | "Customer is identified" |
| "Caller confirmed name AND 'generate_auth_token' returned success" | "Authentication complete" |
| "'book_appointment' returned a confirmation with booking ID" | "Appointment booked" |

### Step 4 — Validate

Run the structural validator:

```bash
python scripts/validate_el_json.py agents/{agent_name}_EL.json
```

Fix any errors and re-validate until `Status: PASSED`. Only output after clean validation.

Common error fixes are cataloged in `references/correct_prompt.md`:
- E001 (self-loop): Remove edge, add looping to node prompt
- E002 (duplicate edges): Merge into single edge with combined condition
- E003 (unconditional backward): Change to LLM type
- E005 (invalid transfer_type): Use "conference" or "blind"
- E006 (URL placeholders): Static URL + move variables to request body

### Step 5 — Output

Save to `agents/{agent_name}_EL.json`. Provide deployment instructions:

```bash
# Deploy agent with tools
python scripts/deploy_with_tools.py agents/{agent_name}_EL.json

# Deploy with knowledge base
python scripts/deploy_with_tools.py agents/{agent_name}_EL.json \
  --kb-manifest knowledge-base/kb_manifest.json

# Update existing agent
python scripts/update_agent.py <agent_id> agents/{agent_name}_EL.json
```

---

## Test Mode

When user requests "test mode": generate a testable version without working backends.

1. Remove all `type: "webhook"` tools
2. Keep system tools (`end_call`, `transfer_to_number`)
3. Replace `{{variables}}` with hardcoded test values; remove `dynamic_variables`
4. **CRITICAL:** Do NOT do naive find-and-replace on conditional prompts. Pre-resolve conditions and rewrite as direct instructions. See `references/pipeline.md` "Test Mode" section.
5. Add fake data covering all tool response scenarios (found/not-found/multiple/error)
6. Preserve flow structure: same nodes, same edges, same conditions

Save as `agents/{agent_name}_EL_testmode.json`.

---

## V3 Mode (Expression Tags)

When user requests "v3" or "v3 mode": generate a personality-driven agent with expression tags.

1. Analyze character/energy/speech style from source material
2. Present summary: character, energy level, speech style, functional requirements
3. **STOP AND WAIT** for user confirmation
4. Generate V3 persona prompt with sections: identity, personality, speech patterns, expression tags, rewrite examples, signature style, avoid list, conversation style, technical notes, identity response
5. Generate JSON with V3 TTS config: `eleven_v3_conversational`, `expressive_mode: true`, 8-12 `suggested_audio_tags`

Full V3 reference (tag categories, energy profiles, TTS rules): `references/reference.md` "V3 Mode" section.

---

## Knowledge Base Preparation

When source material includes large reference content that would bloat the prompt:

1. Read `references/prepare_kb.md` for article design rules
2. Read `references/reference.md` "Knowledge Base (RAG)" section for RAG internals
3. Design articles: question-style H1 headings, 1.5-3 KB per article, self-contained, no YAML front matter, no cross-references
4. Deploy: `python scripts/deploy_kb.py knowledge-base/ --root-name my_kb`
5. Wire into agent: `--kb-manifest` flag on `deploy_with_tools.py`

---

## Error Handling

When user reports deployment or behavioral errors:

1. Read `references/correct_prompt.md` for E-code and B-code fix catalog
2. MERGE conditions when combining edges — never delete routing paths
3. PRESERVE all intended workflow behavior
4. Re-validate after fixing

---

## Quick Reference: Payload Structure

```json
{
  "name": "Agent Name",
  "conversation_config": {
    "agent": {
      "first_message": "...",
      "language": "en",
      "dynamic_variables": {"dynamic_variable_placeholders": {}},
      "prompt": {"prompt": "...", "tool_ids": [], "tools": [...]}
    },
    "tts": {"voice_id": "...", "model_id": "..."}
  },
  "platform_settings": {
    "data_collection": {...},
    "evaluation": {"criteria": [...]}
  },
  "workflow": {
    "prevent_subagent_loops": true,
    "nodes": {"start_node": {...}, "node_name": {...}},
    "edges": {"edge-id": {...}}
  }
}
```

For the complete schema with all node types, edge types, tool formats, expression operators, and constraints: **read `references/reference.md`**.
