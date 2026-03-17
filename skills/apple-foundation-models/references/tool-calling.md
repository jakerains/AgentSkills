# Tool Calling

## Table of Contents

- [Overview](#overview)
- [The Tool Protocol](#the-tool-protocol)
- [Complete Tool Example](#complete-tool-example)
- [Registering Tools with a Session](#registering-tools-with-a-session)
- [Tool Output Types](#tool-output-types)
- [Dynamic Tools](#dynamic-tools)
- [Tool Graph Execution](#tool-graph-execution)
- [Debugging with Transcript](#debugging-with-transcript)
- [Best Practices](#best-practices)
- [Sources](#sources)

## Overview

Tools let the on-device model call into your app code to fetch data, perform actions, or access services. The model decides when to call a tool based on the tool's name, description, and the user's prompt. Tool arguments are `@Generable` types, so they benefit from constrained decoding.

Use tools when:
- The model needs data it doesn't have (weather, user profile, database records).
- The task requires an action (send message, toggle setting, create reminder).
- You want to extend the model's capabilities beyond text generation (math, search, API calls).

## The Tool Protocol

Every tool conforms to the `Tool` protocol:

```swift
import FoundationModels

struct MyTool: Tool {
    // Display name shown in debugging/transcript
    let name = "my_tool"

    // The model reads this to decide when to call the tool.
    // Keep it short and specific.
    let description = "Looks up the current weather for a given city."

    // The arguments type must be @Generable
    @Generable
    struct Arguments {
        @Guide(description: "City name, e.g. San Francisco")
        var city: String
    }

    // Called when the model invokes this tool
    func call(arguments: Arguments) async throws -> ToolOutput {
        // Your app logic here
        let weather = await WeatherService.fetch(city: arguments.city)
        return .init(stringLiteral: "Currently \(weather.temp)°F and \(weather.condition) in \(arguments.city)")
    }
}
```

## Complete Tool Example

```swift
import FoundationModels

struct LookupContactTool: Tool {
    let name = "lookup_contact"
    let description = "Finds a contact by name and returns their phone number and email."

    @Generable
    struct Arguments {
        @Guide(description: "Full or partial name to search for")
        var name: String
    }

    func call(arguments: Arguments) async throws -> ToolOutput {
        guard let contact = ContactStore.shared.find(name: arguments.name) else {
            return "No contact found matching '\(arguments.name)'."
        }
        return "Name: \(contact.fullName), Phone: \(contact.phone), Email: \(contact.email)"
    }
}

// Register and use:
let session = LanguageModelSession(tools: [LookupContactTool()])
let response = try await session.respond(
    to: "What's Jamie's phone number?"
)
// The model calls lookup_contact(name: "Jamie"), gets the result,
// and formulates a natural language response.
```

## Registering Tools with a Session

Pass tools when creating a session. The model sees all registered tools for every request in that session.

```swift
let session = LanguageModelSession(
    model: .default,
    instructions: "You are a helpful assistant with access to the user's contacts and calendar.",
    tools: [
        LookupContactTool(),
        SearchCalendarTool(),
        CreateReminderTool()
    ]
)
```

**Tip:** Only register tools the model actually needs. Extra tools increase token usage (their schemas are included in the context) and may confuse the model.

## Tool Output Types

The `call` method returns `ToolOutput`, which can be created from:

| Source | Example |
|--------|---------|
| String literal | `return "Temperature is 72°F"` |
| String variable | `return .init(stringLiteral: result)` |
| `GeneratedContent` | For complex structured responses |

Keep tool output **concise**. The output is injected back into the context window, so verbose outputs consume tokens and may cause context overflow.

## Dynamic Tools

For tools whose definitions change at runtime (e.g., user-configured actions, plugin systems), use dynamic tool creation:

```swift
import FoundationModels

let dynamicTool = DynamicTool(
    name: "search_inventory",
    description: "Searches the store inventory for a product by name.",
    argumentSchema: .object([
        "query": .string(description: "Product name to search for")
    ])
) { arguments in
    let query = arguments["query"] as? String ?? ""
    let results = await InventoryService.search(query)
    return "Found \(results.count) items: \(results.map(\.name).joined(separator: ", "))"
}

let session = LanguageModelSession(tools: [dynamicTool])
```

## Tool Graph Execution

When the model determines it needs multiple tools, it builds an execution graph:

- **Parallel execution:** Independent tool calls run concurrently. If the model needs both weather and calendar data, both tools fire at the same time.
- **Serial execution:** Dependent tool calls run in sequence. If tool B needs output from tool A, the model waits for A to complete.
- **Multi-step chains:** The model can call tools, read their outputs, then call more tools before producing a final response.

You do not control the execution order — the model decides. Design tools to be independent when possible for best performance.

## Debugging with Transcript

Use `session.transcript` to inspect the full tool call graph after a response completes. This is invaluable for debugging unexpected model behavior.

```swift
let response = try await session.respond(to: "Schedule lunch with Jamie tomorrow.")

// Inspect what happened:
for entry in session.transcript {
    switch entry {
    case .userMessage(let text):
        print("User: \(text)")
    case .assistantMessage(let text):
        print("Assistant: \(text)")
    case .toolCall(let name, let args, let output):
        print("Tool call: \(name)(\(args)) → \(output)")
    }
}
```

## Best Practices

| Practice | Rationale |
|----------|-----------|
| Keep `description` under 100 characters | Longer descriptions consume tokens and may confuse the model |
| Keep tool output concise (under 200 tokens) | Output is injected into the 4096-token context window |
| Use `@Guide` descriptions on all arguments | Helps the model produce valid arguments |
| Handle errors gracefully in `call` | Return an error string instead of throwing when possible — thrown errors stop generation |
| Log or inspect `session.transcript` in debug builds | Reveals why the model called (or didn't call) a tool |
| Register only necessary tools per session | Unused tools waste context and increase latency |
| Design tools to be side-effect-aware | Tools that create/modify data should confirm actions in their output |
| Test tools in isolation before session integration | Verify `call(arguments:)` works correctly with expected and edge-case inputs |

## Sources

- https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling
- https://developer.apple.com/documentation/foundationmodels/tool
- https://developer.apple.com/documentation/foundationmodels/tooloutput
- WWDC25 Session: Meet the Foundation Models framework
- WWDC25 Session: Build an agent with the Foundation Models framework
