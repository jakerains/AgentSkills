# Model Capabilities and Limitations

## Table of Contents

- [Model Specifications](#model-specifications)
- [Strong Capabilities](#strong-capabilities)
- [Known Limitations](#known-limitations)
- [Decision Flowchart](#decision-flowchart)
- [Content Tagging Adapter](#content-tagging-adapter)
- [Xcode Playground Macro](#xcode-playground-macro)
- [Reporting Issues](#reporting-issues)
- [Sources](#sources)

## Model Specifications

| Property | Value |
|----------|-------|
| Parameters | ~3 billion |
| Quantization | 2-bit (on-device) |
| Context window | 4,096 tokens (instructions + prompts + outputs) |
| Supported languages | 15 (English, Chinese, French, German, Italian, Japanese, Korean, Portuguese, Spanish, Vietnamese, Hindi, Turkish, Dutch, Thai, Swedish) |
| Runtime | On-device only via `SystemLanguageModel` |
| Availability | iOS 26+, iPadOS 26+, macOS 26+, Mac Catalyst 26+, visionOS 26+ |

## Strong Capabilities

The on-device model excels at focused, constrained tasks where the answer comes from the input or the prompt itself.

| Capability | Description | Example Prompt |
|-----------|-------------|----------------|
| Summarization | Condense input text into key points | "Summarize this email in 3 bullets." |
| Extraction | Pull structured data from unstructured text | "Extract the date, location, and attendee count from this event description." |
| Classification | Categorize input into predefined labels | "Classify this review as positive, negative, or neutral." |
| Tagging | Assign topic or category tags to content | Use `SystemLanguageModel(useCase: .contentTagging)` built-in adapter |
| Composition | Draft short-form text (emails, replies, captions) | "Write a friendly reply declining this meeting invitation." |
| Revision | Rewrite, adjust tone, fix grammar | "Rewrite this paragraph in a more formal tone." |
| Guided generation | Produce typed structured output via `@Generable` | See `references/generable-and-guided-generation.md` |
| Tool calling | Invoke app functions to fetch or act on data | See `references/tool-calling.md` |

## Known Limitations

The on-device model is a small (~3B) language model. It does **not** have broad world knowledge, reasoning depth, or code generation ability comparable to cloud models.

| Limitation | Why It Fails | Alternative |
|-----------|-------------|-------------|
| World knowledge / factual Q&A | Training data is limited; model hallucinates facts | Route to a backend cloud model or use a tool that fetches authoritative data |
| Math and arithmetic | Small models are unreliable at multi-step math | Use a tool that calls a calculator or math library |
| Code generation | Cannot reliably produce syntactically correct code | Route to a cloud model specialized for code |
| Long-form writing (>200 words) | 4,096-token context window limits total output length | Split into multiple sessions or route to a cloud model |
| Multi-hop reasoning | Chains of dependent inferences degrade quickly | Break into sequential single-hop steps with tools |
| Real-time / current events | No internet access, no live data | Use a tool that fetches live data from an API |
| Languages not in the 15 supported | Model will produce low-quality or garbled output | Check `SystemLanguageModel.supportsLocale(_:)` first |

**Critical rule:** Before writing code, check the task against these tables. If the task falls under "Known Limitations," design an escalation path (tool, backend model, or user-facing disclosure) instead of relying on the on-device model alone.

## Decision Flowchart

```
User request arrives
        │
        ▼
Is the task summarization, extraction,
classification, tagging, composition,
revision, or structured output?
        │
   YES ─┤─── NO
   │         │
   ▼         ▼
Does it fit   Does it need world knowledge,
in 4096       math, code gen, or long-form?
tokens?       │
   │     YES ─┤─── NO (ambiguous)
   │     │         │
   ▼     ▼         ▼
Use      Route to   Try on-device first,
on-      backend    catch errors, fall
device   model      back to backend
```

## Content Tagging Adapter

Apple ships a built-in adapter optimized for content tagging. Use it instead of prompt engineering when the task is assigning topic tags.

```swift
import FoundationModels

let model = SystemLanguageModel(useCase: .contentTagging)
guard model.isAvailable else { return }

let session = LanguageModelSession(model: model)
let response = try await session.respond(to: articleText)
// response.content contains comma-separated tags
```

## Xcode Playground Macro

Use the `#Playground` macro in Xcode to iterate on prompts without building and running your app. This provides a live preview of model output directly in the source editor.

```swift
import FoundationModels

#Playground {
    let session = LanguageModelSession()
    let response = try await session.respond(to: "Summarize: The meeting discussed Q3 targets and hiring plans.")
    print(response.content)
}
```

**Tip:** Use `#Playground` to test prompt phrasing, instruction variations, and guided generation schemas before integrating into production code.

## Reporting Issues

Use `LanguageModelFeedbackAttachment` to let users report problematic model outputs directly to Apple. Attach this to a feedback mechanism in your app during development or beta testing.

```swift
import FoundationModels

// After receiving a response from a session:
let feedback = LanguageModelFeedbackAttachment(session: session)
// Attach to your feedback/bug-report flow
```

## Sources

- https://developer.apple.com/documentation/foundationmodels
- https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel
- https://machinelearning.apple.com/research/introducing-apple-foundation-models
- https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
- WWDC25 Session: Explore machine learning on Apple silicon
- WWDC25 Session: Meet the Foundation Models framework
