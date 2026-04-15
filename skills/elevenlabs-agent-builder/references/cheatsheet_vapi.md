# Vapi → ElevenLabs Migration Cheat Sheet

Quick reference for migrating Vapi voice assistants to ElevenLabs.

---

## Quick Vocabulary

| Vapi | ElevenLabs | Notes |
|------|------------|-------|
| Assistant | Agent | Same concept |
| Squad | Agent with Workflow | One agent, multiple subagent nodes |
| Squad Member | Subagent Node | Each member becomes a node in the workflow |
| Handoff | Edge (transition) | Routing between nodes via conditions |
| Transfer to Phone | Transfer Tool | System tool with phone numbers |
| Code Tool | Server Tool | You host the code, ElevenLabs calls it |
| System Prompt | Prompt | Direct mapping |
| First Message | First Message | Direct mapping |

---

## The Big Gotchas

### 1. Code Tools → Server Tools (You Host)
Vapi runs your TypeScript on their servers. ElevenLabs calls YOUR server instead.

**What to do**: Host your code somewhere (Vercel, AWS, etc.) and point ElevenLabs to it. Same functionality, different hosting.

### 2. Squads Become One Agent with a Workflow
Don't create separate agents for each squad member. Instead:
- Create ONE agent
- Add a workflow with multiple "subagent" nodes
- Each node handles one squad member's role
- Edges control routing between them

### 3. One Edge Per Node Pair
In the workflow builder, you can only have ONE connection between any two nodes. If you need traffic both ways (A↔B), use:
- **Forward condition**: When to go A → B
- **Backward condition**: When to go B → A

Creating two separate edges will cause an error.

### 4. Terminal Nodes = Call Ends Immediately
Phone Transfer, End Call, and Agent Transfer NODES are final. Once the call hits them:
- Call ends or transfers
- No retry possible
- No fallback

**If you need retry/fallback**: Use the Transfer TOOL instead of the Transfer NODE. Tools return control to the agent if they fail.

### 5. Use Tools for Transfers (Not Nodes)
| Approach | What Happens on Failure |
|----------|------------------------|
| Transfer **Node** | Call ends. Done. |
| Transfer **Tool** | Returns to agent, can retry or apologize |

Always prefer tools unless you're okay with the call ending on failure.

### 6. No Self-Loop Edges
An edge can't connect a node back to itself. If you need "keep doing this until X", put that logic in the node's prompt instead.

---

## Migration At a Glance

| Vapi Setup | What to Build in ElevenLabs |
|------------|----------------------------|
| Simple Assistant | Single agent (no workflow needed) |
| Assistant + Tools | Agent with tools configured |
| Assistant + Code Tools | Host code externally → add as server tool |
| Squad (2-5 members) | One agent with workflow containing subagent nodes |

---

## Squad → Workflow Mapping

```
Vapi Squad                      ElevenLabs Agent + Workflow
─────────────────────────────────────────────────────────────
Squad Name                  →   Agent Name
Member 1 (Reception)        →   Subagent Node: "Reception"
Member 2 (Support)          →   Subagent Node: "Support"
Member 3 (Billing)          →   Subagent Node: "Billing"

Handoff: Reception→Support  →   Edge with condition: "needs tech help"
Handoff: Support→Reception  →   Same edge, backward condition: "has other questions"
```

**Why one agent?** Shared conversation context, simpler setup, single deployment.

---

## Tool Types

| Vapi Tool | ElevenLabs Equivalent |
|-----------|----------------------|
| Webhook/Function | Server Tool (webhook) |
| Code (TypeScript) | Server Tool (you host the code) |
| Transfer to Number | Transfer to Number (system tool) |
| Transfer to Assistant | Use workflow edges instead |
| End Call | End Call (system tool) |

---

## Workflow Building Tips

### Start Node
Every workflow needs a start node. It connects to your first real node (usually a router/reception).

### Subagent Nodes
Each subagent node has:
- **Label**: Display name (e.g., "Technical Support")
- **Additional Prompt**: Instructions specific to this node's role

### Edge Conditions
Edges can trigger on:
- **LLM Condition**: Natural language (e.g., "customer asks about billing")
- **Unconditional**: Always proceed
- **Expression**: Variable-based logic

### Common Pattern: Router + Specialists
```
[Start] → [Router] → [Support]
                  → [Billing]
                  → [Sales]
                  
Router determines intent, edges route to specialists.
Specialists can route back to Router via backward conditions.
```

---

## Voice & Model Notes

**Voices**: Only ElevenLabs voices map directly.

**TTS Models**:
- English only: Use Turbo v2 or Flash v2
- Multilingual: Use Turbo v2.5 or Flash v2.5

---

## Quick Checklist

**Simple Assistant:**
- [ ] Create agent in ElevenLabs
- [ ] Copy over system prompt
- [ ] Configure voice
- [ ] Add any server tools needed

**Squad:**
- [ ] Create ONE agent with a workflow
- [ ] Add subagent node for each squad member
- [ ] Create edges with conditions matching your handoff logic
- [ ] Remember: one edge per node pair (use backward conditions)
- [ ] Add Transfer to Number tool for human escalation
- [ ] Add End Call tool
- [ ] Test all routing paths

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Creating separate agents for squad members | Use one agent with workflow subagent nodes |
| Two edges between same nodes | Use one edge with forward + backward conditions |
| Using Transfer Node when you need retry | Use Transfer Tool instead |
| Edge from node to itself | Put looping logic in the node's prompt |
| Expecting fallback after terminal node | Terminal = call ends. Use tools for fallback. |

