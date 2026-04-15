# Retell → ElevenLabs Migration Cheat Sheet

A practical guide for Retell Conversation Flow users moving to ElevenLabs Conversational AI.

---

## Quick Vocabulary Translation

| Retell Conversation Flow | ElevenLabs Equivalent | Notes |
|--------------------------|----------------------|-------|
| Agent | Agent | Same concept! |
| Conversation Node | Agent Node | Where the AI talks to callers |
| Node Prompt | Additional Prompt | Instructions specific to that node |
| Transfer Call Node | Phone Transfer Node | Routes to human agents |
| Branch Node | Edge Conditions | Routing logic moves to edges in ElevenLabs |
| End Node | End Node | Same concept - terminates the call |
| Edge | Edge | Connections between nodes |
| Edge Description | Edge Condition | What triggers the transition |
| Begin Message | First Message | What the agent says when call starts |
| Tools | Tools | Webhooks, transfers, etc. |
| Cold Transfer | Blind Transfer | Transfer without introduction |
| Warm Transfer | Conference Transfer | Agent stays until connected |
| Global Node | System Tool + Prompt | Handled via tools instead of special nodes |
| Variable Extractor | Data Collection | Captures info from conversation for logs/webhooks |

---

## Your Workflow Canvas: Side by Side

### In Retell Conversation Flow
You're used to a visual canvas with:
- Conversation nodes (where the AI talks)
- Transfer Call nodes (routes to humans)
- Branch nodes (for conditional routing)
- End nodes (terminates call)
- Edges with descriptions that the AI evaluates

### In ElevenLabs
Very similar visual experience! You get:
- **Start Node** - Where every call begins (auto-created)
- **Agent Nodes** - Like your Conversation nodes
- **Phone Transfer Nodes** - Like your Transfer Call nodes
- **End Nodes** - Same as Retell

**What's Different?**
- No separate "Branch" nodes - routing conditions live on the edges themselves
- ElevenLabs uses a single edge to handle *both directions* between two nodes (more below)
- "Global" behaviors use tools + prompts instead of special nodes

---

## Visual Example: Before & After

### Your Retell Conversation Flow
```
[Start] → [Greeting] → [Branch: What do you need?]
                              ├── "billing" → [Billing Node] → [Transfer: Billing Dept]
                              ├── "support" → [Support Node] → [Transfer: Support Dept]
                              └── "else" → [General Help] → [End]
```

### Same Flow in ElevenLabs
```
[Start] → [Greeting] ──"billing question"──→ [Billing Handler] → [Phone Transfer: Billing]
              │
              ├──"support question"──→ [Support Handler] → [Phone Transfer: Support]
              │
              └──"other/unclear"──→ [General Help] → [End]
```

**What changed:**
- The Branch node disappeared - its conditions moved to the edges
- Greeting now has 3 outgoing edges, each with its own condition
- Everything else maps over directly!

---

## The Big "Gotchas" (Read This First!)

### 1. One Edge Per Pair of Nodes

**In Retell Conversation Flow**: You might draw two separate edges - one from Router → Billing, and another from Billing → Router.

**In ElevenLabs**: These must be ONE edge with two conditions:
- **Forward condition**: "When caller asks about billing" (Router → Billing)
- **Backward condition**: "When billing issue is resolved or caller has other questions" (Billing → Router)

💡 **Think of it as**: One road between two cities that handles traffic in both directions.

### 2. Transfer and End Nodes Are "Dead Ends"

Once you route to a Phone Transfer or End node, you can't have edges going *out* of them. The call either transfers or ends - there's no coming back in the workflow.

**What if the transfer fails?** Put retry instructions in the *previous* node's prompt:
> "Transfer the caller to billing. If the transfer fails, apologize and offer to take a message or try an alternate number."

### 3. No Looping Back to Yourself

You can't have an edge that goes from a node back to itself. 

**In Retell Conversation Flow**: You might have an edge that loops a node back to itself for handling multiple questions.

**In ElevenLabs**: Put that looping behavior in the node's prompt instead:
> "Continue answering the caller's questions about hours, location, and services. When they indicate they're done, the conversation can move on."

---

## Building Your First Workflow

### Step 1: Create Your Agent
1. Go to **Conversational AI** in your ElevenLabs dashboard
2. Click **Create Agent**
3. Set up your agent's:
   - **First Message** (your greeting)
   - **System Prompt** (personality and instructions)
   - **Voice** (pick from the voice library)

### Step 2: Add Workflow Nodes
1. Open the **Workflow** tab
2. You'll see a Start node already there
3. Add nodes by clicking the **+** button:
   - **Agent Node**: For conversation handling (most common)
   - **Phone Transfer**: To route to human agents
   - **End Call**: To terminate the conversation

### Step 3: Connect Your Nodes
1. Drag from one node to another to create an edge
2. Click the edge to set conditions:
   - **LLM Condition**: Natural language (like Retell!) - "When caller asks about billing"
   - **Unconditional**: Always proceeds (for auto-advance scenarios)

### Step 4: Write Node Prompts
Click on any Agent Node to add an **Additional Prompt** - specific instructions for what the agent should do in that step.

---

## Migrating Common Patterns

### Pattern 1: Simple Intent Router

**Retell Conversation Flow**: 
- Greeting node → Branch node (routes by intent) → Department conversation nodes

**ElevenLabs**:
```
[Start] → [Greeting] → [Billing Handler]
                   → [Support Handler]  
                   → [Sales Handler]
```

The Branch node goes away - its logic moves to the **edge conditions**:
- "Caller asking about billing, payments, or invoices"
- "Caller asking for technical help or support"
- "Caller interested in purchasing or upgrades"

💡 **Key insight**: In ElevenLabs, you don't need a separate router node. Just add multiple edges from your Greeting node, each with its own condition.

### Pattern 2: Transfer to Human

**Retell Conversation Flow**: Transfer Call node with phone number and transfer type

**ElevenLabs**: Two options:

**Option A - Phone Transfer Node** (simple, no fallback):
- Add a Phone Transfer node
- Set the phone number and transfer type (blind or conference)
- Connect with an edge

**Option B - Transfer Tool** (recommended, has fallback):
- Add a `transfer_to_number` system tool in your agent settings
- Reference it in your prompts: "When caller needs human help, use the transfer tool"
- If transfer fails, the agent can respond and try again

💡 **Recommendation**: Use the transfer tool unless you have a final "fire and forget" transfer. It gives you error handling that you'd otherwise lose.

### Pattern 3: Conversation Node with Multiple Back-and-Forths

**Retell Conversation Flow**: A conversation node that handles multiple exchanges before moving on (maybe with a self-loop edge)

**ElevenLabs**:
- Create an Agent Node
- In the Additional Prompt, write:
  > "Answer the caller's questions about our hours, location, and services. Continue helping until they indicate they're finished or want something else."
- The conversation naturally continues in this node until an exit condition is met

### Pattern 4: Branch Node with Multiple Conditions

**Retell Conversation Flow**: Branch node evaluating conditions and routing to different paths

**ElevenLabs**:
- Add multiple edges coming out of your Agent Node
- Each edge gets its own condition
- Order matters - put more specific conditions first, catch-all conditions last

Example: From a "Main Menu" node, you might have edges:
1. "Caller wants to schedule an appointment" → Scheduling
2. "Caller has a billing question" → Billing
3. "Caller wants to speak with someone" → Transfer
4. (Unconditional - fallback) → General Help

### Pattern 5: Global Nodes (Triggered from Anywhere)

**Retell Conversation Flow**: Global nodes that can be reached from any point in the flow

**ElevenLabs**:
- Add `transfer_to_number` or `end_call` tools to your agent
- In your main system prompt, add:
  > "If the caller asks to speak with a human, representative, or customer service at any point, use the transfer_to_number tool."
  > "If the caller says goodbye or indicates they're done, use the end_call tool."

This works from ANY node without needing explicit edges everywhere - just like your global nodes did!

### Pattern 6: Transfer Failover (Backup Numbers)

**Retell Conversation Flow**: Transfer Call node with edges for "transfer failed" going to another transfer or message

**ElevenLabs**:
Put the failover logic in the **node prompt before the transfer**:
> "Transfer the caller to billing at +1-555-123-4567. If that transfer fails or no one answers, try the backup number +1-555-987-6543. If both fail, apologize and offer to take a message."

The transfer tool returns to the agent if it fails, so your prompt handles the retry.

### Pattern 7: Variable Extractors (Collecting Caller Information)

**Retell Conversation Flow**: Variable Extractors that automatically pull information from the conversation (name, phone number, reason for calling, appointment date, etc.)

**ElevenLabs - Data Collection**:

This is how you capture information from the conversation:

1. Go to your agent's **Data Collection** settings
2. Define the fields you want to collect:
   - Field name (e.g., "caller_name", "appointment_date")
   - Description (helps the AI know what to look for)
   - Type (string, number, date, etc.)
   - Whether it's required
3. The AI automatically extracts these during conversation
4. Data shows up in your call logs and gets sent to your webhooks

**Example - Appointment Booking:**

In Retell, you might have extractors for: `patient_name`, `preferred_date`, `preferred_time`, `reason_for_visit`

In ElevenLabs Data Collection:
| Field Name | Description | Type | Required |
|------------|-------------|------|----------|
| patient_name | The patient's full name | string | Yes |
| preferred_date | Date they want to come in | string | Yes |
| preferred_time | Morning, afternoon, or specific time | string | Yes |
| reason_for_visit | Why they're scheduling | string | No |

💡 **Key difference**: Retell extracts variables per-node. ElevenLabs Data Collection works across your entire agent - define once, collect anywhere in the conversation.

---

### Important: Dynamic Variables Limitation

You might see `{{variable_name}}` syntax in ElevenLabs documentation. Here's what you need to know:

**These ONLY work with data from EXTERNAL sources:**
- Data sent via pre-call webhook
- Data returned from your webhook tools
- Data passed when starting a call via SDK

**These do NOT work with `{{variables}}`:**
- Information the caller said during the call
- Data captured via Data Collection

**Bottom line:** If you want to route based on what the caller said, use LLM conditions on your edges (e.g., "Caller said they need billing help"). Don't try to use `{{captured_intent}}` - it won't work.

---

## Writing Effective Prompts

### Main System Prompt Structure

```
# Personality
You are [Name], a [role] at [Company].
You are helpful, professional, and patient.

# Tone  
Keep responses concise - under 2-3 sentences when possible.
Use a warm, conversational tone.

# Goal
Help callers with [primary purpose].

# Tools
Use 'transfer_to_number' when the caller needs human assistance.
Use 'end_call' when the conversation is complete.

# Important Rules
- Never make up information you don't have
- Always confirm important details back to the caller
- If unsure, offer to connect to a human
```

### Node-Specific Prompts (Additional Prompt)

Keep these **short and focused**:

```
# Goal
Collect the caller's appointment preferences.

# Steps
1. Ask what day works best
2. Ask morning or afternoon
3. Confirm the details

# When Done
Once appointment preferences are confirmed, the conversation can proceed.
```

### Tips for Better Prompts

| Do This | Not This |
|---------|----------|
| "Ask for their account number" | "You should probably ask for their account number if you think it's relevant" |
| "Confirm the address: 123 Main St" | "Make sure to confirm everything is correct" |
| "If transfer fails, apologize and offer to take a message" | "Handle errors appropriately" |

**Pro tip**: End critical instructions with "This step is important." The AI pays extra attention to these.

---

## Setting Up Transfers

### Blind vs Conference Transfer

| Type | What Happens | When to Use |
|------|--------------|-------------|
| **Blind** | Caller is transferred immediately, AI disconnects | General routing, simple transfers |
| **Conference** | AI stays on until human answers | VIP callers, warm handoffs |

### Transfer Tool Setup

In your agent's tools section, add a system tool:
- **Type**: transfer_to_number
- **Transfers**: Add each destination with:
  - Phone number
  - Condition (when to use this transfer)
  - Transfer type (blind or conference)

Example conditions:
- "When caller asks about billing or payment issues"
- "When caller needs technical support"
- "When caller explicitly asks for a human"

---

## Testing Your Agent

### In the Dashboard
1. Use the **Test** button to have a conversation
2. Check the transcript for any issues
3. Review the call logs after testing

### Test Scenarios to Try
- [ ] Happy path through main flow
- [ ] Ask for a human transfer
- [ ] Ask multiple questions (FAQ handling)
- [ ] Say goodbye naturally (should trigger end)
- [ ] Ask about something off-topic

---

## Common Migration Issues

### "My edges aren't working"
- Check that conditions are specific enough
- Make sure you're not trying to have two edges between the same nodes
- Verify the condition describes observable behavior ("caller said X") not internal state ("caller is frustrated")

### "Transfers aren't happening"
- If using a Phone Transfer node: that's a one-way street, no fallback
- If using transfer_to_number tool: check the condition matches what caller says
- Make sure phone numbers are in correct format (+1XXXXXXXXXX)

### "Agent isn't following instructions"
- Move critical instructions to the `# Important Rules` section
- Add "This step is important." after key instructions
- Keep prompts concise - shorter is often better

### "Conversation gets stuck"
- Check that every non-terminal node has outgoing edges
- Make sure at least one edge condition can be met
- Add an "unconditional" edge as a fallback if needed

---

## Quick Reference: Node Type Mapping

| Retell Conversation Flow | ElevenLabs | Notes |
|--------------------------|------------|-------|
| (Start of flow) | Start Node | Auto-created in ElevenLabs |
| Conversation Node | Agent Node | Very similar - add prompts here |
| Branch Node | *Edge conditions* | No equivalent node - logic goes on edges |
| Transfer Call Node | Phone Transfer Node | Terminal - no outgoing edges allowed |
| End Node | End Node | Terminal - no outgoing edges allowed |

### Terminal Nodes (No Outgoing Edges)
- **Phone Transfer** - Once the call transfers, the workflow is done
- **End** - Call is terminated

💡 If you need fallback behavior after a transfer attempt, use the `transfer_to_number` tool instead of a Phone Transfer node.

---

## Need More Help?

- **ElevenLabs Documentation**: docs.elevenlabs.io
- **Workflow Builder Guide**: Look for "Conversational AI" in the docs
- **Voice Library**: Browse voices at elevenlabs.io/voice-library

---

## Migration Checklist

### Setup
- [ ] Created new agent in ElevenLabs Conversational AI
- [ ] Set first message (your begin message from Retell)
- [ ] Configured system prompt (personality, tone, rules)
- [ ] Selected a voice

### Workflow
- [ ] Added Agent Nodes for each Conversation Node from Retell
- [ ] Moved Branch Node logic to edge conditions
- [ ] Created edges with clear, specific conditions
- [ ] Added Phone Transfer nodes (or configured transfer tool)
- [ ] Added End nodes where needed
- [ ] Checked for bidirectional flows - using single edges with forward + backward conditions

### Tools & Data
- [ ] Added `end_call` system tool
- [ ] Added `transfer_to_number` tool (if you need human escalation from anywhere)
- [ ] Migrated any webhook/custom tools
- [ ] Set up Data Collection fields (if you had Variable Extractors)

### Testing
- [ ] Tested main happy path
- [ ] Tested each branch/routing condition
- [ ] Tested transfer scenarios
- [ ] Tested saying goodbye (should end call)
- [ ] Tested asking for a human

---

## Quick Tips for Success

1. **Start simple** - Get your main flow working before adding all the edge cases
2. **Test as you go** - Use the built-in test feature after each major change
3. **Conditions should be observable** - "Caller said they want billing help" not "Caller is frustrated"
4. **When in doubt, use tools** - Transfer tools give you more control than transfer nodes
5. **Keep prompts short** - Concise instructions often work better than long explanations

Good luck with your migration.
