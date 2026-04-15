# ElevenLabs Conversational AI — Technical Reference

Complete technical reference for building ElevenLabs voice agents. Covers the agent JSON schema, constraints, node/edge types, tools, post-call analysis, V3 mode, and the behavioral spec intermediate format.

---

## Input Type Detection

When source material is provided, identify the type to determine the analysis approach.

### Competitor Agent JSON

Look for these signatures:

| Platform | Signature Fields |
|----------|-----------------|
| **Retell** (Multi-State) | `states[]`, `starting_state`, `general_tools` |
| **Retell** (Flow-Based) | `nodes[]`, `edges[]` at root level with Retell field names |
| **Vapi** | `assistant`, `squad`, `firstMessage`, `model.provider` |
| **Bland** | `pathway`, `prompt`, `analysis_schema`, `transfer_list` |
| **ElevenLabs** | `conversation_config`, `workflow.nodes`, `workflow.edges` |

When a competitor format is detected, consult the corresponding `competitor/cheatsheet_*.md` for platform-specific mapping guidance.

### Call Scripts / SOPs

Indicators:
- Step-by-step numbered instructions
- "Agent says:" / "If caller says:" patterns
- Decision trees with branching ("If X, then Y; otherwise Z")
- Specific phrases in quotes that must be said verbatim
- Escalation rules ("Transfer to supervisor if...")

### Natural Language Descriptions

Indicators:
- Conversational English describing what the agent should do
- No structured format — just paragraphs or bullet points
- May be incomplete — expect to ask clarifying questions

### Documentation / Knowledge Base

Indicators:
- Product documentation, FAQ pages, policy documents
- Markdown or HTML formatted content
- Reference material rather than conversational flow
- Used as knowledge base content, not direct agent instructions

---

## Design Summary

When analyzing source material, the LLM produces an internal design summary covering:

- **Agent purpose** and communication mode (telephony-Twilio, telephony-SIP, web widget)
- **Tool inventory** — names, types, schemas, URLs if known
- **Split-point assessment** — for each candidate split point: routing type, wrong-routing cost, failed-transition cost, decision (see `architecture_framework.md`)
- **Proposed node map** — which `override_agent` nodes, which tool nodes, tools assigned per node
- **LLM and TTS model selection** with rationale (see `architecture_framework.md`)
- **Key business rules** and flow requirements

This summary is produced internally during generation (pipeline mode) or presented to the user for confirmation (interactive complex-agent mode). It is not a formal JSON schema — the LLM carries it in context and uses it to drive generation.

---

## Critical Constraints

### 1. Terminal Nodes Cannot Have Outgoing Edges

These node types are TERMINAL:
- `phone_number` — Phone transfer
- `standalone_agent` — AI-to-AI transfer  
- `end` — Call termination

**Error if violated**: `"It's not possible to transition from Phone transfer to Phone transfer."`

Failsafe handling: When a transfer fails, control returns to the calling `override_agent`. Put retry logic in the agent's prompt.

### 2. One Edge Per Node Pair (Most Common Error)

**STOP AND CHECK** before creating any edge: Does an edge already exist between these nodes IN EITHER DIRECTION?

You can ONLY have ONE edge object between any two nodes:

```json
// WRONG - Two separate edges (causes "Duplicate edge found")
{"edge-router-to-pharmacy": {"source": "intent_router", "target": "pharmacy_handler", ...}}
{"edge-pharmacy-to-router": {"source": "pharmacy_handler", "target": "intent_router", ...}}

// CORRECT - ONE edge with both directions
{
  "edge-router-pharmacy": {
    "source": "intent_router",
    "target": "pharmacy_handler",
    "forward_condition": {"type": "llm", "label": "Pharmacy", "condition": "Caller asking about prescriptions"},
    "backward_condition": {"type": "llm", "label": "Other Questions", "condition": "Caller has other questions"}
  }
}
```

**Naming Rule**: Use `edge-nodeA-nodeB` NOT `edge-nodeA-to-nodeB`.

**Multiple Conditions Same Direction:**
```json
// WRONG - Multiple edges A→B
{"edge-optical": {"source": "Router", "target": "Transfer", "forward_condition": "optical..."}}
{"edge-aesthetics": {"source": "Router", "target": "Transfer", "forward_condition": "aesthetics..."}}

// CORRECT - ONE edge with combined condition
{
  "edge-router-transfer": {
    "source": "Router",
    "target": "Transfer",
    "forward_condition": {"type": "llm", "condition": "Caller asking about optical OR aesthetics"},
    "backward_condition": null
  }
}
```

**Edge Creation Procedure:**
1. List ALL node pairs that need connections (ignore direction)
2. For EACH pair: one-way or bidirectional?
3. Create exactly ONE edge per pair
4. Name edges WITHOUT direction
5. VERIFY: # of edges must equal # of unique node pairs

### 3. No Multiple LLM Conditions in Expressions

**Wrong**: `{type: "or_operator", children: [{type: "llm"}, {type: "llm"}]}`
**Correct**: `{type: "llm", condition: "condition1 OR condition2"}`

### 4. TTS Model for English Agents

**Standard (non-V3):** Must use `eleven_turbo_v2` or `eleven_flash_v2`.
Do NOT use `eleven_turbo_v2_5` or `eleven_flash_v2_5` for English.

**V3 mode:** Must use `eleven_v3_conversational` with:
- `"expressive_mode": true`
- `"suggested_audio_tags"`: Array of 8-12 `{"tag": "...", "description": "..."}` objects

### 5. Turn Mode Values

`conversation_config.turn.mode` only accepts `"turn"` or `"silence"`:
- `"turn"` — agent responds after detecting end of user's turn (default, use for conversations)
- `"silence"` — agent responds after a silence threshold

Do NOT use `"conversational"` or any other value.

### 6. Start Node Key Must Be "start_node"

### 7. Start Edge Should Be Unconditional (no label needed)

### 8. No Self-Loop Edges

Put looping behavior in the node's prompt instead:
`"Continue answering the caller's questions until they indicate they're done"`

---

## Node Types

### start
```json
{
  "start_node": {
    "type": "start",
    "position": {"x": 0, "y": 0},
    "edge_order": ["edge-to-first-node"]
  }
}
```

### override_agent (REQUIRED FIELDS)
```json
{
  "node_name": {
    "type": "override_agent",
    "position": {"x": 0, "y": 0},
    "edge_order": ["edge-1", "edge-2"],
    "label": "Node Display Name",
    "additional_prompt": "Instructions for this node",
    "additional_knowledge_base": [],
    "additional_tool_ids": [],
    "conversation_config": {}
  }
}
```

**Tool scoping fields:**
- `additional_tool_ids`: Tool IDs to ADD to this node (on top of base config)
- `conversation_config.agent.prompt.tool_ids`: Override to REPLACE the base tool list

For workflow faithfulness, set `tool_ids: []` in the base config and use `additional_tool_ids` per node.

**Prompt fields (two modes):**

| Mode | Field | Behavior |
|------|-------|----------|
| **Append** (default) | `additional_prompt` | Appended to base prompt under `# Specific goal for this portion of the conversation` header. Base personality/tone/guardrails preserved. |
| **Override** | `conversation_config.agent.prompt.prompt` | Replaces the base prompt entirely. Base personality/tone lost unless re-added. |

**Use `additional_prompt` (append) by default.** The node instructions land at the end of the combined prompt — a high-attention position for LLMs — while personality and guardrails carry forward from the root prompt without duplication.

**Use override only when:**
- The node needs a fundamentally different interaction mode (e.g., IVR/hold-handling vs. conversation)
- The base prompt's instructions would conflict with the node's purpose
- The combined base + additional prompt exceeds ~4000 words and needs trimming
- The node requires a different persona

The UI's "Override prompt" toggle controls which mode is active. Both modes preserve full conversation history across node transitions.

### phone_number (TERMINAL)

```json
{
  "node_name": {
    "type": "phone_number",
    "position": {"x": 0, "y": 0},
    "edge_order": [],
    "transfer_destination": {
      "type": "phone",
      "phone_number": "+15551234567"
    },
    "transfer_type": "blind"
  }
}
```

**transfer_type values** (ONLY these are valid):
| Value | Description |
|-------|-------------|
| `"blind"` | Caller transferred without intro (cold) |
| `"conference"` | Agent stays until connected (warm) |
| `"sip_refer"` | SIP-based transfer |

**phone_number node vs transfer_to_number tool:**
| Approach | Error Handling | Use When |
|----------|----------------|----------|
| `phone_number` node | **NONE** — call ends on failure | Final fire-and-forget transfer |
| `transfer_to_number` tool | **YES** — returns to LLM | Need retry/fallback/error handling |

**Prefer `transfer_to_number` tool** for most transfers.

### end (TERMINAL)
```json
{"node_name": {"type": "end", "position": {"x": 0, "y": 0}, "edge_order": []}}
```

### standalone_agent (TERMINAL)
```json
{
  "node_name": {
    "type": "standalone_agent",
    "position": {"x": 0, "y": 0},
    "edge_order": [],
    "agent_id": "agent_xxx",
    "delay_ms": 0,
    "transfer_message": "Connecting you to a specialist...",
    "enable_transferred_agent_first_message": true
  }
}
```

### tool
```json
{
  "node_name": {
    "type": "tool",
    "position": {"x": 0, "y": 0},
    "edge_order": ["edge-success", "edge-failure"],
    "tools": [{"tool_id": "tool_xxx"}]
  }
}
```
Use with `result` condition type on edges to route based on tool execution outcome.

---

## Edge Structure

```json
{
  "edge-id": {
    "source": "source_node_name",
    "target": "target_node_name",
    "forward_condition": {
      "type": "llm",
      "label": "Short UI Label",
      "condition": "Detailed natural language condition"
    },
    "backward_condition": null
  }
}
```

### Condition Types

**LLM** — Natural language condition:
```json
{"type": "llm", "label": "Schedule Appointment", "condition": "User wants to schedule an appointment"}
```

**Unconditional** — Always taken:
```json
{"type": "unconditional"}
```

**Expression** — Variable-based:
```json
{
  "type": "expression",
  "label": "Billing Department",
  "expression": {
    "type": "eq_operator",
    "left": {"type": "dynamic_variable", "name": "department"},
    "right": {"type": "string_literal", "value": "billing"}
  }
}
```

**Result** — Tool execution routing:
```json
{"type": "result", "label": "Tool Succeeded", "successful": true}
```

**Expression operators:** `eq_operator`, `neq_operator`, `gt_operator`, `lt_operator`, `gte_operator`, `lte_operator`, `or_operator`, `and_operator`

**Value types:** `dynamic_variable`, `string_literal`, `number_literal`, `boolean_literal`

### Edge Constraints

- Always include `label` for UI display
- Every edge MUST have at least one condition
- No self-loops (source ≠ target)
- ONE edge per node pair
- backward_condition must be LLM type — NEVER unconditional (infinite loop)
- Unconditional edges should be LAST in `edge_order` when mixed with conditional

---

## Tools

Tools go in: `conversation_config.agent.prompt.tools[]`

### Webhook Tool
```json
{
  "type": "webhook",
  "name": "tool_name",
  "description": "What it does",
  "api_schema": {
    "url": "https://example.com/endpoint",
    "method": "POST",
    "request_body_schema": {
      "type": "object",
      "properties": {
        "param_name": {"type": "string", "description": "Parameter description"}
      },
      "required": ["param_name"]
    },
    "request_headers": {"Content-Type": "application/json"}
  },
  "response_timeout_secs": 20
}
```

### System Tools

**end_call:**
```json
{"type": "system", "name": "end_call", "description": "", "params": {"system_tool_type": "end_call"}}
```

**transfer_to_number** (recommended for phone transfers):
```json
{
  "type": "system",
  "name": "transfer_to_number",
  "description": "Transfer caller to appropriate department",
  "params": {
    "system_tool_type": "transfer_to_number",
    "enable_client_message": true,
    "transfers": [
      {
        "transfer_destination": {"type": "phone", "phone_number": "+15551234567"},
        "condition": "When caller asks about billing or payments",
        "transfer_type": "conference"
      }
    ]
  }
}
```

**transfer_to_agent:**
```json
{
  "type": "system",
  "name": "transfer_to_agent",
  "description": "Transfer to specialized agent",
  "params": {
    "system_tool_type": "transfer_to_agent",
    "transfers": [
      {
        "agent_id": "agent_xxx",
        "condition": "When caller needs specialized support",
        "delay_ms": 0,
        "transfer_message": "Connecting you now...",
        "enable_transferred_agent_first_message": true
      }
    ]
  }
}
```

**play_keypad_touch_tone** (DTMF for IVR navigation):
```json
{
  "type": "system",
  "name": "play_keypad_touch_tone",
  "description": "Send DTMF tones to navigate phone menus. Enter ALL digits in a single call as one string. Always insert w between groups of 2-4 digits for a 0.5-second pause (e.g., 123w456w7890 for a 10-digit number). Never call this tool one digit at a time.",
  "params": {
    "system_tool_type": "play_keypad_touch_tone",
    "suppress_turn_after_dtmf": true,
    "disable_interruptions": true,
    "use_out_of_band_dtmf": false,
    "force_pre_tool_speech": false
  }
}
```

`dtmf_tones` string characters: `0-9`, `*`, `#`, `w` (0.5s pause), `W` (1.0s pause). The tool description MUST match the prompt's DTMF instructions — conflicting guidance (tool says "if needed," prompt says "always") causes the LLM to skip pauses. See `architecture_framework.md` DTMF Patterns for pacing tables.

**Other system tools:** `language_detection`, `skip_turn`, `voicemail_detection`

### Dynamic Variables in Tools

Use `{{variable_name}}` syntax for dynamic routing:
```json
{
  "transfer_destination": {
    "type": "phone_dynamic_variable",
    "phone_number": "{{department_phone}}"
  }
}
```

**System variables:** `system__caller_id`, `system__agent_id`, `system__agent_turns`

### Tool Schema Rules

1. **URLs must be static** — no `{{variable}}` in paths. Move dynamic values to request body.
2. **Transfer types**: Only `"blind"`, `"conference"`, or `"sip_refer"`. Never "warm" or "cold".
3. **Every property needs description** (or `constant_value`, `dynamic_variable`, `is_system_provided`)
4. **Array items need full schema** — `items` is REQUIRED on arrays. `constant_value` is NOT allowed on arrays.
5. **query_params_schema cannot have "type": "object"** at root
6. **Do NOT include empty `path_params_schema` or `query_params_schema`**
7. **`request_headers` must be an object** (not array)
8. **Always include an `end_call` tool**
9. **Property fields are mutually exclusive** — only ONE of: `description`, `constant_value`, `dynamic_variable`, `is_system_provided`
10. **Value paths use DOT notation** — `data.items.0.id` NOT `data.items[0].id`

### Secret Headers

For Authorization headers using workspace secrets:
```json
"request_headers": {
  "Content-Type": "application/json",
  "Authorization": {"secret_id": "gO9jzFRynUe4Egm7lapj"}
}
```
Retrieve secret IDs via `GET /v1/convai/secrets`.

### Response Variable Assignments

Extract values from tool responses into dynamic variables:
```json
"assignments": [
  {
    "source": "response",
    "dynamic_variable": "cartId",
    "value_path": "data.createCart.cart.id"
  }
]
```

---

## Dynamic Variables

**CRITICAL LIMITATION**: Dynamic variables can ONLY be populated from external sources:
- Pre-call webhooks
- Webhook tool responses
- SDK call initiation

You CANNOT use `{{variable}}` with data extracted from conversation. Use LLM edge conditions for routing based on conversation content.

### Placeholder Declaration (REQUIRED)

If using `{{variable_name}}` anywhere, you MUST declare placeholders:

```json
"conversation_config": {
  "agent": {
    "dynamic_variables": {
      "dynamic_variable_placeholders": {
        "full_name": "Jane Doe",
        "specialist": "cardiologist"
      }
    }
  }
}
```

Placeholders are default values for the ElevenLabs UI; actual values come at call time via SDK/API/webhook.

### Test Mode: Resolving Variables in Conditional Prompts

When generating test mode agents, dynamic variables must be replaced with hardcoded values. However, **do NOT do a naive find-and-replace** on prompts that use variables as boolean/string flags in conditional logic.

A production prompt like:
```
If {{capsuleEligible}} is true AND {{hasPriorPharmacy}} is false:
  Say: "Would you like delivery?"
```

Becomes this **broken** prompt after naive replacement:
```
If true is true AND false is false:
  Say: "Would you like delivery?"
```

The LLM cannot reason about `If true is true`. Instead, **pre-resolve the conditions** and write direct instructions:
```
Since the patient is Capsule-eligible and has no prior pharmacy, say:
"Would you like your prescriptions delivered to your door for free?"
```

**Rules for test mode variable replacement:**
- Simple value references (names, dates, medication lists) → direct string substitution is fine
- Conditional logic using variables as flags → **rewrite the prompt from scratch**, keeping only the branches that match the test values
- Edge conditions referencing `{{variables}}` → resolve to concrete values

---

## Knowledge Base (RAG)

### Architecture

Agents can access reference documents through a knowledge base. Documents are attached to the agent via `conversation_config.agent.prompt.knowledge_base` — an array of `KnowledgeBaseLocator` objects:

```json
{
  "type": "file",
  "id": "doc_abc123",
  "name": "product_faq.md",
  "usage_mode": "auto"
}
```

**`KnowledgeBaseLocator` fields:**
- `type`: `"file"` | `"url"` | `"text"` | `"folder"` — folder references include all docs inside
- `id`: ElevenLabs document/folder ID
- `name`: human-readable name
- `usage_mode`: `"auto"` (RAG retrieval, recommended) or `"prompt"` (injected into system prompt in full — only for very small docs)

**Document types and limits:**
- File upload (`POST /v1/convai/knowledge-base/file`): PDF, EPUB, DOCX, TXT, MD, HTML — max 20MB
- URL (`POST /v1/convai/knowledge-base/url`): fetches and indexes a webpage
- Text (`POST /v1/convai/knowledge-base/text`): raw text content
- Folders (`POST /v1/convai/knowledge-base/folder`): organizational containers

### RAG Config

```json
"rag": {
  "enabled": true,
  "embedding_model": "e5_mistral_7b_instruct",
  "max_documents_length": 50000,
  "max_vector_distance": 0.6,
  "max_retrieved_rag_chunks_count": 20
}
```

| Field | Default | Notes |
|---|---|---|
| `embedding_model` | `e5_mistral_7b_instruct` | 1024-token chunks, 192 overlap. Best for English. |
| `embedding_model` | `multilingual_e5_large_instruct` | 450-token chunks, 62 overlap. Use for non-English. |
| `embedding_model` | `qwen3_embedding_4b` | 1024-token chunks, 192 overlap. |
| `max_documents_length` | 50000 | Max total characters of all retrieved chunks combined. |
| `max_vector_distance` | 0.6 | Chunks with similarity below this threshold are discarded. |
| `max_retrieved_rag_chunks_count` | 20 | Max chunks retrieved from vector store per turn. |

### How RAG Retrieval Works (Internals)

1. **Query rewrite**: The user's latest message is rewritten by an LLM (Gemini/Qwen) into a self-contained question incorporating chat history. Falls back to raw user message on 1.5s timeout.
2. **Chunking**: Documents are converted to HTML, then split token-by-token using `RecursiveCharacterTextSplitter`. Separators: `</p>`, `\n\n`, `\n`, sentence-ending punctuation, space. No special handling for markdown headers, bullet points, or tables.
3. **Embedding similarity**: Query embedding is compared against chunk embeddings via MongoDB Atlas Vector Search, filtered by `document_id` only. Document names, folder paths, and other metadata are NOT used in search.
4. **Filtering**: Chunks below `max_vector_distance` or exceeding cumulative `max_documents_length` are dropped.
5. **Injection**: Retrieved chunks are appended after the system prompt, wrapped in `[Beginning of retrieved RAG chunk]...[End of retrieved RAG chunk]`. Prompt-mode docs appear as "Knowledgebase relevant to the whole conversation"; RAG chunks as "Knowledgebase relevant to the last user message."

### Per-Node KB Scoping

- `knowledge_base` on the base agent: available to ALL nodes
- `additional_knowledge_base` on `override_agent` nodes: additive, same pattern as `additional_tool_ids`
- Cannot remove base KB docs from a node — strictly additive
- Strategy: for fully scoped KB, put nothing on the base agent and assign everything via `additional_knowledge_base` per node. Reference folder IDs for convenience.
- **Per-node KB scoping is a secondary benefit of an already-justified node split, not a primary reason to create nodes.** For KBs <100 docs with distinct topics, single-node with all docs works fine — embedding similarity + distance threshold filter out irrelevant chunks.

### Article Design Best Practices

These are verified against the actual chunking and retrieval implementation:

1. **Use question-style headings** — most impactful practice. The retrieval query is a rewritten question, so Q-style headings (e.g. "## What medications are available?") increase embedding similarity with user queries.

2. **Keep articles to 1.5-3 KB** — maps to 1-2 chunks with `e5_mistral_7b_instruct` (1024 tokens ≈ 4KB). Each chunk is more likely to contain a complete answer. Note: chunking doesn't respect article boundaries — it splits mechanically on paragraphs, newlines, and sentence endings.

3. **Minimize duplication across articles** — duplicate content wastes the 20-chunk retrieval slots with redundant results. However, cross-references ("see article X") are meaningless — the LLM only sees retrieved chunks, not referenced articles. If the LLM needs context from another article, that content must appear in a chunk that gets retrieved on its own merit.

4. **Skip YAML front matter** — RAG retrieval is pure embedding similarity. No metadata is used. Front matter becomes noise in the first chunk and can cause false-positive retrieval on keyword matches.

5. **Structure for clean chunk boundaries** — use paragraph breaks (`\n\n`) and clear sentence endings between logical sections. These are the primary split points the chunker uses.

---

## Post-Call Analysis

Both data collection and evaluation run **after the call ends** (not during). Data collection runs first, then evaluation. Each field/criterion is a separate LLM call (Gemini 2.5 Flash). Results are stored with the conversation record and accessible via API.

### Data Collection (`platform_settings.data_collection`)

Extract structured data from the conversation transcript.

```json
{
  "platform_settings": {
    "data_collection": {
      "caller_name": {"type": "string", "description": "The caller's full legal name as confirmed during the call"},
      "call_outcome": {"type": "string", "description": "Final outcome of the call", "enum": ["completed", "declined", "abandoned", "transferred"]},
      "vehicle_year": {"type": "integer", "description": "Model year of the vehicle discussed"},
      "hard_inquiry_authorized": {"type": "boolean", "description": "Whether the caller verbally said 'yes' to the hard credit inquiry disclosure"}
    }
  }
}
```

**Schema rules:**
- Allowed types: `"boolean"`, `"string"`, `"integer"`, `"number"` (no objects or arrays)
- `enum` is only valid for `"string"` type — provides constrained values for the extraction LLM
- `description` is the extraction instruction — the LLM uses it to determine what to pull from the transcript
- Max **40 fields** (25 on non-enterprise tiers)
- If extraction fails or data isn't in the transcript, `value` is `null`

**Best practices for data collection:**

1. **Write descriptions as extraction instructions**, not labels. The LLM sees `"description"` as its prompt for what to find.

| Bad | Good |
|-----|------|
| `"Customer name"` | `"The caller's full legal name as stated and confirmed during the call"` |
| `"Outcome"` | `"Final outcome: did the application get submitted, was the caller declined, or did they choose not to proceed"` |
| `"Amount"` | `"The monthly mortgage payment amount the caller reported, in dollars"` |

2. **Use boolean for yes/no facts** — more reliable than string extraction:
   - `"authorized_soft_inquiry"`: `boolean` — "Whether the caller verbally said 'yes' to the soft credit inquiry authorization"
   - `"has_cosigner"`: `boolean` — "Whether the credit report showed a co-signer on the auto loan"

3. **Use enum for constrained categories** — helps the LLM pick from valid options:
   - `"housing_type"`: `string`, `enum: ["rent", "mortgage", "family_friends", "own_outright"]`
   - `"employment_status"`: `string`, `enum: ["employed", "self_employed", "retired", "unemployed"]`

4. **Use integer/number for numeric values** — not strings:
   - `"monthly_income"`: `number` — "Gross monthly income in dollars as reported by the caller"
   - `"vehicle_mileage"`: `integer` — "Exact mileage of the vehicle as stated by the caller"

5. **Keep field count practical** — each field is a separate LLM call. 5-15 fields is typical. Only collect what you'll actually use for analytics or follow-up.

6. **Design for null** — if the caller hangs up early, most fields will be null. Don't treat null as an error.

7. **Avoid extracting what you already have** — if `customer_name` comes from a dynamic variable at call initiation, don't re-extract it post-call.

8. **Never reference other fields in descriptions** — each field is extracted in a separate, independent LLM call. The extraction LLM for field B does not see field A's result. Descriptions like "Only populated when is_coverage_active = 'yes'" create an impossible contract. Instead, make each description self-contained: "Only extract if the representative confirmed active coverage during the call."

9. **Never request multi-value / comma-separated responses** — the platform only supports scalar types. The extraction prompt tells the LLM to return null when "multiple answers are equally valid," which directly conflicts with "select all that apply." If you need multiple values, split into: a primary field (string with enum for the most important value) and a secondary field (free-text for additional values).

10. **Keep descriptions under ~500 characters** — long descriptions (2000+ chars) dilute the extraction instruction. The LLM receives: system prompt + full transcript + your field schema. If the schema is a wall of text, the model loses focus on what to extract. Let enum lists do the structural guidance; keep the description to the extraction instruction itself.

11. **Use enum liberally for string fields** — enum values are shown in the extraction prompt and provide stronger guidance than descriptions alone. Even large enums (50+ values) are more reliable than description-only fields, because the LLM has a constrained vocabulary to choose from. Note: extracted values are NOT validated against the enum — the LLM can still return non-enum values, but it rarely does when the enum is present.

### Evaluation Criteria (`platform_settings.evaluation`)

Evaluate call quality against specific goals. Each criterion produces `success`, `failure`, or `unknown`.

```json
{
  "platform_settings": {
    "evaluation": {
      "criteria": [
        {
          "id": "disclosure_compliance",
          "name": "Disclosure Compliance",
          "type": "prompt",
          "conversation_goal_prompt": "Evaluate whether the agent read ALL required verbatim disclosures. Specifically check: (1) the soft inquiry authorization starting with 'Before we can perform a prequalification inquiry', (2) the hard inquiry authorization starting with 'I have everything needed to submit your application', (3) the ECOA income disclosure about alimony/child support, and (4) the citizenship question 'Are you a US Citizen, Permanent Resident, or Temporary Resident'. Mark SUCCESS only if all applicable disclosures were read. If the call ended before reaching a disclosure, mark UNKNOWN for that disclosure.",
          "use_knowledge_base": false
        },
        {
          "id": "information_completeness",
          "name": "Information Completeness",
          "type": "prompt",
          "conversation_goal_prompt": "Evaluate whether the agent collected all required application information before moving to the next phase. Required fields: full legal name, phone number, email, current address, housing type and payment, employment status and income details, SSN, and date of birth. Mark SUCCESS if all fields were collected. Mark FAILURE if the agent skipped a required field. Mark UNKNOWN if the call ended before the collection phase completed.",
          "use_knowledge_base": false
        }
      ]
    }
  }
}
```

**Schema rules:**
- Only type `"prompt"` exists — no other evaluation types
- `conversation_goal_prompt`: max **2000 characters** — this is the evaluation instruction
- `use_knowledge_base`: includes RAG chunks in the evaluation context — untested at scale, avoid for now
- Max **30 criteria**
- `id` must be unique; defaults to `name` if omitted
- Overall `call_successful` = all criteria must be `success` (any `failure` → overall failure, any `unknown` with no failures → overall unknown)

**Best practices for evaluation criteria:**

1. **Write as evaluation questions, not agent instructions.** The evaluation LLM sees the transcript and your prompt — it's judging, not acting.

| Bad | Good |
|-----|------|
| `"The agent should greet the customer"` | `"Evaluate whether the agent greeted the customer by name within the first 30 seconds of the call"` |
| `"Read all disclosures"` | `"Evaluate whether each required verbatim disclosure was read in full, without paraphrasing or skipping words"` |

2. **Be specific about what constitutes success.** The LLM needs clear criteria, not vague goals.

| Bad | Good |
|-----|------|
| `"Was the call successful?"` | `"Evaluate whether the application was fully submitted (hard inquiry authorized and submit_application confirmed) OR the caller was properly informed of a decline reason with the appropriate decline statement"` |
| `"Did the agent handle objections?"` | `"Evaluate whether the agent responded to rate/inquiry objections with the approved rebuttal language rather than making up responses or providing unauthorized rate guarantees"` |

3. **Account for early termination.** Calls end early for many reasons. Use `UNKNOWN` guidance:
   - "If the call ended before reaching this phase, mark UNKNOWN"
   - "If the caller hung up before the agent could read the disclosure, mark UNKNOWN rather than FAILURE"

4. **Keep criteria independent.** Since overall success requires ALL criteria to pass, overlapping criteria make the overall metric overly strict.

5. **Use 3-5 criteria for most agents.** Each is a separate LLM call. Focus on what matters most:

| Category | Example Criterion |
|----------|-------------------|
| **Compliance** | Were all required disclosures read verbatim? |
| **Completeness** | Were all required data fields collected? |
| **Accuracy** | Did the agent correctly identify decline conditions and use the right decline statement? |
| **Boundaries** | Did the agent stay within scope (no unauthorized rate promises, no credit advice)? |
| **Outcome** | Was the application submitted, or was the caller properly informed of next steps? |

6. **Group related checks into one criterion.** Instead of 4 separate disclosure criteria, combine them: "Evaluate whether ALL of the following disclosures were read: (1) soft inquiry, (2) hard inquiry, (3) ECOA, (4) citizenship."

7. **Reference specific language from the transcript.** The evaluation LLM sees timestamped messages — your prompt can reference what to look for: "Check whether the agent said the phrase 'Before we can perform a prequalification inquiry' verbatim."

**Placement**: `platform_settings` is a top-level sibling of `conversation_config` and `workflow`.

---

## Workflow Faithfulness (Preventing Node Skipping)

### Why Agents Skip Nodes

1. **Nested subgraph tool schemas**: Edge tools include conditions for the entire reachable subgraph (~10 nodes deep). The LLM can pre-fill future conditions.
2. **Speculative transition meta-prompt**: A hardcoded instruction encourages the LLM to fire transitions based on inferred intent.
3. **Global tool inheritance**: All tools are available at every node by default.
4. **Base prompt flow descriptions**: Describing the overall flow gives the LLM a roadmap to skip ahead.

### Defense 1: Tool Scoping Per Node

Set `tool_ids: []` in base config. Use `additional_tool_ids` per node.

```json
{
  "conversation_config": {
    "agent": {
      "prompt": {
        "tool_ids": [],
        "tools": [/* all tools defined here */]
      }
    }
  },
  "workflow": {
    "nodes": {
      "authentication": {
        "type": "override_agent",
        "additional_tool_ids": ["tool_id_for_client_lookup"]
      },
      "scheduling": {
        "type": "override_agent",
        "additional_tool_ids": ["tool_id_for_check_availability", "tool_id_for_book_appointment"]
      }
    }
  }
}
```

### Defense 2: Boundary Instructions

Add `# Boundaries` to every node prompt:
```
# Boundaries
Do NOT discuss services, pricing, or appointment availability.
Do NOT call any tools other than 'client_lookup' and 'generate_auth_token'.
Do NOT ask about scheduling until authentication is fully complete.
```

### Defense 3: Tight Edge Conditions

| Tight (Recommended) | Loose (Causes Skipping) |
|---------------------|------------------------|
| "'client_lookup' tool returned a matching record" | "Customer is identified" |
| "Caller confirmed 'yes' AND 'generate_auth_token' returned success" | "Authentication complete" |
| "'book_appointment' returned a confirmation with a booking ID" | "Appointment booked" |

### Base Prompt: What NOT to Include

Remove from the root prompt:
- **Flow descriptions** ("Step 1: Greet. Step 2: Authenticate...")
- **Global tool instructions** for scoped tools
- **Phase-awareness hints**

The base prompt should contain ONLY: personality, tone, global guardrails, character normalization rules.

---

## Node Architecture: When to Split vs Merge

For the full decision framework — including the 5-phase pipeline (PREPARE → CLASSIFY → ASSESS → ARCHITECT → VALIDATE), split-point risk assessment, decision matrix, and LLM/TTS model selection guidance — see `architecture_framework.md`.

For the full list of why edges fail (mechanical failures, configuration failures, platform pitfalls) — see `edge_failures.md`.

### How Node Transitions Work Internally

Each `override_agent` node transition:
1. The LLM calls a `notify_condition_X_met` tool (injected per outgoing edge)
2. The current **brain is terminated** (`BrainTerminationReason.AGENT_TRANSFER`)
3. A **new brain is constructed** for the target node
4. Conversation history is preserved, but transfer tool calls are hidden from the new brain

Each transition is a full LLM teardown + rebuild. This means:
- **Latency**: Brain construction takes measurable time (dead air)
- **Failure risk**: If the LLM malforms the notify tool call, all conditions evaluate to false → no transition → agent stuck
- **Cascade restart**: New brain starts fresh LLM cascade from primary model
- **Context re-reading**: The new brain must re-parse the full conversation history

### Split Decision Summary

**Default**: single `override_agent` node with labeled internal phases in the prompt.

**Split only when the split-point risk assessment (see `architecture_framework.md`) justifies it:**

| Routing Type | When to Split |
|-------------|---------------|
| **DATA** | Tool result drives routing → tool node + expression edges (always split — deterministic) |
| **SCOPING** | High-risk tool must be restricted → node boundary for hard scoping |
| **JUDGMENT** | Only when wrong-routing cost HIGH + failed-transition cost LOW; otherwise keep in prose |

**When NOT to split:**

| Anti-Pattern | Better Approach |
|-------------|----------------|
| Sequential phases (auth → verify → collect → wrap-up) | One node with labeled internal phases |
| Simple if/then branch | Prompt-level branching |
| Wrap-up as its own node | End-of-prompt instructions in previous node |
| IVR as a separate node (unless prompt size demands it) | Internal phase + `skip_turn` + `suppress_turn_after_dtmf` |

### Prompt-Level Phase Management

When merging phases into a single node, structure the prompt with clear internal phases:

```
# Phase 1 — [Label]
[Instructions for this phase. What to collect, what to ask, what tool to call.]
Do not move to Phase 2 until [specific completion criteria].

# Phase 2 — [Label]
[Instructions for this phase.]
If [condition], proceed to Phase 3. If [other condition], [handle accordingly].

# Phase 3 — [Label]
[Instructions for this phase.]
```

Completion criteria between phases should be specific and unambiguous (e.g., "both name and DOB confirmed" not "authentication complete"). The LLM tracks which phase it's in from conversation history.

### Tool Accumulation Warning

`additional_tool_ids` on an `override_agent` node ADDS to the base agent's `tool_ids`. You cannot remove a base-level tool from a specific node. When tool scoping matters: put NO tools on the base agent's `tool_ids` and use `additional_tool_ids` exclusively per node.

### Dynamic Variable Constraints

- All dynamic variables MUST have defaults or the agent JSON won't upload. Use `""`, `"unknown"`, or `"pending"` for variables set at runtime by tools.
- Variables set at call initiation (e.g., `{{patient_name}}`) are populated by the calling system; define with placeholder defaults.
- For SOPs/natural language: use placeholder webhook URLs and document required auth headers for customer configuration post-generation.

### Telephony Prompt Patterns

**Hold/silence handling:**

The agent cannot detect hold music from audio. VAD treats music as speech. The LLM only sees the raw ASR transcript — no confidence score, no audio-type metadata.

- If transcript appears to be noise/garbled/meaningless: call `skip_turn` and wait silently.
- `skip_turn` disables both `turn_timeout` and `silence_end_call_timeout` for that turn — this is why it's the correct tool for holds.
- Never `end_call` because of hold/silence.
- Anti-narration: never verbalize internal actions ("I need to wait," "Let me look that up"). Everything the agent says is spoken aloud.
- **Platform setting:** `silence_end_call_timeout` (default `-1` = disabled). If enabled, extended silence disconnects the call unless `skip_turn` is active.

**Voice normalization:**

For `eleven_v3_conversational`, number normalization is entirely prompt-driven. For V2 models, the TTS normalizer can handle numbers when `TextNormalisationType.ELEVENLABS` is set.

- Long digit sequences: break into groups of 3-4 with pauses. Read digit-by-digit.
- Alphanumeric codes: spell character by character. Never use NATO alphabet unless domain requires it.
- Pacing mechanisms by reliability: SSML `<break time="Xs"/>` (most reliable) > punctuation (model-dependent) > V3 audio tags `[slow]` > `speed` parameter (0.7-1.2, global).
- No TTS-level volume control. Provide explicit output examples in the prompt.

**Garbled STT handling:**

The LLM receives only raw transcript text — no confidence metadata. Telephony (ULAW_8000) has lower VAD thresholds, so agents see more garbled transcripts.

- If transcript looks like noise/nonsense: call `skip_turn` rather than "I didn't understand."
- Several consecutive garbled turns: politely ask the other party to repeat.
- Timeout placeholder: `"..."` means silence (turn timeout), not noise.

### first_message Guidance

| Scenario | Guidance |
|----------|----------|
| **Inbound telephony** | Brief greeting + purpose. "Thank you for calling [company], how can I help you?" |
| **Outbound telephony** | Identify self + reason. Keep under 2 sentences — human may talk over. |
| **Web widget** | Welcoming + prompt engagement. Can be slightly longer since user sees text. |
| **No first_message** | Agent waits for user to speak first. Valid for some inbound scenarios. |

---

## Prompt Writing Guidance

### Root Agent Prompt Template

```
# Personality
You are [NAME], a [ROLE] at [COMPANY].
[2-3 personality traits]

# Environment
[Channel and system context]

# Tone
[Response style — concise, professional]
Keep explanations under [X] sentences.

# Guardrails
Never ask for sensitive information such as passwords or PINs.
Maintain a professional tone even when users express frustration.
Remain within scope of [allowed topics].
```

### Override Agent Prompt Template

```
# Goal
[Single clear objective]

# Instructions
1. [Action 1]
2. [Action 2]. This step is important.
3. [Action 3]

# Tools
Call '[tool_name]' when [specific condition].
If '[tool_name]' fails, [fallback behavior].

# Boundaries
Do NOT [action from other nodes].
Do NOT call tools other than [listed tools].

# Exit
When [observable condition with tool reference], conversation can progress.
```

### LLM Condition Best Practices

| Good (Observable + Concrete) | Bad (Vague + Speculatable) |
|------------------------------|---------------------------|
| "'client_lookup' tool returned a matching record" | "Customer is identified" |
| "Caller said they want to speak with a human" | "Caller is frustrated" |
| "'book_appointment' tool returned a booking ID" | "Appointment booked" |
| "Caller confirmed address by saying 'yes'" | "Address verified" |

### Voice-Specific: Character Normalization

```
# For speech to user:
"plus one four one five five five zero one three four"
"john at gmail dot com"

# For tool parameters:
"+14155550134"
"john@gmail.com"
```

### Prompt Design Principles

1. Separate into sections — `# Goal`, `# Instructions`, `# Tools`, `# Boundaries`, `# Exit`
2. One action per line
3. Be concise
4. Emphasize critical steps — "This step is important."
5. Give examples of expected responses
6. Handle tool failures in prompt
7. Guardrails section gets extra model attention
8. Boundary instructions in every node
9. Never describe the full flow in the ROOT prompt — let the workflow engine control progression. Individual node prompts CAN have internal phase labels describing their own flow.
10. Reference tool results in exit conditions

---

## Complete Payload Structure

```json
{
  "name": "Agent Name",
  "conversation_config": {
    "agent": {
      "first_message": "Hello! How can I help you today?",
      "language": "en",
      "dynamic_variables": {
        "dynamic_variable_placeholders": {}
      },
      "prompt": {
        "prompt": "# Personality\nYou are...",
        "tool_ids": [],
        "tools": [
          {"type": "system", "name": "end_call", "description": "", "params": {"system_tool_type": "end_call"}}
        ]
      }
    },
    "asr": {
      "quality": "high",
      "user_input_audio_format": "ulaw_8000"
    },
    "turn": {
      "turn_timeout": 15,
      "mode": "turn"
    },
    "tts": {
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "model_id": "eleven_turbo_v2"
    }
  },
  "platform_settings": {
    "evaluation": {"criteria": [...]},
    "data_collection": {"field": {"type": "string", "description": "..."}}
  },
  "workflow": {
    "prevent_subagent_loops": true,
    "nodes": {
      "start_node": {"type": "start", "position": {"x": 0, "y": 0}, "edge_order": []},
      "node_name": {
        "type": "override_agent",
        "position": {"x": 200, "y": 0},
        "edge_order": [],
        "label": "Node Name",
        "additional_prompt": "...",
        "additional_knowledge_base": [],
        "additional_tool_ids": ["tool_id"],
        "conversation_config": {}
      }
    },
    "edges": {
      "edge-start": {
        "source": "start_node",
        "target": "node_name",
        "forward_condition": {"type": "unconditional"},
        "backward_condition": null
      }
    }
  }
}
```

**CRITICAL**:
- Nodes go inside `workflow.nodes`, edges go inside `workflow.edges`
- Set `prevent_subagent_loops: true` for complex flows
- Set `tool_ids: []` in base prompt + `additional_tool_ids` per node
- Always include `end_call` system tool
- `platform_settings` is a top-level sibling of `conversation_config` and `workflow`

---

## V3 Mode: Expression Tags & Personality-Driven Agents

V3 mode generates personality-rich agents optimized for ElevenLabs TTS with expression tags and natural speech patterns.

### Expression Tags Reference

Tags go BEFORE the text they modify: `[excited] That's amazing!`

**Syntax Rules:**
- Max 2 words per tag: `[chuckles lightly]` valid, `[chuckles very lightly]` NOT
- No nesting: `[excited [whisper]]` invalid
- No emojis, no parentheticals — ONLY bracketed tags
- 1-3 tags per response for natural agents, up to 5+ for theatrical

**Tag Categories:**

| Category | Tags |
|----------|------|
| Emotion/Tone | `[excited]`, `[warm]`, `[warmly]`, `[softly]`, `[thoughtful]`, `[calm]`, `[gentle]`, `[genuine]`, `[supportive]`, `[apologetic]`, `[understanding]`, `[confident]` |
| Actions | `[laughs]`, `[chuckles]`, `[sighs]`, `[exhales]`, `[clears throat]` |
| Pacing | `[pause]`, `[long pause]`, `[faster]`, `[slow]`, `[quick]` |
| Delivery | `[whisper]`, `[checking]`, `[focused]`, `[considering]`, `[reassuring]` |

### V3 TTS Configuration

```json
"tts": {
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "model_id": "eleven_v3_conversational",
  "expressive_mode": true,
  "suggested_audio_tags": [
    {"tag": "warmly", "description": "Warm tone for greetings and acknowledgments"},
    {"tag": "checking", "description": "Looking something up or reviewing information"},
    {"tag": "reassuring", "description": "Calming the caller when they seem concerned"},
    {"tag": "apologetic", "description": "Expressing regret when something doesn't work out"},
    {"tag": "calm", "description": "Steady, even tone for confused callers"},
    {"tag": "um", "description": "Natural thinking filler"},
    {"tag": "hmm", "description": "Considering or processing information"},
    {"tag": "confirming", "description": "Verifying information back to the caller"}
  ]
}
```

**V3 TTS requirements:**
- `model_id` MUST be `"eleven_v3_conversational"`
- `expressive_mode` MUST be `true`
- `suggested_audio_tags` MUST include 8-12 tags from the persona prompt

### Energy Level Profiles

| Energy | Filler Words | Tags/Response | Best For |
|--------|-------------|---------------|----------|
| **Low/Steady** | Moderate | 1-2 | Advisors, chill companions |
| **Medium/Warm** | Light | 1-3 | **Professional agents (recommended)** |
| **High/Energetic** | Heavy | 2-4 | Enthusiastic companions |
| **Chaotic/Theatrical** | Extreme | 3-5+ | Character agents |

### V3 TTS Technical Rules

1. Output only words to be spoken — no markdown, no formatting, no HTML tags, no SSML tags. V3 reads everything aloud, including `<br>`, `<break>`, `**bold**`, etc.
2. No emojis
3. Use `[tags]` not `(laughing)` or `*laughing*`
4. Write out numbers: "twenty-three" not "23"
5. Standard ASCII characters and punctuation only
6. Tag length: 1-2 words max
7. Use `...` for pauses, `—` for interruptions
8. For telephony: avoid silence-producing tags (`[pause]`, `[long pause]`, `[slow]`) — they create dead air. Use sound-producing filler tags (`[um]`, `[hmm]`, `[checking]`) or punctuation instead.
9. `optimize_streaming_latency` is a V2-only parameter. It is ignored by V3. Do not include it in V3 configs.

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Duplicate edge found between X and Y` | Multiple edges between same pair | Use ONE edge — backward_condition for reverse |
| `An edge cannot connect a node to itself` | Self-loop | Remove edge, put logic in prompt |
| `Input should be 'blind', 'conference' or 'sip_refer'` | Invalid transfer_type | Use "blind" or "conference" |
| `URL placeholders must match path_params_schema` | `{{var}}` in URL path | Static URL + request body |
| `English Agents must use turbo or flash v2` | Wrong TTS model | Use `eleven_turbo_v2` |
| `Expression cannot contain multiple LLM values` | OR with multiple LLM children | Single LLM with "OR" |
| `It's not possible to transition from Phone transfer` | Terminal node has outgoing edge | Remove edge, put failsafe in prompt |
| `Must set one of: description, dynamic_variable...` | Missing description on property | Add `"description": "..."` |
| `Extra inputs are not permitted` (query_params) | Root has `"type": "object"` | Remove `"type"` |
| `Field required: items` (array) | Array missing items schema | Add `"items": {...}` |

### Error Fixing Principle

When fixing errors, PRESERVE workflow intent:
- **DO** merge conditions: "condition1 OR condition2"
- **DO** verify all routing paths still work
- **DO NOT** delete conditions just to fix errors
- **DO NOT** simplify routing in ways that lose functionality

---

## Tool API Creation (Programmatic)

When creating tools via the API (`POST /v1/convai/tools`), wrap in `tool_config`:

```json
{
  "tool_config": {
    "type": "webhook",
    "name": "my_tool",
    "description": "...",
    "api_schema": {...},
    "response_timeout_secs": 120
  }
}
```

Share with workspace: `POST /v1/workspace/resources/{id}/share`
```json
{"role": "admin", "resource_type": "convai_tools", "group_id": "default"}
```

---

## Transfer Architecture Patterns

### Global Reachability (Transfer from Any Node)

For behaviors that should be available everywhere (transfer to human, end call), use system tools in the root prompt instead of adding edges from every node:

```
# Tools
If any tool returns an error, apologize and call 'transfer_to_number'.

Call 'transfer_to_number' when:
- Caller asks for human/representative/customer service
- Caller needs help outside your capabilities
- You cannot resolve after 2 attempts

Call 'end_call' when caller says goodbye or issue is resolved.
```

### Transfer Patterns

| Pattern | Implementation |
|---------|---------------|
| Transfer → End on failure | LLM condition "Transfer failed" → `end` node |
| Transfer → Fallback on failure | LLM condition → `override_agent` (fallback) → `phone_number` |
| Catch-all routing | Combined LLM: "Unknown intent OR confused OR escalation" |

Key points:
- `transfer_to_number` is invoked by LLM from prompt, not by edges
- Success/failure detection uses LLM conditions
- Each phase handles its own transfers — logic stays co-located
