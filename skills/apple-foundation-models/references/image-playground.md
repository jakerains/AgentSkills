# Image Playground Reference

## Table of Contents

- [Scope](#scope)
- [API Surface and Availability Snapshot](#api-surface-and-availability-snapshot)
- [Integration Modes](#integration-modes)
- [Availability Check Pattern](#availability-check-pattern)
- [SwiftUI Sheet Pattern](#swiftui-sheet-pattern)
- [UIKit/AppKit Pattern](#uikitappkit-pattern)
- [Programmatic Pattern with ImageCreator](#programmatic-pattern-with-imagecreator)
- [Styles and Content Inputs](#styles-and-content-inputs)
- [iOS 26 Updates](#ios-26-updates)
- [Error and UX Guidance](#error-and-ux-guidance)
- [Sources](#sources)

## Scope

Use this reference when integrating Apple's on-device image generation features.

## API Surface and Availability Snapshot

- `ImagePlayground` framework availability: iOS 18.1+, iPadOS 18.1+, macOS 15.1+, Mac Catalyst 18.1+, visionOS 2.4+.
- `ImageCreator` availability: iOS 18.4+, iPadOS 18.4+, macOS 15.4+, Mac Catalyst 18.4+, visionOS 2.4+.
- Images are generated on device.

## Integration Modes

1. SwiftUI sheet APIs (`imagePlaygroundSheet`) for quick system UI integration.
2. `ImagePlaygroundViewController` for UIKit/AppKit control with delegate callbacks.
3. `ImageCreator` for fully programmatic generation via async sequences.

## Availability Check Pattern

```swift
guard ImagePlaygroundViewController.isAvailable else {
    // Hide or disable image generation feature.
    return
}
```

## SwiftUI Sheet Pattern

Use concept text or `[ImagePlaygroundConcept]` and receive a generated image URL on completion.

```swift
.imagePlaygroundSheet(
    isPresented: $isPresented,
    concepts: [.text("A cozy cafe in the rain")],
    sourceImage: nil,
    onCompletion: { url in
        // Load and persist image from URL.
    },
    onCancellation: {
        // Handle cancellation.
    }
)
```

## UIKit/AppKit Pattern

- Configure `ImagePlaygroundViewController` with:
- `concepts`
- optional `sourceImage`
- `selectedGenerationStyle` and `allowedGenerationStyles`
- Implement delegate callbacks for completion and cancellation.

## Programmatic Pattern with ImageCreator

```swift
let creator = try await ImageCreator()
let concepts: [ImagePlaygroundConcept] = [.text("Minimal poster of a mountain skyline")]

for try await generated in creator.images(
    for: concepts,
    style: .illustration,
    limit: 2
) {
    // Handle generated.url and metadata.
}
```

## Styles and Content Inputs

### Core Styles

- Core style constants include `.animation`, `.illustration`, and `.sketch`.
- **Always query `availableStyles` at runtime** rather than hardcoding style constants, as available styles vary by OS version and device.

```swift
let available = ImagePlaygroundViewController.availableStyles
// Use only styles present in this array
```

- Support optional source images to guide generation where appropriate.
- Keep concept text concise and specific for better results.

## iOS 26 Updates

iOS 26 and iPadOS 26 introduce significant Image Playground enhancements:

### ChatGPT Integration Styles

New styles powered by ChatGPT integration. These extend the existing on-device styles with:

- **Anime** — Japanese animation aesthetic
- **Oil Painting** — Classical painterly style
- **Vector** — Clean vector illustration look
- **Print** — Printed/lithographic quality
- **Watercolor** — Watercolor painting effect
- **"Any Style" mode** — User-defined style via text description

**Important:** ChatGPT-powered styles require an active network connection. The on-device styles (`.animation`, `.illustration`, `.sketch`) remain available offline.

### Genmoji Creation

Image Playground now supports creating custom Genmoji — personalized emoji generated from descriptions and optional photos.

### Other Improvements

- Improved generation quality across all styles.
- Image labeling for accessibility metadata on generated images.
- Extended style options may appear in system surfaces (Messages, Freeform, etc.).

### Runtime Style Discovery

Do not hardcode new iOS 26 style constants. Instead, always discover available styles at runtime:

```swift
// Correct — adapts to OS version and device capabilities
let styles = ImagePlaygroundViewController.availableStyles

// Incorrect — will crash on earlier OS versions
// let style = .anime  // ❌ Don't hardcode new styles
```

## Error and UX Guidance

- Handle `ImageCreator.Error` cases and cancellation cleanly.
- Offer fallback UI when unavailable or unsupported by language/device.
- Keep generation work on the main user flow lightweight; persist outputs quickly.
- For ChatGPT-powered styles, handle network unavailability gracefully — fall back to on-device styles.

## Sources

- https://developer.apple.com/documentation/imageplayground
- https://developer.apple.com/documentation/imageplayground/imageplaygroundviewcontroller
- https://developer.apple.com/documentation/imageplayground/imagecreator
- https://developer.apple.com/documentation/imageplayground/imageplaygroundstyle
- https://developer.apple.com/apple-intelligence/get-started/
- https://developer.apple.com/apple-intelligence/whats-new/
