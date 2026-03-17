---
name: apple-foundation-models
description: Build Apple Intelligence features with Foundation Models and Image Playground on iOS 26+, iPadOS 26+, macOS 26+, Mac Catalyst 26+, and visionOS 26+. Use when implementing SystemLanguageModel, LanguageModelSession, guided generation with @Generable/@Guide, tool calling, streaming responses, prompt design, safety and guardrail handling, model availability checks, content tagging, context-window limits, local on-device inference, routing to larger-model paths, adapters, and ImagePlayground/ImageCreator APIs. Covers model capabilities and limitations, structured output, error handling, and SwiftUI integration patterns.
---

# Apple Foundation Models and Image Playground

Implement reliable Apple Intelligence features with Apple's on-device text and image generation APIs across all supported platforms.

## Model Limitations (CRITICAL — Read First)

The on-device model is ~3B parameters with a 4,096-token context window. It excels at summarization, extraction, classification, tagging, composition, and revision. It **cannot reliably** do:

- **World knowledge / factual Q&A** — will hallucinate
- **Math and arithmetic** — unreliable at multi-step calculations
- **Code generation** — cannot produce correct code
- **Long-form writing** (>200 words) — context window too small

Before writing any code, check `references/model-capabilities-and-limits.md` to confirm the task is within the model's capabilities. If it is not, design an escalation path (tool, backend model, or user disclosure).

## Quick Reference

| Capability | Key API | Reference |
|-----------|---------|-----------|
| Text generation (basic) | `LanguageModelSession.respond(to:)` | `references/foundation-models-framework.md` |
| Streaming output | `session.streamResponse(to:)` | `references/foundation-models-framework.md` |
| Structured output | `@Generable`, `@Guide`, `session.respond(to:generating:)` | `references/generable-and-guided-generation.md` |
| Tool calling | `Tool` protocol, `session` with `tools:` | `references/tool-calling.md` |
| Prompt and instruction design | `LanguageModelSession(instructions:)` | `references/prompt-design-and-safety.md` |
| Safety and error handling | `guardrailViolation`, input sanitization | `references/prompt-design-and-safety.md` |
| Model capabilities check | Capability/limitation tables | `references/model-capabilities-and-limits.md` |
| Image generation | `ImagePlayground`, `ImageCreator` | `references/image-playground.md` |
| Testing and debugging | `#Playground`, `session.transcript`, Instruments | `references/foundation-models-framework.md` |
| Local vs cloud routing | `GenerationPath` enum pattern | `references/routing-local-vs-bigger-model.md` |

## Workflow

1. **Check model limitations first.** Verify the task is within the on-device model's capabilities using the tables in `references/model-capabilities-and-limits.md`. If it is not, design an escalation path before writing code.
2. **Classify the request.** Use Foundation Models for on-device text generation, ImagePlayground for image generation, and App Intents/Shortcuts for the "Use Model" automation action.
3. **Check platform support and runtime readiness.** Use `isAvailable` and `availability` states, then design fallback UI for unavailable states.
4. **Design instructions and prompts.** Set behavioral constraints in `instructions:` (developer-only). Keep prompts concise with length qualifiers. See `references/prompt-design-and-safety.md`.
5. **Design `@Generable` types for structured output.** Use `@Generable` with `@Guide` constraints instead of asking the model to produce JSON. See `references/generable-and-guided-generation.md`.
6. **Stream all user-facing generation.** Use `streamResponse(to:)` instead of `respond(to:)` for any output the user sees. See the streaming section in `references/foundation-models-framework.md`.
7. **Add tools only as needed.** Register tools when the model needs data or actions it cannot perform alone. See `references/tool-calling.md`.
8. **Decide whether to route to a larger model.** For Apple-managed routing, use App Intents "Use Model." For in-app escalation, use an explicit backend model path. See `references/routing-local-vs-bigger-model.md`.
9. **Validate behavior on physical devices** and include robust error handling for guardrail violations, context size, language support, and tool failures.

## References

- **Framework core (sessions, availability, streaming, performance):** `references/foundation-models-framework.md`
- **Model capabilities and limitations:** `references/model-capabilities-and-limits.md`
- **Structured output with @Generable and @Guide:** `references/generable-and-guided-generation.md`
- **Tool calling (Tool protocol, dynamic tools, tool graphs):** `references/tool-calling.md`
- **Prompt design, safety, and error handling:** `references/prompt-design-and-safety.md`
- **Image generation (ImagePlayground, ImageCreator):** `references/image-playground.md`
- **Local vs larger-model routing strategy:** `references/routing-local-vs-bigger-model.md`

## Execution Rules

- Prefer official Apple docs and WWDC sources for API behavior.
- Treat Foundation Models app APIs as on-device unless Apple docs explicitly document a server-routing API for app code.
- Re-verify docs for "latest" requests because Apple Intelligence behavior can change across OS releases.
- Keep prompts concise and structured to reduce token use and latency.
- **Check model limitations before implementing.** If the task involves world knowledge, math, code generation, or long-form writing, design an escalation path — do not rely on the on-device model.
- **Stream all user-facing generation.** Use `streamResponse(to:)` for any output displayed to the user. Reserve `respond(to:)` for background processing.
- **Use `@Generable` for structured output, not JSON in prompts.** The model uses constrained decoding with `@Generable` types, guaranteeing valid output. Prompt-based JSON is unreliable.
