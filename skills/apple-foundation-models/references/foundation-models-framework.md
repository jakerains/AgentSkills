# Foundation Models Framework Reference

## Table of Contents

- [Scope](#scope)
- [Platform and Availability Snapshot](#platform-and-availability-snapshot)
- [Local-First Baseline Pattern](#local-first-baseline-pattern)
- [Availability-Aware UX Pattern](#availability-aware-ux-pattern)
- [Session and Prompting Rules](#session-and-prompting-rules)
- [Token and Context Window Constraints](#token-and-context-window-constraints)
- [Streaming](#streaming)
- [Guided Generation and Tools](#guided-generation-and-tools)
- [Locale, Safety, and Guardrails](#locale-safety-and-guardrails)
- [Performance Tuning](#performance-tuning)
- [Adapter Guidance](#adapter-guidance)
- [Testing and Debugging](#testing-and-debugging)
- [Sources](#sources)

## Scope

Use this reference when building text features with the Foundation Models framework in iOS and macOS apps. For structured output, see `references/generable-and-guided-generation.md`. For tool calling, see `references/tool-calling.md`. For prompt design and safety, see `references/prompt-design-and-safety.md`.

## Platform and Availability Snapshot

- `FoundationModels` framework availability: iOS 26.0+, iPadOS 26.0+, macOS 26.0+, Mac Catalyst 26.0+, visionOS 26.0+.
- `SystemLanguageModel` is the on-device language model in app code.
- Model usage depends on Apple Intelligence device eligibility and whether Apple Intelligence is enabled.
- The model is ~3B parameters, 2-bit quantized, with a 4,096-token context window. See `references/model-capabilities-and-limits.md` for what it can and cannot do.

## Local-First Baseline Pattern

```swift
import FoundationModels

let model = SystemLanguageModel.default
guard model.isAvailable else {
    // Fall back to non-AI UX.
    return
}

let session = LanguageModelSession(model: model)
let response = try await session.respond(to: "Summarize this note in 3 bullets.")
```

## Availability-Aware UX Pattern

Use `availability` for targeted UX states.

```swift
switch SystemLanguageModel.default.availability {
case .available:
    // Show AI feature.
case .unavailable(.deviceNotEligible):
    // Device does not support Apple Intelligence.
case .unavailable(.appleIntelligenceNotEnabled):
    // Ask user to enable Apple Intelligence.
case .unavailable(.modelNotReady):
    // Model may be downloading or preparing.
case .unavailable:
    // Generic fallback.
}
```

## Session and Prompting Rules

- Use a new `LanguageModelSession` for one-shot tasks.
- Reuse the same session for multi-turn tasks that need conversation memory.
- Send one request at a time per session. Check `isResponding` before issuing another request.
- Keep prompts task-specific and concise.
- Use the `instructions:` parameter for developer-level behavioral constraints. **Never put user input in instructions** — it has elevated priority. See `references/prompt-design-and-safety.md` for details.

```swift
let session = LanguageModelSession(
    instructions: """
    You are a note-taking assistant.
    - Respond only with bullet-point summaries.
    - Keep each bullet under 20 words.
    - Use plain language, no jargon.
    """
)
```

## Token and Context Window Constraints

- Session context window is 4,096 tokens total (instructions + prompts + outputs).
- Catch `LanguageModelSession.GenerationError.exceededContextWindowSize(_)`.
- For large inputs, chunk data and process across multiple sessions.
- Budget your tokens: if instructions are ~300 tokens and the prompt is ~500, you have ~3,296 tokens for output.

## Streaming

Streaming is essential for user-facing generation. It delivers partial results as they are produced, giving users immediate feedback instead of waiting for the full response.

### Basic Streaming

```swift
import FoundationModels

let session = LanguageModelSession()

for try await partial in session.streamResponse(to: "Write a haiku about Swift programming.") {
    // partial.content grows incrementally
    updateTextView(partial.content)
}
```

### Streaming with Guided Generation

When streaming `@Generable` types, each yielded value is a `PartiallyGenerated<T>` where properties fill in progressively in declaration order.

```swift
@Generable
struct MeetingSummary {
    var title: String
    var keyDecisions: [String]
    var actionItems: [String]
}

let stream = session.streamResponse(
    to: "Summarize this meeting transcript: \(transcript)",
    generating: MeetingSummary.self
)

for try await partial in stream {
    if let title = partial.title {
        titleLabel.text = title
    }
    if let decisions = partial.keyDecisions {
        updateDecisionsList(decisions)
    }
}

let final = try await stream.result
```

### SwiftUI Streaming Pattern

Use `@State` to hold partial content and update the view as tokens arrive.

```swift
import SwiftUI
import FoundationModels

struct StreamingView: View {
    @State private var displayText = ""
    @State private var isGenerating = false

    var body: some View {
        VStack {
            ScrollView {
                Text(displayText)
                    .animation(.easeInOut, value: displayText)
            }

            Button("Generate") {
                Task { await generate() }
            }
            .disabled(isGenerating)
        }
    }

    private func generate() async {
        isGenerating = true
        displayText = ""

        let session = LanguageModelSession()
        do {
            for try await partial in session.streamResponse(to: "Explain SwiftUI state management in 3 paragraphs.") {
                displayText = partial.content
            }
        } catch {
            displayText = "Error: \(error.localizedDescription)"
        }

        isGenerating = false
    }
}
```

**Rule:** Always stream user-facing generation. Use non-streaming `respond(to:)` only for background processing where the user doesn't see incremental output.

## Guided Generation and Tools

Detailed guidance for these features is in dedicated reference files:

- **Guided generation (`@Generable`, `@Guide`):** See `references/generable-and-guided-generation.md`
- **Tool calling (`Tool` protocol, dynamic tools):** See `references/tool-calling.md`

Quick reminders:
- Use `@Generable` types for typed outputs — never ask the model to produce JSON in a prompt.
- Use `Tool` to give the model access to app logic, local data, or external services.
- Keep tool argument descriptions short; long descriptions increase token usage and latency.
- Inspect `session.transcript` to debug tool-call graphs.

## Locale, Safety, and Guardrails

- Check locale support with `SystemLanguageModel.supportsLocale(_:)`.
- Handle `unsupportedLanguageOrLocale` generation errors.
- Remember that built-in guardrails are scoped to supported languages and locales.
- For comprehensive safety guidance, see `references/prompt-design-and-safety.md`.

## Performance Tuning

- Call `prewarm(promptPrefix:)` before expected generation to reduce time-to-first-token.
- Reduce token usage with concise instructions and prompts.
- Use Instruments and Foundation Models profiling guidance to measure improvements.
- For guided generation streams, tune `includeSchemaInPrompt` to balance quality versus token cost.
- Always stream user-facing output — perceived performance is dramatically better than waiting for a full response.

## Adapter Guidance

- Use adapters only for advanced specialization after prompt and tool optimization.
- Adapter files are large (160MB+). Deliver via Background Assets or server-hosted packs.
- Adapters are version-specific to base model versions and require retraining as model versions update.
- Deployment requires `com.apple.developer.foundation-model-adapter` entitlement.

## Testing and Debugging

There is **no terminal/CLI access** to Apple's on-device model. `SystemLanguageModel` requires the full Apple Intelligence runtime on a supported device. All testing happens within the Apple developer toolchain.

### Xcode #Playground Macro (Fastest Iteration)

The `#Playground` macro gives live model output directly in the Xcode source editor — no build-and-run cycle needed. Use it to iterate on prompts, test instruction variations, and validate `@Generable` schemas.

```swift
import FoundationModels

#Playground {
    let session = LanguageModelSession(
        instructions: "Reply with exactly 3 bullet points."
    )
    let response = try await session.respond(to: "Summarize the benefits of SwiftUI.")
    print(response.content)
}
```

**Tips for `#Playground`:**
- Runs on a connected device or Mac with Apple Intelligence enabled.
- Change the prompt and see new output without rebuilding.
- Test `@Generable` types here before integrating into production code.
- Test edge cases: empty input, very long input, unsupported languages.

### SwiftUI Previews

Xcode Previews can run Foundation Models code on a connected device. Useful for testing streaming UX patterns.

```swift
#Preview {
    StreamingView()
}
```

**Limitation:** Previews require a device or simulator with Apple Intelligence support. Standard simulators may not have the model available — check `isAvailable` in your preview.

### Transcript Inspection (Tool Call Debugging)

After any generation that involves tools, inspect `session.transcript` to see exactly what the model did — which tools it called, in what order, with what arguments, and what each tool returned.

```swift
let response = try await session.respond(to: "What's the weather in Tokyo?")

// Debug: print the full interaction trace
for entry in session.transcript {
    print(entry)
}
```

This is the primary debugging tool for understanding why the model:
- Called a tool you didn't expect
- Didn't call a tool you expected
- Produced unexpected output after tool calls
- Made multiple tool calls instead of one

### Instruments Profiling

Use the **Foundation Models instrument** in Xcode Instruments to measure:
- Time-to-first-token (TTFT)
- Total generation time
- Token throughput
- Context window utilization

Profile on a physical device for accurate numbers — simulator performance does not reflect real hardware.

### Feedback Attachments (Beta Testing)

During beta testing, use `LanguageModelFeedbackAttachment` to let testers report problematic outputs directly to Apple.

```swift
import FoundationModels

// After a session produces a bad response:
let feedback = LanguageModelFeedbackAttachment(session: session)
// Attach to your TestFlight feedback flow or bug reporter
```

### Physical Device Requirements

| Test Surface | Apple Intelligence Required | Notes |
|-------------|---------------------------|-------|
| `#Playground` macro | Yes (on connected device or Mac) | Fastest prompt iteration |
| SwiftUI Previews | Yes | May not work on all simulators |
| Unit tests (XCTest) | Yes (on device) | Must guard with `isAvailable` |
| Instruments profiling | Yes (physical device) | Simulator numbers are inaccurate |
| UI tests (XCUITest) | Yes (on device) | Test availability fallback paths on ineligible devices too |

**Always test your fallback UX** on a device or simulator where Apple Intelligence is NOT available. The `isAvailable` / `availability` code paths are just as important as the happy path.

## Sources

- https://developer.apple.com/documentation/foundationmodels
- https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models
- https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel
- https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling
- https://developer.apple.com/documentation/foundationmodels/supporting-languages-and-locales-with-foundation-models
- https://developer.apple.com/documentation/foundationmodels/analyzing-the-runtime-performance-of-your-foundation-models-app
- https://developer.apple.com/documentation/foundationmodels/loading-and-using-a-custom-adapter-with-foundation-models
- WWDC25 Session: Meet the Foundation Models framework
- WWDC25 Session: Build an agent with the Foundation Models framework
- WWDC25 Session: Stream and generate structured output with Foundation Models
