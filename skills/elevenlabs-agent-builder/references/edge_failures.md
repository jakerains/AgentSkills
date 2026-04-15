# Edge Failure Modes Reference

Comprehensive reference on why workflow edges fail in ElevenLabs Conversational AI, grounded in the platform's source code. Every edge added to an agent multiplies the failure surface — both mechanical and configuration failures can compound.

---

## Mechanical Failures (Runtime)

These happen regardless of how well the agent is configured.

### 1. LLM Never Calls the Tool

The most common failure. Each outgoing edge from an `override_agent` node is exposed to the LLM as a `notify_condition_X_met` tool. If the LLM doesn't recognize the condition is met, it never calls the tool, and the transition never fires. The agent stays stuck in the current node.

**Why it happens:**
- The LLM is generating conversational text and doesn't pause to evaluate tool-calling conditions
- Long conversation history pushes the edge's meta-prompt description out of the LLM's attention window
- The condition description doesn't match how the conversation actually unfolded

### 2. Turn Abandoned by VAD

Voice Activity Detection (VAD) can trigger a turn commitment before the LLM's `notify_condition` tool call is processed by `maybe_add_tool_request()`. The tool call is silently dropped — the LLM "decided" to transition, but the platform never received the instruction.

**Why it happens:**
- User speech triggers VAD while the LLM is still generating its response + tool call
- More common in telephony (ULAW_8000) where VAD thresholds are lower (0.5 vs 0.7-0.78 for wideband)
- Interruption handling cuts off generation before tool calls are extracted

### 3. Malformed JSON Parameters

The LLM produces invalid JSON for the `notify_condition` tool call. The platform falls back to empty parameters, which means no condition values match any edge — the transition silently fails.

**Why it happens:**
- Complex nested tool schemas increase the chance of malformed output
- Lower-capability LLMs (nano/lite tier) are more prone to JSON formatting errors
- Long context windows degrade structured output quality

### 4. Brain Reconstruction Latency

Each `override_agent` transition involves a full LLM brain lifecycle:
1. Current brain terminated (`BrainTerminationReason.AGENT_TRANSFER`)
2. Brain cleanup runs
3. New brain constructed for target node
4. Async post-initialization completes

This gap causes dead air. There is no single metric that covers the full duration — it spans multiple async operations. The user hears silence during reconstruction.

### 5. Mid-Sentence Transition

The LLM fires `notify_condition` while still generating conversational text. `break_generation=True` immediately cuts off the response. The user hears a half-sentence, then silence during brain reconstruction, then the new node speaks.

**Example:** "Great, I've confirmed your coverage and your benefits include—" [cut off] [silence] [new node] "Now let me collect your pharmacy information."

### 6. History Confusion

When transitioning between nodes, `transfer_to_agent` tool calls are stripped from the conversation history (via `chat_history_llm_view`). The new brain sees the full conversation but "thinks" it was the one having it. This can cause:
- Hallucinated context ("As I mentioned earlier..." when it didn't)
- Repeated questions the previous node already asked
- Confusion about what's been collected vs what hasn't

### 7. Subagent Loop Prevention

`_is_stuck_in_a_loop()` tracks recent node visits. If it detects a loop pattern, it disables the `notify_condition` tool entirely — preventing the transition. This blocks legitimate revisits (e.g., returning to a router node after handling one intent to handle another).

**Controlled by:** `prevent_subagent_loops: true` in the workflow config.

### 8. Max Iterations Exceeded

The orchestrator caps response generation iterations at 100. If a nested tool-calling loop exceeds 10 iterations, it sets `is_error` on the tool result. In extreme cases, the agent gets stuck in a loop calling tools without making progress.

### 9. LLM Cascade Restart

Each node transition constructs a fresh brain, which starts the LLM cascade from the primary model. If the primary model was timing out (triggering cascade fallback), the new node re-experiences the timeout before falling back — compounding latency across transitions.

**How cascade works:** Primary model → timeout after `cascade_timeout_seconds` → backup model 1 → backup model 2 → etc. Default backup order: `gemini-2.5-flash → gpt-4o → gemini-2.5-flash-lite → claude-sonnet-4-5 → gemini-2.0-flash`.

---

## Configuration Failures (Agent Design)

These are caused by how the agent's prompts, edges, and tools are configured.

### 1. Vague Edge Conditions

Ambiguous descriptions force the LLM to guess whether the condition is met. Combined with the meta-prompt's instruction ("You don't need to be certain that a condition is met"), vague conditions lead to premature or missed transitions.

**Bad:** "Customer is ready to proceed"
**Good:** "'client_lookup' tool returned a matching record AND caller verbally confirmed their name"

### 2. Overlapping Edge Conditions

Multiple outgoing edges from the same node with similar descriptions. The LLM may fire the wrong one or fire both simultaneously (some models support parallel tool calls).

**Example:** Node has edges for "Caller wants to schedule" and "Caller wants to book an appointment" — these are the same intent with different wording.

### 3. Prompt/Edge Mismatch

The node's prompt instructs the agent to do something that conflicts with or doesn't align with the outgoing edge conditions. The prompt says "collect A, B, and C" but the edge fires on "A is collected" — the agent transitions before finishing.

### 4. Missing Exit Paths

No edge for scenarios that naturally arise. The agent reaches a conversational state where it should transition but has no matching edge. Common with error/not-found/refusal scenarios.

### 5. Prompt Too Long

Edge meta-prompts (the `notify_condition` tool descriptions) are buried in a long context. The LLM attends to the start and end of long prompts but skims the middle — "lost in the middle" effect. Edge conditions in the middle of a complex tool schema get less attention.

### 6. Edge Condition Fights Prompt

The node prompt says "always confirm before proceeding" but the meta-prompt's instruction encourages the LLM to fire transitions speculatively. The prompt and edge work against each other.

### 7. Dynamic Variable Dependencies

Expression edges reference dynamic variables that haven't been set yet. If a variable has no value (or its default), the expression evaluates to an unexpected result — the edge stays `AUTO` or goes `DISABLED`.

### 8. Wrong Edge Type

Misusing edge types:
- `unconditional` where `llm` was needed (agent always transitions, ignoring conditions)
- `llm` where `expression` was possible (introducing LLM judgment where data-driven routing would be deterministic)
- `result` on a non-tool node (type mismatch)

### 9. Greedy Transition Firing

The meta-prompt tells the LLM: "You don't need to be certain that a condition is met. If you think it might be, call the tool." Combined with eager edge conditions and no debouncing/cooldown mechanism, the LLM fires transitions too early — before the conversation has actually reached the trigger point.

---

## Platform Pitfalls

### 1. UI Clobbers API-Only Fields

Per-node `turn_timeout` overrides can be set via the API but are NOT exposed in the ElevenLabs dashboard UI. Saving the agent from the dashboard strips these API-set values, reverting to the global default. Any agent relying on per-node turn config must be deployed and maintained exclusively via API.

### 2. `suppress_turn_after_dtmf` Is Global

The `suppress_turn_after_dtmf` parameter on the `play_keypad_touch_tone` tool is tool-level, not per-node. It works regardless of architecture — no need to split into a separate node just for DTMF handling.

### 3. Tools Accumulate

`additional_tool_ids` on an `override_agent` node ADDS to the base agent's `tool_ids` list. You cannot remove a base-level tool from a specific node. If tool scoping is needed, put NO tools on the base agent and use `additional_tool_ids` exclusively per node.

### 4. `silence_end_call_timeout` Interaction

When `skip_turn` is active (turn is suppressed), both `turn_timeout` and `silence_end_call_timeout` are disabled for that turn. However, if `silence_end_call_timeout` is enabled (range 10-7200s, default -1 = disabled) and the agent is NOT calling `skip_turn` during a hold, extended silence WILL disconnect the call. Agents that may be placed on hold must either disable this setting or reliably call `skip_turn`.

---

## Compounding Effect

Each edge is a surface where both categories stack. A moderately vague condition (configuration) + VAD turn-abandonment (mechanical) + mid-sentence firing (mechanical) can compound into a complete conversation failure. Every edge added multiplies the failure surface.

**Implication for architecture:** The default should be the minimum number of nodes. Only add edges when the value of the split (tool scoping, deterministic routing, prompt size management) clearly exceeds the compounded failure risk.
