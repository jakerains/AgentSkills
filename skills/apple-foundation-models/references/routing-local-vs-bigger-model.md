# Routing: Local Versus Bigger Model

## Table of Contents

- [Critical Distinction](#critical-distinction)
- [Routing Strategy](#routing-strategy)
- [When to Stay On-Device](#when-to-stay-on-device)
- [When to Escalate](#when-to-escalate)
- [Escalation Paths](#escalation-paths)
- [Backend Fallback Example](#backend-fallback-example)
- [App Intents and Use Model Example](#app-intents-and-use-model-example)
- [Example Router Shape](#example-router-shape)
- [Guardrails for Router Design](#guardrails-for-router-design)
- [Date and Verification Note](#date-and-verification-note)
- [Sources](#sources)

## Critical Distinction

- Foundation Models framework APIs in app code expose the on-device language model (`SystemLanguageModel`).
- Apple Intelligence as a platform includes both on-device and server-side models (Private Cloud Compute), but those are not the same thing as public Foundation Models app APIs.
- Apple's "Use Model" action in Shortcuts/App Intents is documented as using Apple Intelligence models on device or with Private Cloud Compute.

Treat these as separate routing surfaces unless Apple publishes an explicit server-routing API for `FoundationModels`.

## Routing Strategy

1. Default to on-device Foundation Models in app code.
2. Escalate to a larger model path only when task requirements exceed on-device limits.
3. Preserve user trust with clear privacy/network behavior and graceful fallback UX.

## When to Stay On-Device

- Structured extraction, summarization, rewriting, classification, tagging, composition, and revision.
- Workloads that fit within the session context window (4,096 tokens).
- Privacy-sensitive data that should remain local.
- Features that need offline support.

For a detailed breakdown of what the on-device model handles well, see `references/model-capabilities-and-limits.md`.

## When to Escalate

- Prompt or context size routinely exceeds on-device limits.
- The task needs broad world knowledge, factual Q&A, or deeper reasoning not reliably met by the on-device model.
- The task requires math, arithmetic, or code generation (unreliable on-device).
- Product requirements explicitly require cloud-scale model behavior.

## Escalation Paths

### Path A: App Intents and Shortcuts (Apple-Managed Routing to PCC)

Use this when your app surfaces actions through Siri and Shortcuts. The "Use Model" action in Shortcuts can route to Apple's Private Cloud Compute (PCC) — larger, more capable models — but this routing is **Apple-managed** and only available through the Shortcuts/App Intents surface, not through direct API calls in app code.

**How it works:**
1. Your app defines App Intents (actions and entities) that expose app functionality.
2. Users (or Shortcuts automations) can chain your intents with the built-in "Use Model" action.
3. "Use Model" sends a prompt to Apple Intelligence, which decides whether to run on-device or escalate to PCC based on task complexity.
4. The result flows back into the Shortcut, which can pass it to your app's next intent.

**You don't control the routing** — Apple Intelligence decides on-device vs PCC. But your app benefits from PCC's superior reasoning when users invoke your features through Siri or Shortcuts.

See the [App Intents and Use Model Example](#app-intents-and-use-model-example) section below for a concrete implementation.

### Path B: In-App Backend Router (Your Own Cloud Model)

Use this for direct in-app experiences that need larger-model fallback. This is the path to use when you need **programmatic control** over cloud model access.

- Keep a local-first `FoundationModels` path as the default.
- Add a backend model path (your provider choice: OpenAI, Anthropic, Google, etc.) for escalation.
- Route based on availability, context size, task type, latency budget, and policy.
- The user should be informed when data leaves the device (privacy transparency).

See the [Backend Fallback Example](#backend-fallback-example) section below for a complete try-local-then-cloud pattern.

## Backend Fallback Example

This pattern tries on-device generation first, detects when it fails or is unavailable, and falls back to a cloud API.

```swift
import FoundationModels

enum GenerationResult {
    case local(String)
    case cloud(String)
    case failed(Error)
}

actor SmartGenerator {
    /// Attempts on-device generation first, falls back to a cloud provider.
    func generate(prompt: String, requiresWorldKnowledge: Bool = false) async -> GenerationResult {
        // Skip local entirely for tasks we know it can't handle
        if requiresWorldKnowledge {
            return await generateFromCloud(prompt: prompt)
        }

        let model = SystemLanguageModel.default
        guard model.isAvailable else {
            return await generateFromCloud(prompt: prompt)
        }

        // Try on-device first
        do {
            let session = LanguageModelSession(model: model)
            let response = try await session.respond(to: prompt)
            return .local(response.content)
        } catch let error as LanguageModelSession.GenerationError {
            switch error {
            case .exceededContextWindowSize:
                // Input too large for on-device — escalate
                return await generateFromCloud(prompt: prompt)
            case .guardrailViolation:
                // Safety refusal — don't retry on cloud with same prompt
                return .failed(error)
            default:
                return await generateFromCloud(prompt: prompt)
            }
        } catch {
            return await generateFromCloud(prompt: prompt)
        }
    }

    private func generateFromCloud(prompt: String) async -> GenerationResult {
        // Replace with your preferred cloud AI provider
        guard let url = URL(string: "https://your-backend.example.com/api/generate") else {
            return .failed(URLError(.badURL))
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONEncoder().encode(["prompt": prompt])

        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            let result = try JSONDecoder().decode(CloudResponse.self, from: data)
            return .cloud(result.text)
        } catch {
            return .failed(error)
        }
    }
}

struct CloudResponse: Codable {
    let text: String
}
```

**Usage in SwiftUI:**

```swift
struct SmartTextView: View {
    @State private var result = ""
    @State private var source = ""
    let generator = SmartGenerator()

    var body: some View {
        VStack {
            Text(result)
            if !source.isEmpty {
                Text("Generated \(source)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Button("Analyze") {
                Task {
                    let output = await generator.generate(
                        prompt: "Explain quantum computing in 2 sentences.",
                        requiresWorldKnowledge: true
                    )
                    switch output {
                    case .local(let text):
                        result = text; source = "on-device"
                    case .cloud(let text):
                        result = text; source = "via cloud"
                    case .failed(let error):
                        result = "Error: \(error.localizedDescription)"; source = ""
                    }
                }
            }
        }
    }
}
```

**Key points:**
- Tag the result source so your UI can inform the user when data went to the cloud.
- Never send to cloud silently for privacy-sensitive content — check your data policy.
- Handle `guardrailViolation` separately — retrying the same prompt on cloud won't fix a safety refusal.

## App Intents and Use Model Example

This pattern exposes your app's data through App Intents so users can chain it with the "Use Model" action in Shortcuts, gaining access to Apple Intelligence's larger models (including PCC).

### Step 1: Define an App Entity

Expose your app's content as an entity the system can reference.

```swift
import AppIntents

struct NoteEntity: AppEntity {
    static var typeDisplayRepresentation = TypeDisplayRepresentation(name: "Note")
    static var defaultQuery = NoteQuery()

    var id: UUID
    var title: String
    var body: String

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(title)")
    }
}

struct NoteQuery: EntityQuery {
    func entities(for identifiers: [UUID]) async throws -> [NoteEntity] {
        return NoteStore.shared.notes(for: identifiers)
    }

    func suggestedEntities() async throws -> [NoteEntity] {
        return NoteStore.shared.recentNotes(limit: 10)
    }
}
```

### Step 2: Define an App Intent that returns content

Create an intent that extracts or returns text content from your app. The user can pipe this output into "Use Model" in a Shortcut.

```swift
import AppIntents

struct GetNoteContentIntent: AppIntent {
    static var title: LocalizedStringResource = "Get Note Content"
    static var description = IntentDescription("Returns the full text of a note.")

    @Parameter(title: "Note")
    var note: NoteEntity

    func perform() async throws -> some ReturnsValue<String> {
        return .result(value: note.body)
    }
}
```

### Step 3: User builds a Shortcut

The user creates a Shortcut like:

```
1. Get Note Content → (selects a note)
2. Use Model → "Summarize the following text in 3 bullet points: [output from step 1]"
3. Show Result
```

In step 2, Apple Intelligence routes the request to the best available model — on-device for simple tasks, PCC for complex reasoning. **Your app code doesn't need to handle this routing; Apple manages it.**

### Step 4: Accept processed results back (optional)

If your app should receive the AI-processed result, create an intent that accepts text input:

```swift
struct SaveSummaryIntent: AppIntent {
    static var title: LocalizedStringResource = "Save Note Summary"
    static var description = IntentDescription("Saves an AI-generated summary to a note.")

    @Parameter(title: "Note")
    var note: NoteEntity

    @Parameter(title: "Summary")
    var summary: String

    func perform() async throws -> some IntentResult {
        NoteStore.shared.saveSummary(summary, for: note.id)
        return .result()
    }
}
```

**When to use this path vs backend router:**

| Scenario | Use App Intents Path | Use Backend Router |
|----------|---------------------|-------------------|
| User-initiated via Siri/Shortcuts | Yes | No |
| Programmatic in-app generation | No | Yes |
| Need control over which cloud model | No (Apple decides) | Yes |
| Want PCC without managing a backend | Yes | N/A |
| Offline fallback required | No (PCC needs network) | Design your own |

## Example Router Shape

```swift
enum GenerationPath {
    case onDevice
    case backend
}

func choosePath(
    localAvailable: Bool,
    estimatedTokens: Int,
    needsBroadWorldKnowledge: Bool,
    needsMathOrCode: Bool
) -> GenerationPath {
    if localAvailable
        && estimatedTokens <= 4096
        && !needsBroadWorldKnowledge
        && !needsMathOrCode {
        return .onDevice
    }
    return .backend
}
```

## Guardrails for Router Design

- Never silently switch to cloud for sensitive content without product and policy review.
- Surface network-dependent states in UX.
- Log routing decisions and failure reasons for observability.
- Keep parity tests so local and backend outputs remain acceptable for your use case.

## Date and Verification Note

As of March 2026, Apple docs position Foundation Models app APIs as on-device access, while on-device/Private Cloud Compute wording appears in Apple Intelligence + Shortcuts/App Intents material. Re-check Apple docs for each OS cycle.

## Sources

- https://developer.apple.com/documentation/foundationmodels
- https://developer.apple.com/apple-intelligence/
- https://developer.apple.com/apple-intelligence/whats-new/
- https://machinelearning.apple.com/research/introducing-apple-foundation-models
- https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
