# Speech-to-Text (Scribe) Reference

Complete guide to ElevenLabs Scribe v2 speech recognition.

## Models

### Scribe v2 (Batch)
State-of-the-art transcription model.

| Feature | Specification |
|---------|---------------|
| Languages | 90+ |
| Keyterm prompting | Up to 100 terms |
| Entity detection | 56 entity types |
| Speaker diarization | Up to 48 speakers |
| Word timestamps | Yes |
| File size limit | 3 GB |
| Duration limit | 10 hours |

### Scribe v2 Realtime
Live transcription via WebSocket.

| Feature | Specification |
|---------|---------------|
| Latency | ~150ms |
| Languages | 90+ |
| Audio formats | PCM (8-48kHz), μ-law |
| Word timestamps | Yes |
| Auto language detection | Yes |

## Basic Usage

### Python SDK
```python
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="your-api-key")

# Basic transcription
result = client.speech_to_text.convert(
    file=open("audio.mp3", "rb"),
    model_id="scribe_v2"
)

print(result.text)
print(result.language_code)
print(result.language_probability)

# With speaker diarization
result = client.speech_to_text.convert(
    file=open("meeting.mp3", "rb"),
    model_id="scribe_v2",
    diarize=True
)

for word in result.words:
    print(f"{word.speaker_id}: {word.text} ({word.start}-{word.end})")
```

### MCP Tool
```
mcp__ElevenLabs__speech_to_text
- input_file_path: "/path/to/audio.mp3"
- diarize: true
- language_code: "eng" (optional, auto-detect if omitted)
- save_transcript_to_file: true
- return_transcript_to_client_directly: false
```

## Response Format

```json
{
  "language_code": "en",
  "language_probability": 0.98,
  "text": "Full transcript text here...",
  "words": [
    {
      "text": "Hello",
      "start": 0.119,
      "end": 0.359,
      "type": "word",
      "speaker_id": "speaker_0"
    },
    {
      "text": " ",
      "start": 0.359,
      "end": 0.399,
      "type": "spacing",
      "speaker_id": "speaker_0"
    }
  ]
}
```

### Word Types
- `word`: Spoken word
- `spacing`: Space between words
- `audio_event`: Non-speech sounds (laughter, applause)

## Advanced Features

### Keyterm Prompting
Bias the model toward specific words/phrases.

```python
result = client.speech_to_text.convert(
    file=open("medical_recording.mp3", "rb"),
    model_id="scribe_v2",
    keyterms=["acetaminophen", "ibuprofen", "Dr. Smith", "Patient ID 12345"]
)
```

- Up to 100 keyterms
- Context-aware (won't force incorrect transcription)
- Great for: product names, technical terms, proper nouns

### Entity Detection
Automatically detect and timestamp entities.

```python
result = client.speech_to_text.convert(
    file=open("call_center.mp3", "rb"),
    model_id="scribe_v2",
    detect_entities=["phone_number", "email", "credit_card_number", "person_name"]
)
```

**Supported Entity Types (56 total):**
- Personal: person_name, ssn, date_of_birth
- Financial: credit_card_number, bank_account, routing_number
- Contact: phone_number, email, address
- Medical: medical_condition, medication, procedure
- Identifiers: order_id, customer_id, tracking_number

### Multichannel Transcription
Transcribe each audio channel separately.

```python
result = client.speech_to_text.convert(
    file=open("stereo_call.wav", "rb"),
    model_id="scribe_v2",
    multichannel=True  # Up to 5 channels
)
```

Each channel gets assigned a speaker ID based on channel number.

## Realtime Transcription

### WebSocket Connection
```python
import asyncio
import websockets
import json

async def transcribe_realtime():
    uri = "wss://api.elevenlabs.io/v1/speech-to-text/stream"

    async with websockets.connect(uri, extra_headers={
        "xi-api-key": "your-api-key"
    }) as ws:
        # Send config
        await ws.send(json.dumps({
            "model_id": "scribe_v2_realtime",
            "language_code": "en",
            "sample_rate": 16000,
            "encoding": "pcm"
        }))

        # Stream audio chunks
        async for audio_chunk in get_audio_stream():
            await ws.send(audio_chunk)

            # Receive partial transcripts
            response = await ws.recv()
            transcript = json.loads(response)
            print(transcript["text"])
```

### Audio Requirements
| Format | Sample Rates |
|--------|-------------|
| PCM | 8kHz, 16kHz, 22.05kHz, 24kHz, 44.1kHz, 48kHz |
| μ-law | 8kHz |

### VAD (Voice Activity Detection)
Automatic speech segmentation:
- Detects silence to create transcript segments
- Configurable sensitivity
- Or use manual commit control

## Supported Languages (90+)

### Excellent Accuracy (≤5% WER)
English, Japanese, Chinese (Mandarin), German, French, Spanish, Portuguese, Italian, Dutch, Polish, Swedish, Danish, Finnish, Norwegian, Czech, Slovak, Romanian, Bulgarian, Croatian, Greek, Indonesian, Malay, Turkish, Korean, Vietnamese, Hungarian, Ukrainian, Russian, Kannada, Malayalam, Latvian, Estonian, Icelandic, Macedonian, Belarusian, Bosnian, Catalan, Galician

### High Accuracy (5-10% WER)
Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Nepali, Persian, Armenian, Georgian, Kazakh, Lithuanian, Slovenian, Serbian, Swahili, Filipino, Maltese, Odia, Azerbaijani, Cantonese

### Good Accuracy (10-20% WER)
Arabic, Hebrew, Thai, Burmese, Korean, Kyrgyz, Assamese, Afrikaans, Welsh, Maori, Javanese, Tajik, Uzbek, Occitan, Luxembourgish, Hausa

## Webhooks

Configure webhook endpoints to receive results asynchronously:

1. Set up webhook URL in ElevenLabs dashboard
2. Send transcription request with `webhook=True`
3. Receive POST with transcript when complete

Useful for long files or batch processing.

## Pricing & Billing

- Billed per hour of audio
- Keyterm prompting: Additional cost
- Entity detection: Additional cost
- See [elevenlabs.io/pricing](https://elevenlabs.io/pricing)

## Best Practices

1. **Audio Quality**: Clean audio produces best results
2. **Language Hints**: Provide language_code for single-language content
3. **Chunking**: For very long files, consider splitting
4. **Keyterms**: Add domain-specific vocabulary
5. **Diarization**: Use for multi-speaker content

## Supported File Types

**Audio:**
AAC, AIFF, FLAC, M4A, MP3, OGG, OPUS, WAV, WEBM

**Video:**
MP4, AVI, MKV, MOV, WMV, FLV, WEBM, MPEG, 3GPP

Video files will have audio extracted automatically.
