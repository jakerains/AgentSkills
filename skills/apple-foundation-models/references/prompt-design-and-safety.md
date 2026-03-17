# Prompt Design and Safety

## Table of Contents

- [Instructions vs Prompts](#instructions-vs-prompts)
- [Instruction Design](#instruction-design)
- [Prompt Best Practices](#prompt-best-practices)
- [User Input Handling Patterns](#user-input-handling-patterns)
- [Safety Layers](#safety-layers)
- [Error Handling](#error-handling)
- [Safety Evaluation Checklist](#safety-evaluation-checklist)
- [Sources](#sources)

## Instructions vs Prompts

Foundation Models distinguishes between **instructions** (developer-provided, persistent) and **prompts** (per-request, may include user input).

| Aspect | Instructions | Prompts |
|--------|-------------|---------|
| Set by | Developer only | Developer or user input |
| Lifetime | Persist for the session | Per-request |
| Priority | Higher — model treats as system-level | Lower — model treats as user-level |
| Purpose | Define behavior, persona, constraints | Provide the specific task or question |
| Security | Never include user input in instructions | User input goes here (with care) |

**Critical rule:** Instructions are the developer's voice. Never inject raw user input into the `instructions:` parameter — it could override your behavioral constraints.

## Instruction Design

Set instructions when creating a session. They define how the model behaves for all requests in that session.

```swift
import FoundationModels

let session = LanguageModelSession(
    instructions: """
    You are a cooking assistant for the RecipeApp.
    - Only answer questions about cooking, recipes, and food.
    - When asked about other topics, politely redirect to cooking.
    - Keep responses under 100 words.
    - Use metric measurements.
    - Never recommend recipes with raw meat for children.
    """
)
```

**Instruction design tips:**
- Lead with the role or persona.
- Use bullet points for behavioral constraints.
- State what the model should NOT do (negative constraints are effective).
- Keep instructions under 500 tokens to leave room for prompts and output.
- Test with adversarial prompts to verify constraints hold.

## Prompt Best Practices

| Technique | Example | Why It Works |
|-----------|---------|-------------|
| Length qualifiers | "Summarize in 3 bullets" | Prevents runaway output in a 4096-token window |
| Role/style markers | "Rewrite as a formal business email" | Anchors the model's tone without long instructions |
| ALL-CAPS for emphasis | "List ingredients. DO NOT include allergens." | Small models respond well to typographic emphasis |
| Few-shot examples | "Input: 'great!' → Positive\nInput: 'terrible service' → Negative\nInput: '{userText}' →" | Shows the model the exact output format expected |
| Task decomposition | "Step 1: Extract names. Step 2: Classify each as person or organization." | Breaks complex tasks into reliable single-hop steps |
| Explicit output format | "Reply with only the category name, nothing else." | Prevents the model from adding unwanted preamble |

**Token budget awareness:** Instructions + prompt + output must all fit in 4,096 tokens. If your instructions are 300 tokens and your prompt is 500, the model has ~3,296 tokens for output. Plan accordingly.

## User Input Handling Patterns

How you incorporate user input determines your risk profile. Choose the pattern that matches your trust level.

### Pattern 1: Direct Inclusion (High Risk)

User input goes directly into the prompt. Only use when the input is trusted or the model's instructions are strong enough to constrain behavior.

```swift
// ⚠️ High risk — user could inject adversarial prompts
let response = try await session.respond(
    to: userProvidedText
)
```

### Pattern 2: Combined with Template (Balanced)

Wrap user input in a structured prompt template. The template provides context and constraints.

```swift
// ✅ Balanced — template constrains the task
let prompt = """
Classify the following customer review as positive, negative, or neutral.
Reply with only the classification label.

Review: \(userProvidedText)

Classification:
"""
let response = try await session.respond(to: prompt)
```

### Pattern 3: Curated Input (Low Risk)

User input is sanitized, truncated, or selected from fixed options before reaching the model.

```swift
// ✅ Low risk — input is bounded and sanitized
let sanitized = userProvidedText
    .prefix(500)                          // Truncate to limit
    .replacingOccurrences(of: "\n", with: " ") // Flatten
    .trimmingCharacters(in: .whitespacesAndNewlines)

let prompt = "Summarize this text in 2 sentences: \(sanitized)"
let response = try await session.respond(to: prompt)
```

### Choosing a Pattern

| Scenario | Pattern | Rationale |
|----------|---------|-----------|
| Developer-controlled prompts only | Direct | No user input, no risk |
| User provides content to be processed | Combined | Template constrains the task |
| User provides freeform instructions | Curated | Sanitize and truncate first |
| Untrusted input from external sources | Curated | Maximum defensive filtering |

## Safety Layers

Apple's Foundation Models framework includes multiple safety layers:

### 1. Built-in Guardrails

The model has built-in safety training that prevents it from generating harmful, illegal, or inappropriate content. These guardrails are always active and cannot be disabled.

When guardrails activate, the model throws a `guardrailViolation` error instead of producing output.

### 2. Safety Instructions (Developer Layer)

Add explicit safety constraints in your session instructions:

```swift
let session = LanguageModelSession(
    instructions: """
    You are a children's story assistant.
    - Never generate violent, scary, or inappropriate content.
    - If asked for something inappropriate, respond with: "I can only help with fun, kid-friendly stories!"
    - Keep language at a 3rd-grade reading level.
    """
)
```

### 3. Input Sanitization (Code Layer)

Validate and sanitize user input before it reaches the model:

```swift
func sanitizeInput(_ text: String) -> String {
    var cleaned = text
        .prefix(1000)
        .trimmingCharacters(in: .whitespacesAndNewlines)

    // Remove potential injection patterns
    cleaned = cleaned
        .replacingOccurrences(of: "ignore previous instructions", with: "", options: .caseInsensitive)
        .replacingOccurrences(of: "ignore all instructions", with: "", options: .caseInsensitive)

    return String(cleaned)
}
```

### 4. Output Validation (Code Layer)

After generation, validate that output meets your requirements before displaying to users:

```swift
let response = try await session.respond(to: prompt)
let text = response.content

// Validate output length
guard text.count < 5000 else {
    return "Response too long. Please try a more specific question."
}

// Validate output format if expected
guard text.contains(expectedPattern) else {
    return fallbackResponse
}
```

## Error Handling

Handle all Foundation Models errors, with special attention to safety-related ones:

```swift
import FoundationModels

do {
    let response = try await session.respond(to: prompt)
    displayResult(response.content)
} catch let error as LanguageModelSession.GenerationError {
    switch error {
    case .guardrailViolation:
        // The model refused to generate due to safety guardrails.
        // Do NOT retry with a rephrased prompt attempting to bypass this.
        showSafetyMessage("This request cannot be processed. Please try a different question.")

    case .exceededContextWindowSize(let details):
        // Input + instructions exceeded the 4096-token context window.
        showError("Your input is too long. Please shorten it and try again.")

    case .unsupportedLanguageOrLocale:
        // The current locale is not in the 15 supported languages.
        showError("This language is not currently supported.")

    default:
        showError("Something went wrong. Please try again.")
    }
} catch {
    showError("An unexpected error occurred: \(error.localizedDescription)")
}
```

**Critical:** When `guardrailViolation` fires, do not:
- Retry with a rephrased version of the same prompt.
- Log the original prompt in a way that exposes user data.
- Display a message that implies the user did something wrong (it may be a false positive).

## Safety Evaluation Checklist

Before shipping a feature that uses Foundation Models, verify each item:

- [ ] **Instructions don't contain user input.** User-provided text goes only in the prompt.
- [ ] **User input is sanitized.** Length-limited, trimmed, and filtered for injection patterns.
- [ ] **`guardrailViolation` is handled gracefully.** Shows a neutral message, doesn't retry or blame the user.
- [ ] **`exceededContextWindowSize` is handled.** Tells the user to shorten input.
- [ ] **`unsupportedLanguageOrLocale` is handled.** Checked before generation or handled after.
- [ ] **Output is validated.** Length, format, and content checks before displaying.
- [ ] **Adversarial prompts tested.** Tried injection attacks ("ignore previous instructions...") and verified they don't bypass constraints.
- [ ] **Fallback UX exists.** If the model is unavailable or errors out, the app still functions.
- [ ] **Privacy reviewed.** Sensitive user data in prompts stays on-device (it does by default, but verify no logging sends it elsewhere).

## Sources

- https://developer.apple.com/documentation/foundationmodels
- https://developer.apple.com/documentation/foundationmodels/languagemodelsession
- WWDC25 Session 248: Design great prompts for Foundation Models
- WWDC25 Session: Meet the Foundation Models framework
- https://developer.apple.com/apple-intelligence/
