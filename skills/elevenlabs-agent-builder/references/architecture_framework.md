# Architecture Decision Framework for ElevenLabs Voice Agents

This document defines the full pipeline from any source to an ElevenLabs agent architecture. It is self-contained; see `edge_failures.md` for the full list of mechanical failure modes, configuration failures, and platform pitfalls.

---

## Pipeline Overview

```
ANY SOURCE (competitor, SOP, docs, transcripts, natural language)
    ↓
Phase 1: PREPARE — source-dependent pre-processing
    ↓
Phase 2: CLASSIFY — tag each piece of content
    ↓
Phase 3: ASSESS — run split-point risk assessment
    ↓
Phase 4: ARCHITECT — assemble node structure from assessment results
    ↓
Phase 5: VALIDATE — post-architecture checklist
```

---

## Phase 1: PREPARE (source-dependent)

The goal is a flat inventory of: all instructions, all tools (with schemas), all data fields, all business rules, all routing logic. How you get there depends on the source.

### Source Type Table

| Source Type                                      | Process                                                                                                                                                                                                                |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Competitor agent** (Retell, Bland, Vapi, etc.) | Flatten: extract all prompts from states/nodes, extract all tools. Distill: deduplicate repeated instructions (guardrails, persona, greeting logic repeated per state). Remove platform-specific transition mechanics. |
| **SOP / documentation**                          | Extract: pull procedures, decision trees, compliance rules. Expand: fill gaps — what fields are collected? what if verification fails? what are the error paths? May need to ask the user clarifying questions.        |
| **Natural language description**                 | Clarify: ask the user to specify data fields, tools, business rules, error handling. Expand: build out the full conversation flow from sparse input.                                                                   |
| **Call transcripts**                             | Pattern-extract: identify recurring conversation phases, data collected, decisions made. Formalize: convert patterns into structured instructions and tool definitions.                                                |

### Flat Content Inventory

All sources converge into a **flat content inventory**:

- Instructional content (persona, tone, guardrails, how-to-behave)
- Data fields to collect (with formats and validation)
- Tools (with schemas, parameters, when to call)
- Business rules (if X then Y, eligibility criteria, routing logic)
- Flow requirements (ordering, gating, specific conversational direction)
- **Communication mode** (telephony-Twilio, telephony-SIP, web widget, WhatsApp) — this constrains tool availability and calibrates the risk assessment

### Communication Mode Constraints Table

Determine the target mode early — it gates which tools and features are available:

| Feature                                | Telephony (Twilio)        | Telephony (SIP)           | Web Widget          |
| -------------------------------------- | ------------------------- | ------------------------- | ------------------- |
| Audio quality                          | `ulaw_8000` (noisy)       | `pcm_48000` (clean)       | `pcm_16000` (clean) |
| DTMF / keypad                          | In-band only              | Out-of-band or in-band    | Not available       |
| Transfer to number                     | Yes                       | Yes                       | Not available       |
| Voicemail detection                    | Yes (outbound)            | Yes (outbound)            | Not available       |
| System vars (caller_id, called_number) | Yes                       | Yes (+ SIP header vars)   | Not available       |
| Client events                          | AUDIO + INTERRUPTION only | AUDIO + INTERRUPTION only | Full set            |

Strip unavailable tools/features during PREPARE. A web agent doesn't need DTMF, transfer_to_number, or voicemail detection — remove them and any instructions that reference them.

### Critical Content Definition

When distilling (competitor) or expanding (SOP/NL), classify content as:

**Critical — must keep:**

- Specific data fields to collect (names, IDs, dates — and their formats)
- Business logic / decision rules (eligibility, routing conditions, pricing)
- Tool invocation triggers (when to call which tool, with what params)
- Hard guardrails / boundaries (scope limits, compliance, what agent must NEVER do)
- Required persona/tone (if the business has specific brand requirements)
- Conversational flow direction (specific ordering the business requires — this is not redundancy, it's intent)

**Non-critical — distill or remove:**

- Repeated instructions across states (keep one copy)
- Verbose examples restating what instructions already say
- Platform-specific transition logic ("when state completes, move to state X")
- Confirmation prompts LLMs do naturally ("repeat back what the caller said")
- Overly prescriptive scripting (condense to tone + key points)
- Defensive workarounds for the source platform's quirks

---

## Phase 2: CLASSIFY

Tag each piece of content from the inventory:

### Content Tagging Table

| Tag               | Meaning                                                                                       | Example                                                              | Architecture Implication                                   |
| ----------------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------- |
| **INSTRUCTIONAL** | How to behave, what to say, persona, tone, guardrails                                         | "Be professional and empathetic"                                     | Stays in prompt; contributes to word count                 |
| **ROUTING**       | If condition X → path A, if condition Y → path B (structurally different subsequent behavior) | `lookup_member` → found vs not_found → different flows               | May need expression edge via tool node                     |
| **GATING**        | Don't do X until Y is confirmed                                                               | "Don't discuss benefits until coverage is verified"                  | Prompt instruction if low-risk; node boundary if high-risk |
| **TOOL-SCOPING**  | Tool X should only be callable during phase Y                                                 | `cancel_appointment` only after explicit user request + verification | Needs node boundary (hard constraint)                      |
| **KB-SCOPING**    | Documents X should only be searchable during phase Y                                          | Product catalog for sales; troubleshooting guide for support         | Candidate split point, but weaker than TOOL-SCOPING (see below) |

Only ROUTING and TOOL-SCOPING tags create strong candidate split points. **KB-SCOPING** is a weaker candidate — RAG retrieval uses embedding similarity with a distance threshold (default 0.6), so for KBs <100 docs with distinct topics, irrelevant chunks are naturally filtered out without node boundaries. Promote KB-SCOPING to a split point only when: (a) the KB is very large (100+ docs) with overlapping topics causing demonstrably noisy retrieval, or (b) the split is already justified by ROUTING or TOOL-SCOPING. INSTRUCTIONAL content stays in prompts. GATING is handled by prompt instructions unless wrong-routing cost is HIGH (then promote to a split point).

---

## Phase 3: ASSESS (Split-Point Risk Assessment)

For each candidate split point, evaluate three dimensions:

### Dimension A — Wrong-routing cost

(What if the LLM handles this with prose and gets it wrong?)

- **LOW**: Slightly out of order, recoverable (asking benefits before confirming coverage; greeting tone slightly off)
- **MEDIUM**: Bad experience but no lasting damage (collecting wrong info; redundant questions)
- **HIGH**: Irreversible action or compliance violation (charging payment; cancelling appointment; HIPAA violation; calling emergency services)

### Dimension B — Failed-transition cost

(What if the edge fails mechanically? See `edge_failures.md` for the full list of mechanical failure modes.)

- **LOW**: Minor pause, agent recovers (chat-based; internal tool; no human waiting)
- **MEDIUM**: Noticeable dead air, conversation continues (inbound call; human can re-prompt)
- **HIGH**: Call drops, agent goes silent, human hangs up (outbound to busy rep; IVR with strict timeouts; telephony where >2s silence = confusion)

### Communication Mode Baseline Shift Table

Communication mode shifts the baseline for Dimension B:

| Mode                           | Baseline Shift           | Why                                                                                       |
| ------------------------------ | ------------------------ | ----------------------------------------------------------------------------------------- |
| Web widget                     | Shift toward LOW         | Clean audio (fewer VAD issues), visual feedback possible, user more patient               |
| Telephony — SIP (pcm_48000)    | MEDIUM                   | Good audio but no visual feedback; silence = confusion                                    |
| Telephony — Twilio (ulaw_8000) | Shift toward HIGH        | Noisy audio → more VAD false positives → higher turn-abandonment risk; no visual feedback |
| Inbound telephony              | Same as channel baseline | Human initiated, slightly more patient                                                    |
| Outbound telephony             | Shift +1 toward HIGH     | Agent called them; silence feels worse; may need to survive IVR/hold                      |

### Dimension C — Routing type

(How deterministic can the routing be?)

- **DATA**: Tool result → tool node → expression edge. Deterministic when tool succeeds. (e.g., `lookup_member` returns status)
- **JUDGMENT**: LLM decides conversational state → LLM edge. Probabilistic + mechanical risk. (e.g., "caller has been authenticated")
- **SCOPING**: Tool/KB availability per node. Binary — tool is either available or not. (e.g., `cancel_appointment` only in cancellation node)

### Decision Matrix

```
ROUTING TYPE = DATA:
    → SPLIT. Use tool node + expression edges.
      Deterministic routing. High reliability.

ROUTING TYPE = SCOPING:
    Wrong-routing cost HIGH → SPLIT. Hard tool/KB scoping is worth transition cost.
    Wrong-routing cost LOW/MEDIUM → DON'T SPLIT. Prompt-level scoping is sufficient.

ROUTING TYPE = JUDGMENT:
    Wrong-routing HIGH + Failed-transition LOW → SPLIT.
        Cost of LLM ignoring prose > transition risk.
    Wrong-routing LOW/MEDIUM + Failed-transition HIGH → DON'T SPLIT.
        Graceful degradation (prose) > catastrophic failure (dead air).
    Both HIGH → SPLIT, but REDESIGN as DATA routing.
        Add a classification tool that returns a categorical result.
        Route via expression edges instead of LLM judgment.
    Both LOW → DON'T SPLIT.
```

### Key Principle: Convert JUDGMENT to DATA

When a split point scores JUDGMENT + HIGH wrong-routing cost, don't accept the LLM edge. Redesign: add a tool (classification webhook, structured LLM tool call) that returns a categorical result, then route via expression edges. Converts the hardest tradeoff into the most reliable pattern.

### Additional Factors (tiebreakers, not primary drivers)

- **Expected conversation length**: Short (<15 turns) favors prose (instructions stay prominent). Long (30+ turns) favors splitting (history dilutes prose instructions, fresh brain gets prominent instructions via recency position).
- **Prompt position effect**: Node's `additional_prompt` is appended at the END of system prompt (most attended position). In single prompt, phase instructions are in the MIDDLE (least attended as history grows).
- **LLM cascade**: Each transition restarts cascade from primary model. If primary is flaky, more transitions = more cascade restarts.
- **Knowledge base scoping**: If a split is already justified, use `additional_knowledge_base` to scope KB docs per node as a bonus. RAG retrieval is filtered by `document_id` per node, the query is LLM-rewritten for clarity, and a 0.6 distance threshold discards irrelevant chunks — so for most KBs, single-node with all docs works fine. See `reference.md` "Knowledge Base (RAG)" for RAG internals and article design.

---

## Phase 4: ARCHITECT

Starting from a single node (the default):

1. **Add a node boundary** at each split point that scored SPLIT
2. **Insert tool nodes** for DATA-driven routing (not override_agent → override_agent with LLM edges)
3. **Use say nodes** (literal) where a deterministic transition message is needed
4. **Merge everything between split points** into single `override_agent` nodes with labeled internal phases
5. **Assign tools** to the narrowest node where they're needed
6. **Choose edge types**:
   - `unconditional` — only for start → first node
   - `expression` — for data-driven routing from tool nodes (PREFERRED for all routing)
   - `result` — for tool-result-based routing
   - `llm` — LAST RESORT, only when routing is inherently judgment-based and the split was justified
7. **Write edge conditions** — crisp, unambiguous, aligned with node prompt instructions
8. **Distribute content**:
   - Base agent prompt: persona, tone, guardrails, dynamic variable definitions (shared across all nodes)
   - Per-node `additional_prompt` (default): phase-specific instructions, tool usage guidance, internal phase labels. Appended to base prompt under `# Specific goal for this portion of the conversation` — lands at end of prompt (high-attention position).
   - Per-node override (`conversation_config.agent.prompt.prompt`): replaces the base prompt entirely. Use only when node needs a fundamentally different interaction mode or base prompt conflicts with node purpose.
   - Keep base prompt lean — it's prepended to every node's instructions

### Node Type Guide Table

| Node Type            | Use When                                           | Speaks?          | Deterministic?         |
| -------------------- | -------------------------------------------------- | ---------------- | ---------------------- |
| `override_agent`     | Conversational phase (LLM drives the interaction)  | Yes (LLM)        | No                     |
| `tool` node          | Need deterministic routing on a tool result        | No               | Yes (expression edges) |
| `say` node (literal) | Need a guaranteed transition message               | Yes (exact text) | Yes                    |
| `say` node (prompt)  | Need LLM-generated message with forced progression | Yes (LLM)        | No                     |
| `start` node         | Entry point only                                   | No               | Routes via edges       |

### LLM Model Selection

Model choices interact with architecture decisions. The framework should recommend models based on the agent's needs, not default to gpt-4o.

#### Available LLM Models (latency and cost from ElevenLabs UI, March 2026)

**ElevenLabs self-hosted:**

- `glm-4.5-air` — ~827ms, ~$0.0158/min — "Great for agentic use cases"
- `qwen3-30b-a3b` — ~203ms, ~$0.0047/min — Ultra low latency
- `gpt-oss-120b` — ~325ms, ~$0.0040/min — OS model from OpenAI (Experimental)

**Google:**

- `gemini-3-pro-preview` — ~3.83s, ~$0.0305/min — Slow but powerful
- `gemini-3-flash-preview` — ~1.38s, ~$0.0076/min
- `gemini-3.1-flash-lite-preview` — ~1.48s, ~$0.0038/min
- `gemini-2.5-flash` — ~1.05s, ~$0.0022/min — Strong balance of speed/quality/cost
- `gemini-2.5-flash-lite` — ~626ms, ~$0.0015/min — Fast + cheap

**OpenAI:**

- `gpt-5` — ~1.23s, ~$0.0198/min
- `gpt-5.1` — ~1.01s, ~$0.0198/min
- `gpt-5.2` — ~843ms, ~$0.0278/min — Newest, fast for its capability
- `gpt-5-mini` — ~907ms, ~$0.0040/min — Good balance
- `gpt-5-nano` — ~750ms, ~$0.0008/min — Cheapest available
- `gpt-4.1` — ~963ms, ~$0.0293/min
- `gpt-4.1-mini` — ~834ms, ~$0.0059/min
- `gpt-4.1-nano` — ~538ms, ~$0.0015/min — Fast + cheap
- `gpt-4o` — ~743ms, ~$0.0366/min — Proven tool calling; parallel tool calls
- `gpt-4o-mini` — ~736ms, ~$0.0022/min
- `gpt-4-turbo` — ~1.68s, ~$0.1435/min — Legacy, expensive
- `gpt-3.5-turbo` — ~551ms, ~$0.0072/min — Fast but limited capability

**Anthropic:**

- `claude-sonnet-4.6` — ~937ms, ~$0.0449/min — Newest Claude
- `claude-sonnet-4.5` — ~1.24s, ~$0.0449/min
- `claude-sonnet-4` — ~1.1s, ~$0.0449/min
- `claude-haiku-4.5` — ~921ms, ~$0.0150/min — Claude's speed option
- `claude-3.7-sonnet` — ~1.11s, ~$0.0449/min
- `claude-3-haiku` — ~590ms, ~$0.0037/min — Fastest Claude, cheap

**Custom:** user's own Chat Completions–compatible endpoint (can't be cascade backup).

#### Capability Tiers Table

Nano/lite models are fast and cheap but have limited capability. ElevenLabs internally uses them for filler generation ("Hhmmmm...yeah." via `qwen3-4b`), demo agents, and test evaluation — NOT as primary conversation models. They struggle with complex tool schemas, multi-step reasoning, and judgment-based decisions.

| Tier          | Models                                                                  | Latency     | Cost             | Use for                                                                               |
| ------------- | ----------------------------------------------------------------------- | ----------- | ---------------- | ------------------------------------------------------------------------------------- |
| **Nano/lite** | `qwen3-30b-a3b`, `gpt-4.1-nano`, `gemini-2.5-flash-lite`, `gpt-5-nano`  | 200-750ms   | <$0.005/min      | Simple single-turn Q&A; cost testing; cascade backup only. NOT for multi-tool agents. |
| **Mini**      | `gpt-4o-mini`, `gpt-4.1-mini`, `gpt-5-mini`, `claude-haiku-4.5`         | 700-920ms   | $0.002-0.015/min | Simple-moderate agents; single-node with few tools; telephony where latency matters.  |
| **Standard**  | `gpt-4o`, `gpt-5.2`, `gpt-4.1`, `gemini-2.5-flash`, `claude-sonnet-4.6` | 740ms-1.05s | $0.002-0.045/min | Multi-node agents; complex tool calling; judgment-based routing. The workhorse tier.  |
| **Pro**       | `gpt-5`, `claude-sonnet-4.5`, `gemini-3-pro-preview`                    | 1.2s+       | $0.02-0.05/min   | Complex reasoning; nuanced judgment; quality over speed.                              |

#### Factor-Based Recommendation Table

| Factor                         | Recommended Tier + Models                                                 | Why                                                                                                 |
| ------------------------------ | ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Telephony (simple agent)       | Mini: `gpt-4o-mini` (736ms), `gpt-4.1-mini` (834ms)                       | Fast enough for telephony; capable enough for basic tool calling.                                   |
| Telephony (complex agent)      | Standard: `gpt-5.2` (843ms), `gpt-4o` (743ms), `gemini-2.5-flash` (1.05s) | Reliable `notify_condition` calls + tool execution. OpenAI supports parallel tool calls.            |
| Multi-node (reliable edges)    | Standard: `gpt-4o`, `gpt-5.2`, `gemini-2.5-flash`                         | Edge reliability depends on tool-calling quality. Never use nano/lite as primary for multi-node.    |
| Single-node long conversations | Standard: `gemini-2.5-flash` (1.05s)                                      | Best context handling for long history; excellent cost/quality.                                     |
| Complex reasoning / judgment   | Standard-Pro: `claude-sonnet-4.6` (937ms), `gpt-5.2` (843ms)              | For nuanced conversational decisions.                                                               |
| Cost-sensitive (simple agents) | Mini: `gpt-4o-mini` ($0.0022/min), `gpt-5-mini` ($0.0040/min)             | Don't go below mini for production agents.                                                          |
| Balanced default               | `gemini-2.5-flash` (~1.05s, ~$0.0022/min)                                 | Fast enough for telephony, capable enough for tools, best cost/quality. Recommended starting point. |

### TTS Selection Guidance Table

| Factor                   | Model                      | Why                                                                                         |
| ------------------------ | -------------------------- | ------------------------------------------------------------------------------------------- |
| Telephony (English)                   | `eleven_flash_v2`          | Ultra-low latency. V3 expressiveness is partially lost at ulaw_8000 anyway. ConvAI default. |
| Telephony (multilingual)              | `eleven_flash_v2_5`        | Ultra-low latency + 32 languages.                                                           |
| Telephony (number-heavy / deception)  | `eleven_v3_conversational` | Prompt-driven normalization (SYSTEM_PROMPT) gives full control over digit pronunciation. Essential when V2's normalizer reads numbers incorrectly (e.g., "fifty" for "15") or when the agent must sound indistinguishable from a human. Accept the latency trade-off. |
| Web (branded/expressive)              | `eleven_v3_conversational` | Full quality at pcm_16000. Expressive_mode + audio_tags for emotional steering.             |
| Web (standard)                        | `eleven_flash_v2_5`        | Good balance of latency and quality.                                                        |
| Multi-node agents                     | Prefer flash models        | Each transition restarts TTS. Lower TTS latency = shorter dead air gap during transitions.  |

#### V3 Audio Tags for Telephony

When using `eleven_v3_conversational` on telephony, audio tag selection matters more than on web:

- **Prefer sound-producing tags** that create natural filler: `um`, `hmm`, `uh`, `ah`, `oh`. These buy the LLM thinking time without dead air and sound human.
- **Include action tags**: `checking`, `confirming`, `considering` — these produce brief vocal expressions that fill space naturally.
- **Avoid silence-producing tags on telephony**: `[pause]`, `[long pause]`, `[slow]` can introduce dead air that triggers the other party to say "hello?" or the IVR to time out. If pacing is needed, use punctuation (commas, em-dashes, ellipses) instead.
- **8-12 tags is the sweet spot** — enough variety for the LLM to express a range of emotions without overwhelming the tag list.

`optimize_streaming_latency` is a V2-only parameter and is ignored by V3. Remove it from V3 configs to avoid confusion.

### Cascade Configuration Table

| Mode                         | cascade_timeout_seconds | Rationale                                                                    |
| ---------------------------- | ----------------------- | ---------------------------------------------------------------------------- |
| Telephony                    | 3s                      | Fast fallback; dead air is unacceptable                                      |
| Web                          | 5-8s                    | More tolerance; quality of primary model matters more                        |
| Complex multi-node telephony | 3s                      | Each transition restarts cascade; fast fallback prevents compounding latency |

Default backup order (`gemini-2.5-flash → gpt-4o → gemini-2.5-flash-lite → claude-sonnet-4-5 → gemini-2.0-flash`) is reasonable for most agents. Override when:

- **HIPAA compliance** excludes providers: GPT models are excluded for some BAAs. Remove them from the cascade and backfill with compliant alternatives. Verify each model's HIPAA status — compliance is provider-level, not model-level.
- **Rate-limit exposure**: If a provider is prone to 429s (e.g., Gemini under high volume), don't place it as the sole backup. The cascade has no retry-with-backoff for 429s — a 429 immediately fails that slot and moves to the next model. A 429 on the last slot causes `CascadeBrainError` ("All LLMs Failed").
- **Cross-provider diversity**: Ensure the cascade spans at least 2 providers. If the primary is Anthropic, include Gemini in the backup (and vice versa). A single-provider cascade is a single point of failure.
- **Cost-efficient primaries**: For agents with predictable, structured tasks (IVR navigation, data collection, form-filling), smaller models (e.g., `claude-haiku-4-5`) are viable primaries — the cascade catches the rare failures. Reserve larger models (`claude-sonnet-4-6`, `claude-sonnet-4-5`) for the backup chain where they handle edge cases that Haiku couldn't.

### Tool Assignment Strategy

`additional_tool_ids` on an `override_agent` node ADDS to the base agent's tool list. You cannot remove a base-level tool from a specific node. See `edge_failures.md` for platform pitfalls around tool accumulation.

- If `cancel_appointment` is on the base agent, EVERY node has it — tool scoping is defeated.
- **When tool scoping matters**: put NO tools on the base agent's `tool_ids`. Use `additional_tool_ids` exclusively per node. Each node gets only the tools it needs.
- **When tool scoping doesn't matter** (single-node agent, or all tools are low-risk): tools can go on the base agent for simplicity.
- System tools (`end_call`, `skip_turn`, `play_keypad_touch_tone`) are typically safe on the base agent since they're low-risk and universally needed.

### Dynamic Variables — Wiring, Defaults, and Limitations

Dynamic variables are conversation-level state that persists across nodes. They're the plumbing for expression edges.

**How expression edge routing works:**

1. Override_agent node collects info from the user via conversation
2. LLM fires `notify_condition` → transitions to a tool node
3. Tool node runs a webhook tool with `assignments` that map response fields to dynamic variables (e.g., `{"dynamic_variable": "member_status", "value_path": "status"}`)
4. Expression edges on the tool node evaluate those variables (e.g., `member_status == "active"` → benefits node; `member_status == "inactive"` → termination node)

**Critical constraints:**

- **All dynamic variables must have defaults** or the agent JSON won't upload. Use empty string `""`, `"unknown"`, or `"pending"` as defaults for variables that will be set by tools at runtime.
- **Variables set at call initiation** (e.g., `{{patient_name}}`, `{{member_id}}`) are populated by the calling system; the generator should define them with placeholder defaults.
- **For SOPs / natural language sources**: the generator won't know what webhook response fields are available. Define the variable names and document the expected schema, but use placeholder webhook URLs and note that the customer must configure the actual endpoints and auth.
- **For competitor conversions**: extract variable names from the source and map them to EL dynamic variables. Source tool schemas often reveal the available response fields.
- **Webhook auth**: the generator won't have the customer's API keys. Use placeholder URLs (e.g., `https://api.example.com/lookup_member`) and document required auth headers. The customer configures these post-generation.

### Language and Multilingual Considerations

Language affects both model and architecture decisions:

- **TTS**: `eleven_flash_v2` is English-only. Multilingual agents must use `eleven_flash_v2_5` (32 languages) or `eleven_v3` / `eleven_v3_conversational`.
- **LLM**: Most major models handle common languages well. For less common languages, test capability. Gemini models tend to have broad language support.
- **ASR**: Language is set in `conversation_config.agent.language`. Ensure it matches the expected caller language.
- **Prompts**: Write prompts in the language the LLM will use (usually English, even for multilingual agents — the LLM follows English instructions and responds in the configured language). If the agent must operate in a specific non-English language, prompts may need to be in that language for better instruction following.
- **Voice normalization**: Digit cadence patterns, spelling conventions, and pronunciation rules are language-specific. English patterns (NPI as 3-3-4 groups) don't apply to other languages.

### first_message Strategy Table

The first message is what the agent says when the conversation starts (before any user input).

| Scenario               | first_message guidance                                                                                                                              |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Inbound telephony**  | Brief greeting + purpose. "Thank you for calling [company], how can I help you?" Agent speaks first since the caller expects it.                    |
| **Outbound telephony** | Identify self + reason for call. "Hi, this is [name] calling from [company] regarding your [topic]." Must be concise — human may talk over.         |
| **Web widget**         | Welcoming + prompt engagement. "Hi there! I'm here to help with [topic]. What can I do for you?" Can be slightly longer since user sees it as text. |
| **No first_message**   | Agent waits for user to speak first. Unusual but valid for some inbound scenarios where the caller is expected to state their need.                 |

For outbound telephony agents, the first_message is especially critical — it's the only guaranteed utterance before the human (or IVR) responds. Keep it under 2 sentences.

### Prompt Engineering Patterns

The architecture framework defines WHEN to split. These patterns define HOW to write prompts within nodes:

#### Internal Phase Labels

For single-node agents with multiple phases:

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

Each phase should have a clear heading. Completion criteria between phases should be specific and unambiguous (e.g., "both name and DOB confirmed" not "authentication complete"). The LLM tracks which phase it's in from conversation history — there's no explicit state variable.

#### Hold/Silence Handling (telephony-specific)

The agent cannot detect hold music from audio characteristics. VAD treats music the same as speech (high VAD scores), and there is no hold-music classifier. The LLM only sees the raw ASR transcript — no confidence score, no audio-type metadata. Hold music typically produces garbled, meaningless, or repetitive transcript text.

- If the transcript appears to be noise, hold music, or automated messages (garbled, meaningless, or obviously non-human text): call `skip_turn` and wait silently. Do not say "hello" or attempt to speak until the transcript clearly shows a human speaking.
- `skip_turn` is the correct tool for holds because it disables both `turn_timeout` (agent re-engagement) and `silence_end_call_timeout` (platform auto-disconnect) for that turn. Without `skip_turn`, those timers remain active and can cause unwanted behavior during holds.
- Never `end_call` because of hold/silence — holds are normal in telephony.
- Anti-narration: never verbalize internal actions ("I need to wait," "Let me look that up," "I should ask about..."). Either act silently or speak directly to the other party. Everything the agent says is spoken aloud — there is no internal monologue.
- **Platform setting to watch:** `silence_end_call_timeout` (default `-1` = disabled, range 10–7200s). If enabled by the agent builder, extended silence WILL disconnect the call unless `skip_turn` is keeping the turn suppressed. For agents that may be placed on hold, either disable this setting or ensure the prompt reliably calls `skip_turn` during holds.

#### Voice Normalization (telephony-specific — adapt to agent's domain)

For `eleven_v3_conversational`, the TTS normalizer pipeline does not apply — number normalization is entirely prompt-driven via `TextNormalisationType.SYSTEM_PROMPT`. For V2 models (`eleven_flash_v2`, `eleven_flash_v2_5`), the platform's TTS normalizer can handle numbers automatically when `TextNormalisationType.ELEVENLABS` is set. Regardless of model, explicit prompt instructions give the most reliable control.

- Long digit sequences (account numbers, IDs, phone numbers): instruct the LLM to write digits with grouping and punctuation. Break into groups of 3-4 with pauses between groups. Read digit-by-digit, not as whole numbers.
- Alphanumeric codes: spell character by character with pauses. Never use the NATO alphabet unless the domain specifically requires it.
- All numeric data: pace deliberately, at normal speaking volume. Never rush or whisper digits.
- Match the cadence convention the human expects for that data type (e.g., phone numbers are typically 3-3-4; credit card numbers are 4-4-4-4; SSNs are 3-2-4).
- **Pacing mechanisms by reliability:** SSML `<break time="Xs"/>` tags work for both V2 and V3 and are the most reliable way to insert pauses. Plain punctuation (commas, em-dashes, ellipses) is interpreted natively by the TTS model — effective but less predictable. V3 audio tags like `[slow]` can influence pacing. The agent-level `speed` parameter (0.7–1.2) is a global lever.
- **Volume:** There is no TTS-level volume control. "Never whisper" is purely prompt-driven and depends on the TTS model's interpretation of the text. Providing explicit examples of desired output in the prompt (e.g., "Say: one, two, three — four, five, six") is the most reliable approach.
- **Dashes and special characters in IDs:** Instruct the LLM to say "dash" or "hyphen" as a word (e.g., CH-50001 → "C H dash five zero zero zero one"). Without this, LLMs may output HTML `<br>` tags, SSML markup, or other notation that V3 TTS reads literally ("br br br br").
- **Anti-markup rule (V3 critical):** V3 TTS reads everything aloud — including HTML tags, SSML tags, and markdown formatting. Add to every V3 agent prompt: "Never output HTML tags, SSML tags, markdown, or any markup. Only output words to be spoken."
- **Data type precedence:** When prompts include both a specific data-type reading table AND general rules (e.g., "spell each character"), the general rule must explicitly defer to the table. Without this, LLMs will spell "BIN" as "B-I-N" instead of saying "bin" as a word. Pattern: "spell each character slowly with pauses, UNLESS the data type table above says otherwise."
- **Correction handling:** LLMs tend to repeat the same correction phrase ("Thank you for that correction") robotically. Add varied correction acknowledgments to the persona section: "Oh, got it," "Sorry about that," "Okay, let me fix that." Explicitly ban corporate correction phrases.

#### Garbled STT Handling (telephony-specific)

The LLM receives only the raw transcript string — no confidence score, no audio quality metadata. ASR confidence (`avg_prob`) is computed internally and used for turn-taking decisions, but is never surfaced to the LLM. Garbled audio still produces text (Whisper has hallucination detection but will still output something). For telephony (ULAW_8000), VAD thresholds are lower (0.5 vs 0.7–0.78 for wideband), meaning more audio passes as "speech" — telephony agents will encounter more garbled transcripts than web agents.

- If the transcript text looks like noise or nonsense (meaningless words, repeated fragments, obviously non-human content): call `skip_turn` rather than saying "I didn't understand." The garbled text is likely background noise, hold music, IVR prompts, or line noise — not speech directed at the agent.
- If several consecutive turns produce garbled text, then politely ask the other party to repeat.
- Don't assume garbled transcript text is the other party speaking — consider the context (was the agent just placed on hold? Is there an IVR playing?).
- **Timeout placeholder:** When the user says nothing during a turn timeout, the platform injects `"..."` as the transcript. The system prompt automatically explains this to the LLM. This is distinct from garbled text — `"..."` means silence, not noise.

### IVR Handling

IVR does NOT automatically warrant a separate node:

- `suppress_turn_after_dtmf` (tool-level) handles silence after DTMF globally
- `skip_turn` handles hold/silence/garbled-STT globally
- Per-node turn config is fragile (UI clobbers API-set values)
- Default: handle IVR via prompt-level internal phases
- Split only when IVR instructions are complex enough to bloat combined prompt past threshold

#### DTMF Patterns (telephony-specific)

The `play_keypad_touch_tone` tool takes a single `dtmf_tones` string — all digits in one call. Valid characters: `0-9`, `*`, `#`, `w` (0.5s pause), `W` (1.0s pause). The tool description, prompt instructions, and IVR table must all say the same thing with no hedging — conflicting signals (e.g., tool says "if needed," prompt says "always") cause the LLM to skip pauses and blast digits.

**Pacing with `w` pauses:** IVRs often fail to decode rapid-fire digit streams. Insert `w` between groups of 2-4 digits. Match the cadence to the data type:

| Data type | Pattern | Example |
|-----------|---------|---------|
| NPI (10 digits) | 3w3w4 | `123w456w7890` |
| DOB (MMDDYYYY) | 2w2w4 | `01w15w1985` |
| Phone (10 digits) | 3w3w4 | `555w123w4567` |
| ZIP (5 digits) | No pauses needed | `10001` |
| Single menu press | No pauses | `2` |

**Critical prompt rules for DTMF:**
- "Send ALL digits in a single call as one string" — never one digit per tool call (10 LLM cycles vs 1)
- "Always insert w between groups" — not "if needed" (LLMs will skip optional pauses)
- "Never call this tool one digit at a time" — explicit prohibition
- "Always use `play_keypad_touch_tone` to navigate IVRs — never speak a number aloud to an automated system" — DTMF is always more reliable than voice for IVR navigation

**Tool config:**
- `suppress_turn_after_dtmf: true` — agent stays silent after pressing, letting the IVR respond
- `disable_interruptions: true` — prevents VAD from cutting off tones mid-play
- `use_out_of_band_dtmf: false` for Twilio (in-band only; out-of-band flag is ignored for Twilio calls)
- `force_pre_tool_speech: false` — agent should NOT narrate before pressing

**Testing note:** In-band DTMF works through the PSTN to real IVRs but is NOT detected by Twilio's `<Gather>` verb (which listens for out-of-band RFC 2833 events). Local TwiML test apps won't pick up DTMF. Test against real IVRs.

#### Anti-Narration (telephony-specific)

Everything the agent says is spoken aloud. There is no internal monologue. The anti-narration guardrail must cover:

- Internal state: "I need to wait," "Let me look that up," "I should ask about..."
- Tool announcements: "I'll press two," "Let me enter the NPI," "I'm going to dial..."
- Action narration: "I'm calling to verify," "Now I'll ask about the BIN..."

Add to every telephony agent's guardrails:
```
- Never narrate or announce what you are about to do. Do not say "I'll press,"
  "Let me enter," "I'm going to dial," or anything similar. Just call the tool
  silently. Everything you say is spoken aloud on the call.
```

#### ASR Keyword Guidance (telephony-specific)

ASR keywords boost recognition for domain-specific terms the model wouldn't normally expect. Use them for:

- **Industry acronyms and jargon**: BIN, PCN, NPI, PBM, EOB, formulary, prior auth
- **Proper nouns**: payer names, PBM names, drug names, company names
- **Confusable number pairs**: fifteen/fifty, thirteen/thirty, fourteen/forty, sixteen/sixty, oh/zero — these are commonly misheard on telephony audio (ulaw 8kHz)

Do NOT add basic vocabulary (common words, single letters A-Z, digits one-nine) — these are already in the ASR's core model and keyword boosting won't help.

---

## Phase 5: VALIDATE

Post-architecture checklist:

- Every edge condition is specific and unambiguous (not "authentication complete" but "member ID and DOB both confirmed")
- No overlapping edge conditions from the same node
- Every node prompt aligns with its outgoing edge conditions (prompt says what to collect; edge fires when collected)
- Edge conditions don't fight the prompt (no "always confirm before proceeding" + meta-prompt "don't ask for confirmation")
- Every reachable conversation state has an exit path (including error/refusal/not-found scenarios)
- No node prompt exceeds ~2000 words (including base prompt contribution)
- No node has more than ~8-10 tools
- High-risk tools (booking, cancellation, payment, emergency) are scoped to the node where they're needed
- `unconditional` edges only for start → first node; `expression` edges for data routing; `llm` edges only where unavoidable
- JUDGMENT-type LLM edges have been converted to DATA-type where possible
- Tool nodes used for deterministic routing (not override_agent → override_agent with LLM edges for data-driven forks)
- No tool node or say node is doing work that could be handled in the adjacent override_agent prompt
- Tool descriptions and prompt instructions agree — no hedging ("if needed") in one that contradicts obligation ("always") in the other. Conflicting signals cause the LLM to unpredictably follow either.
- Dynamic variable placeholder defaults match expected data formats and lengths (a 10-digit NPI field needs a 10-digit placeholder, not 9 — tests and formatting rules break silently on wrong-length data)

---

## Split-Point Assessment Output Format

The analysis phase should produce this for each candidate, which the generator consumes:

```
## Split Point Assessment

### SP1: [description]
- Signal: [what triggers this potential split]
- Routing type: DATA | JUDGMENT | SCOPING
- Wrong-routing cost: LOW | MEDIUM | HIGH — [why]
- Failed-transition cost: LOW | MEDIUM | HIGH — [why]
- Decision: SPLIT | DON'T SPLIT
- If SPLIT: implementation pattern (tool node + expression, override_agent + LLM edge, etc.)
- If DON'T SPLIT: how to handle in prose (internal phase label, gating instruction, etc.)
```

---

## Reference Examples

Assessed column uses the split-point risk assessment. OA = override_agent, TN = tool node.

| Agent             | States  | Faithful | Assessed            | Mode               | Rationale                                                                                                                                                                                                  |
| ----------------- | ------- | -------- | ------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tandem            | 5       | 5        | **1 OA**            | Outbound Twilio    | Zero candidates score SPLIT: no data forks, no dangerous tools (end_call/skip_turn/DTMF are low-risk), short calls (~10 turns). Outbound Twilio shifts failed-transition to HIGH, reinforcing single node. |
| Scheduling        | 7       | 7        | **1-2 OA**          | Inbound telephony  | `create_event` is medium-risk. Success/failure doesn't need different paths (confirm or retry). Borderline SCOPING; single node with prompt gating likely sufficient.                                      |
| VCP Survey        | 52      | 52       | **4-6 OA**          | Outbound telephony | Zero routing forks, zero dangerous tools. All splits from prompt size (~4800 words distills to ~2400; exceeds threshold). Group by survey section. Outbound telephony = conservative on node count.        |
| Condor-Rohan      | 66      | 66       | **4 OA + 1-2 TN**   | Inbound telephony  | 3 intent forks with dangerous tools (book_job, cancel, emergency). JUDGMENT + HIGH wrong-routing → REDESIGN as DATA: classify_intent tool node → expression edges. TOOL-SCOPING per intent cluster.        |
| SAMPLE_ELECTRICAL | 64      | 64       | **4-5 OA + 1-2 TN** | Inbound telephony  | Same pattern as Condor-Rohan. Intent classification tool node. Dangerous tools scoped per cluster.                                                                                                         |
| Onboarding        | 41      | 41       | **5-7 OA**          | Web widget         | Section grouping; multiple distinct tool sets. Web = LOW failed-transition baseline, so more splits are tolerable. KB-SCOPING drives some.                                                                 |
| Caribou Carrie    | complex | 13       | **5-7 OA + 2-3 TN** | Inbound telephony  | HIGH-risk tools (SSN, credit check). DATA forks on app status, vehicle lookup. Tool nodes for deterministic routing at each major gate.                                                                    |

---

## Testing and Iteration Strategy

### Post-Generation Checklist

- Does the agent upload successfully? (Dynamic variable defaults, valid JSON schema)
- Does the first_message play correctly?
- For each node: does the agent follow the prompt's phase instructions?
- For each edge: does the transition fire at the right time? Does it NOT fire prematurely?
- For each tool: does the agent call it with correct parameters?
- For each tool node: does expression edge routing work for all expected results (including error/not-found)?
- For telephony: is dead air acceptable during transitions?

### Diagnosing Issues in Production

- Agent stays in one node too long → prompt or edge condition problem (configuration failure; see `edge_failures.md`)
- Agent transitions too early → greedy edge firing (meta-prompt eagerness)
- Dead air during transitions → brain reconstruction latency (mechanical) or cascade restart (mechanical)
- Agent repeats questions after transition → history confusion (mechanical)
- Agent calls wrong tool → tool scoping issue (use node boundary) or prompt ambiguity
- Agent says "I need to wait" / narrates actions → missing anti-narration guardrail in prompt

### Iteration Approach

- Analyze first, patch second. Don't regenerate the full JSON — iterate via targeted edits.
- Prompt changes are safe (no structural risk). Edge condition rewording is medium-risk. Adding/removing nodes is high-risk (test thoroughly).
- When moving from multi-node to fewer nodes: migrate incrementally (merge two adjacent nodes, test, then merge the next pair).
