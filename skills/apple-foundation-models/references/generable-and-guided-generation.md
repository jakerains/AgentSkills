# Generable and Guided Generation

## Table of Contents

- [Overview](#overview)
- [Supported Types](#supported-types)
- [The @Generable Macro](#the-generable-macro)
- [The @Guide Macro](#the-guide-macro)
- [Complete Example](#complete-example)
- [Nested Generable Types](#nested-generable-types)
- [Enum Support](#enum-support)
- [Property Ordering for Streaming](#property-ordering-for-streaming)
- [Streaming with PartiallyGenerated](#streaming-with-partiallygenerated)
- [Anti-Patterns](#anti-patterns)
- [Sources](#sources)

## Overview

Guided generation lets you get typed Swift structs and enums directly from the model instead of parsing raw strings. The `@Generable` macro makes any Swift type model-output-compatible, and `@Guide` constrains individual properties.

**Always prefer `@Generable` over asking the model to produce JSON in a prompt.** The model uses constrained decoding to guarantee valid output that matches your schema — prompt-based JSON is unreliable and wastes tokens.

## Supported Types

The following Swift types can be used as `@Generable` properties:

| Type | Notes |
|------|-------|
| `String` | Most common; use `@Guide` to constrain length |
| `Int` | Integer values |
| `Float` | Floating-point values |
| `Double` | Double-precision floating-point |
| `Bool` | True/false flags |
| `[String]` | Arrays of strings; use `@Guide(.maximumCount(N))` to limit |
| `[Int]`, `[Float]`, etc. | Arrays of supported primitives |
| Nested `@Generable` structs | Compose complex types from smaller generable types |
| `@Generable` enums | Categorical outputs with fixed cases |
| `Optional<T>` | Optional properties (model may omit them) |
| Recursive `@Generable` | A generable type that references itself (e.g., tree structures) |

## The @Generable Macro

Apply `@Generable` to a struct or enum to make it available for guided generation.

```swift
import FoundationModels

@Generable
struct MovieReview {
    var sentiment: String
    var score: Int
    var keyPoints: [String]
}
```

**Requirements:**
- All stored properties must be supported types (see table above).
- The type must be a struct or enum — classes are not supported.
- Import `FoundationModels` in any file that uses `@Generable`.

## The @Guide Macro

Use `@Guide` to add constraints and descriptions to individual properties. This helps the model understand what values to produce.

| Constraint | Usage | Effect |
|-----------|-------|--------|
| Description string | `@Guide(description: "A 1-5 star rating")` | Tells the model what the property represents |
| `.count(N)` | `@Guide(.count(3))` | Exactly N items (arrays) or N characters (strings, depending on context) |
| `.maximumCount(N)` | `@Guide(.maximumCount(5))` | At most N items in an array |
| `.minimumCount(N)` | `@Guide(.minimumCount(1))` | At least N items in an array |
| Combined | `@Guide(.maximumCount(10), description: "Key topics")` | Multiple constraints together |

## Complete Example

```swift
import FoundationModels

@Generable
struct RecipeCard {
    @Guide(description: "Recipe name, max 60 characters")
    var title: String

    @Guide(description: "Brief one-sentence description")
    var summary: String

    @Guide(.maximumCount(10), description: "Ingredient list")
    var ingredients: [String]

    @Guide(.maximumCount(8), description: "Step-by-step cooking instructions")
    var steps: [String]

    @Guide(description: "Estimated minutes to prepare and cook")
    var totalMinutes: Int

    @Guide(description: "Difficulty: easy, medium, or hard")
    var difficulty: String
}

// Usage:
let session = LanguageModelSession()
let recipe = try await session.respond(
    to: "Create a recipe for a quick weeknight pasta dinner.",
    generating: RecipeCard.self
)
print(recipe.title)       // Typed access
print(recipe.ingredients) // [String] array
```

## Nested Generable Types

Compose complex output by nesting `@Generable` types inside each other.

```swift
@Generable
struct NutritionInfo {
    var calories: Int
    var proteinGrams: Int
    var isVegetarian: Bool
}

@Generable
struct DetailedRecipe {
    var title: String
    var summary: String

    @Guide(.maximumCount(10))
    var ingredients: [String]

    @Guide(.maximumCount(8))
    var steps: [String]

    var nutrition: NutritionInfo  // Nested @Generable type
}
```

## Enum Support

Use `@Generable` enums for categorical outputs where the model must pick from fixed options.

```swift
@Generable
enum Sentiment {
    case positive
    case negative
    case neutral
    case mixed
}

@Generable
struct ReviewAnalysis {
    var sentiment: Sentiment
    var confidence: Double

    @Guide(description: "One-sentence justification for the sentiment classification")
    var reason: String
}
```

## Property Ordering for Streaming

When using streaming (see below), the model generates properties **in declaration order**. Place contextual or auxiliary fields **last** so that the most important content streams first and dependent fields have more context.

```swift
@Generable
struct ArticleSummary {
    // Stream these first — user sees content immediately
    var headline: String
    var bulletPoints: [String]

    // These come last — they benefit from seeing the above
    @Guide(description: "Category tag based on the content above")
    var category: String

    @Guide(description: "Relevance score from 1-10")
    var relevanceScore: Int
}
```

## Streaming with PartiallyGenerated

Stream guided generation results as they are produced. Each yielded value is a `PartiallyGenerated<T>` with optional properties that fill in progressively.

```swift
let session = LanguageModelSession()

let stream = session.streamResponse(
    to: "Summarize this article about climate change.",
    generating: ArticleSummary.self
)

for try await partial in stream {
    // partial.headline may be nil initially, then populated
    if let headline = partial.headline {
        updateUI(headline: headline)
    }
    if let bullets = partial.bulletPoints {
        updateUI(bullets: bullets)
    }
}

// After the stream completes, access the final typed result:
let final = try await stream.result
```

For SwiftUI integration, see the streaming patterns in `references/foundation-models-framework.md`.

## Anti-Patterns

**Never do these:**

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|-----------------|
| Ask the model to "return JSON" in the prompt | Model may produce invalid JSON, wastes tokens on formatting | Use `@Generable` with `session.respond(to:generating:)` |
| Parse a `String` response into a struct manually | Fragile, error-prone, no type safety | Use `@Generable` for direct typed output |
| Put all fields in a single flat String | Loses structure, harder to stream | Design a `@Generable` struct with discrete properties |
| Use `@Generable` for free-form creative writing | Constraints reduce creative quality | Use plain `session.respond(to:)` for open-ended text |
| Omit `@Guide` descriptions on ambiguous properties | Model guesses wrong about expected format | Always describe non-obvious properties |

## Sources

- https://developer.apple.com/documentation/foundationmodels/generating-structured-output-with-guided-generation
- https://developer.apple.com/documentation/foundationmodels/generable()
- https://developer.apple.com/documentation/foundationmodels/guide(_:)
- WWDC25 Session: Meet the Foundation Models framework
- WWDC25 Session: Generate structured output with Foundation Models
