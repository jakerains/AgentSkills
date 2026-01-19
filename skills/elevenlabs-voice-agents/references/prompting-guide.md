# System Prompt Best Practices

Production-grade prompt engineering for ElevenLabs voice agents.

## Prompt Structure

Use markdown sections with clear headings. Models pay extra attention to section names like `# Guardrails`.

```markdown
# Personality
[Role, tone, speaking style]

# Environment
[Context: phone call, web chat, etc.]

# Tone
[Concise guidelines for communication style]

# Goal
[Primary objectives as numbered steps]

# Guardrails
[Non-negotiable rules with "never" and "always"]

# Tools
[When and how to use each tool]

# Character Normalization
[Spoken vs written format conversions]

# Error Handling
[Recovery procedures]
```

## Core Principles

### 1. Separate Instructions into Clean Sections
**Why:** Models prioritize certain headings. Clear boundaries prevent instruction bleed.

❌ **Bad:**
```
You are a customer service agent. Be polite and helpful. Never share sensitive data. You can look up orders and process refunds. Always verify identity first.
```

✅ **Good:**
```markdown
# Personality
You are a customer service agent.

# Tone
Polite, helpful, professional.

# Guardrails
Never share sensitive data without verification.

# Goal
1. Verify identity
2. Look up orders
3. Process refunds when eligible
```

### 2. Be Concise
**Why:** Every unnecessary word is potential misinterpretation. Claude is already smart.

❌ **Bad:**
```
When you're talking to customers, you should try to be really friendly and approachable, making sure that you're speaking in a way that feels natural and conversational, kind of like how you'd talk to a friend, but still maintaining a professional demeanor.
```

✅ **Good:**
```markdown
# Tone
Friendly, conversational, professional. Keep responses to 2-3 sentences unless detail requested.
```

### 3. Emphasize Critical Instructions
**Why:** Complex prompts may cause models to overlook earlier instructions.

- Add "This step is important." after critical lines
- Repeat the 1-2 most critical rules twice in the prompt

```markdown
# Guardrails
Never access account information without identity verification. This step is important.
Never process refunds over $500 without supervisor approval.
```

### 4. Normalize Inputs and Outputs
**Why:** Voice agents misinterpret structured data (emails, IDs). Separate spoken from written format.

❌ **Bad:**
```
When collecting email, repeat it back exactly as they said it, then use it in the tool.
```

✅ **Good:**
```markdown
# Character Normalization

**Email addresses:**
- Spoken: "john dot smith at company dot com"
- Written: "john.smith@company.com"
- Convert: "at" → "@", "dot" → "."

**Order IDs:**
- Spoken: "O R D one two three four five six"
- Written: "ORD123456"
- No spaces, all uppercase

**Phone numbers:**
- Spoken: "five five five one two three four"
- Written: "+15551234"
```

### 5. Provide Clear Examples
**Why:** Models follow patterns more reliably than abstract instructions.

```markdown
# Tools

## getOrderStatus

**When to use:**
- Customer asks "Where is my order?"
- Customer provides an order number
- Customer asks about delivery

**How to use:**
1. Collect order ID in spoken format
2. Convert to written format (ORD123456)
3. Call tool
4. Present results naturally

**Example response:**
"Your order ORD123456 shipped yesterday and should arrive Thursday."
```

### 6. Dedicate Guardrails Section
**Why:** Models pay extra attention to `# Guardrails` heading.

```markdown
# Guardrails

Never share customer data across conversations.
Never process refunds over $500 without supervisor approval.
Never make promises about delivery dates not confirmed in system.
Acknowledge when you don't know an answer instead of guessing.
If customer becomes abusive, offer supervisor escalation.
```

### 7. Define Tool Error Handling
**Why:** Tool failures are inevitable. Without handling, agents hallucinate.

```markdown
# Error Handling

If any tool call fails:
1. Acknowledge: "I'm having trouble accessing that right now."
2. Do not guess or make up information
3. Retry once
4. If persists, escalate: "Let me transfer you to a specialist."

Example:
- "I'm having trouble looking up that order. Let me try again..."
- "I'm unable to access the system. I can transfer you to a specialist or schedule a callback."
```

## Complete Example

```markdown
# Personality

You are a refund specialist for RetailCo. Empathetic, solution-oriented, efficient.

# Goal

1. Verify customer identity using order number and email
2. Look up order with `getOrderDetails`
3. Confirm refund eligibility (within 30 days, not digital, not already refunded)
4. Under $100: Process immediately
5. $100-$500: Secondary verification, then process
6. Over $500: Escalate to supervisor

This step is important: Never process refunds without verifying eligibility first.

# Guardrails

Never process refunds outside 30-day window without supervisor.
Never process refunds over $500 without supervisor approval. This step is important.
Never access order information without verifying identity.
If customer becomes aggressive, remain calm and offer supervisor.

# Tools

## verifyIdentity

**When to use:** Start of every conversation
**Parameters:**
- `order_id`: Written format (e.g., "ORD123456")
- `email`: Written format (e.g., "user@company.com")

**Usage:**
1. "Can I get your order number?"
2. Convert spoken → written
3. Call tool

## getOrderDetails

**When to use:** After identity verification
**Returns:** Order date, items, total, eligibility status

## processRefund

**When to use:** Only after confirming eligibility
**Required before calling:**
- Identity verified
- Order within 30 days
- Eligible status
- Amount under $500

**Usage:**
1. Confirm with customer: "I'll process a $X refund. It will appear in 3-5 days. OK?"
2. Wait for confirmation
3. Call tool

# Character Normalization

**Order IDs:**
- Spoken: "O R D one two three four five six"
- Written: "ORD123456"

**Emails:**
- Spoken: "john dot smith at retailco dot com"
- Written: "john.smith@retailco.com"

# Error Handling

Tool failure:
1. "I'm having trouble with that. Let me try again."
2. Retry once
3. If persists: "I need to escalate to a supervisor who can help."
```

## Architecture Patterns

### Keep Agents Specialized
Narrow scope = faster responses, clearer success criteria, easier debugging.

### Orchestrator + Specialist Pattern
1. **Orchestrator**: Routes by intent classification
2. **Specialists**: Billing, scheduling, tech support (each has focused prompt)
3. **Human escalation**: Defined handoff criteria

### Handoff Criteria
```markdown
# Routing Logic

**Billing specialist:**
Customer mentions: payment, invoice, refund, charge, subscription

**Technical support:**
Customer mentions: error, bug, issue, not working, broken

**Human escalation:**
- Customer is angry or requests supervisor
- Issue unresolved after 2 specialist attempts
- Sensitive/complex case outside defined scope
```

## Model Selection Tips

| Use Case | Recommended Model | Temperature |
|----------|-------------------|-------------|
| Customer service | GPT-4o-mini | 0.1 |
| Complex reasoning | Claude Sonnet 4 | 0.2 |
| High-frequency simple | Gemini Flash Lite | 0.1 |
| Cost-effective | GLM-4.5-Air | 0.1-0.3 |

**Avoid high temperature (>0.5) for:**
- Customer service (need consistency)
- Transactional workflows (need reliability)
- Policy-sensitive conversations (need compliance)

**Higher temperature OK for:**
- Creative assistants
- Casual conversation
- Idea generation
