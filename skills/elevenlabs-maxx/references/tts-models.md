# Text-to-Speech Models & Parameters

Complete reference for ElevenLabs TTS models and voice settings.

## Models Overview

| Model ID | Latency | Languages | Char Limit | Best For |
|----------|---------|-----------|------------|----------|
| `eleven_v3` | Higher | 70+ | 5,000 | Emotional, dramatic, multi-speaker dialogue |
| `eleven_multilingual_v2` | ~500ms | 29 | 10,000 | High quality, long-form, consistent |
| `eleven_flash_v2_5` | ~75ms | 32 | 40,000 | Real-time, agents, low cost |
| `eleven_turbo_v2_5` | ~250ms | 32 | 40,000 | Balanced quality/speed |
| `eleven_flash_v2` | ~75ms | English | 30,000 | English-only, fast |
| `eleven_turbo_v2` | ~250ms | English | 30,000 | English-only, balanced |

## Model Details

### Eleven v3 (Alpha)
Our most emotionally expressive model.

**Best for:**
- Audiobook production with complex emotional delivery
- Character discussions/dialogue
- Dramatic performances

**Features:**
- Natural multi-speaker dialogue
- High emotional range
- 70+ languages
- Audio tags supported ([laughs], [whispers], [slow])

**Limitations:**
- Not for real-time (higher latency)
- 5,000 character limit
- Alpha status (subject to change)

### Multilingual v2
Most stable, high-quality model for production.

**Best for:**
- Professional content creation
- Corporate videos, e-learning
- Long-form narration
- Multilingual projects

**Supported Languages (29):**
English (USA, UK, Australia, Canada), Japanese, Chinese, German, Hindi, French (France, Canada), Korean, Portuguese (Brazil, Portugal), Italian, Spanish (Spain, Mexico), Indonesian, Dutch, Turkish, Filipino, Polish, Swedish, Bulgarian, Romanian, Arabic (Saudi Arabia, UAE), Czech, Greek, Finnish, Croatian, Malay, Slovak, Danish, Tamil, Ukrainian, Russian

### Flash v2.5
Fastest model for real-time applications.

**Best for:**
- Conversational AI agents
- Interactive applications
- High-frequency requests
- Cost-sensitive projects (50% cheaper)

**Additional Languages (vs v2):**
Hungarian, Norwegian, Vietnamese

**Note:** Numbers aren't normalized by default. For phone numbers/dates, use Multilingual v2 or pre-normalize text.

### Turbo v2.5
Balanced quality and speed.

**Best for:**
- When Flash quality isn't sufficient
- But Multilingual latency is too high
- Good default for most applications

## Voice Settings

### Core Parameters

```python
voice_settings = {
    "stability": 0.5,        # 0-1: Higher = more consistent, less emotional
    "similarity_boost": 0.75, # 0-1: Higher = closer to original voice
    "style": 0.0,            # 0-1: Higher = more expressive (adds latency)
    "use_speaker_boost": True # Increases similarity at cost of latency
}
```

### Parameter Guide

| Parameter | Low (0.0-0.3) | Medium (0.4-0.6) | High (0.7-1.0) |
|-----------|---------------|------------------|----------------|
| **Stability** | Emotional, varied | Balanced | Consistent, monotone |
| **Similarity** | More variation | Balanced | Closer to original |
| **Style** | Conservative | Moderate flair | Highly expressive |

### Use Case Presets

**Customer Service:**
```python
stability=0.7, similarity_boost=0.8, style=0.0
```

**Audiobook Narration:**
```python
stability=0.5, similarity_boost=0.75, style=0.3
```

**Character Voice Acting:**
```python
stability=0.3, similarity_boost=0.6, style=0.5
```

**Consistent IVR/Announcements:**
```python
stability=0.9, similarity_boost=0.9, style=0.0
```

## Speed Control

```python
speed=1.0  # Range: 0.7 to 1.2
```

- **0.7-0.9**: Slower, deliberate speech
- **1.0**: Normal speed
- **1.1-1.2**: Faster-paced speech

Extreme values may impact quality.

## Output Formats

| Format | Description | Tier |
|--------|-------------|------|
| `mp3_22050_32` | MP3, 22.05kHz, 32kbps | All |
| `mp3_44100_64` | MP3, 44.1kHz, 64kbps | All |
| `mp3_44100_128` | MP3, 44.1kHz, 128kbps (default) | All |
| `mp3_44100_192` | MP3, 44.1kHz, 192kbps | Creator+ |
| `pcm_16000` | PCM, 16kHz | All |
| `pcm_22050` | PCM, 22.05kHz | All |
| `pcm_24000` | PCM, 24kHz | All |
| `pcm_44100` | PCM, 44.1kHz | Pro+ |
| `ulaw_8000` | μ-law, 8kHz (Twilio) | All |

## Request Stitching

For seamless audio across multiple requests:

```python
# Method 1: Previous text context
audio = client.text_to_speech.convert(
    text="Current sentence.",
    previous_text="The sentence before this one.",
    next_text="The sentence after this one.",
    ...
)

# Method 2: Request IDs (more accurate)
audio = client.text_to_speech.convert(
    text="Current sentence.",
    previous_request_ids=["request_id_1"],
    next_request_ids=["request_id_3"],
    ...
)
```

## Text Normalization

Control how numbers/dates are spoken:

```python
apply_text_normalization="auto"  # "auto", "on", "off"
```

- **auto**: Model decides
- **on**: Always normalize (e.g., "123" → "one hundred twenty-three")
- **off**: Read literally

For Flash models, normalization is off by default for latency.

## Pronunciation Dictionaries

Add custom pronunciations:

```python
audio = client.text_to_speech.convert(
    text="The CEO of ACME announced...",
    pronunciation_dictionary_locators=[
        {"dictionary_id": "dict_123", "version_id": "v1"}
    ],
    ...
)
```

- Up to 3 dictionaries per request
- Applied in order

## Best Practices

1. **Model Selection**: Start with `eleven_multilingual_v2`, use Flash for real-time
2. **Voice Matching**: Test multiple voices with your content
3. **Chunking**: Split long text at natural breaks (paragraphs, sentences)
4. **Rate Limiting**: Respect concurrency limits for your plan
5. **Caching**: Cache generated audio when content is static

## Common Issues

**Audio sounds robotic:**
- Lower stability (try 0.3-0.5)
- Add style (0.2-0.4)

**Inconsistent pronunciations:**
- Higher stability (0.7-0.8)
- Use pronunciation dictionary

**Numbers read incorrectly:**
- Use Multilingual v2 instead of Flash
- Pre-normalize numbers in text
- Use `apply_text_normalization="on"` (Enterprise only for Flash)
