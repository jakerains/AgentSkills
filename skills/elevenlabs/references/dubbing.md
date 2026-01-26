# Dubbing Guide

Translate audio and video while preserving speaker identity, emotion, timing, and tone.

## Overview

ElevenLabs dubbing translates content across 32 languages while maintaining:
- Speaker voice characteristics
- Emotional delivery
- Timing and lip-sync
- Background audio (music, effects)

**Use Cases:**
- International content distribution
- Localization for new markets
- Podcast translation
- Video course localization

## Capabilities

| Feature | Description |
|---------|-------------|
| Languages | 32 supported |
| Speaker separation | Multiple speakers, overlapping speech |
| Voice preservation | Maintains original speaker identity |
| Background audio | Preserves music, effects, ambient |
| Editing | Modify transcripts and translations |

## Usage Methods

### 1. Dubbing Studio (UI)
Interactive editing in the ElevenLabs dashboard:
- Upload file or paste URL
- Review/edit transcripts
- Adjust translations
- Regenerate specific segments
- Download dubbed content

**Limits:** 500MB, 45 minutes

### 2. API Integration
Programmatic dubbing for automation:

```python
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="your-api-key")

# Start dubbing job
dubbing = client.dubbing.dub_a_video_or_an_audio_file(
    file=open("video.mp4", "rb"),
    target_lang="es",  # Spanish
    source_lang="en",  # English (optional, auto-detect)
    num_speakers=2,    # Expected speakers (optional)
    watermark=False    # Add watermark (reduces cost)
)

# Check status
status = client.dubbing.get_dubbing_project_metadata(
    dubbing_id=dubbing.dubbing_id
)

# Download when complete
if status.status == "dubbed":
    audio = client.dubbing.get_dubbed_file(
        dubbing_id=dubbing.dubbing_id,
        language_code="es"
    )
```

**Limits:** 1GB, 2.5 hours

### 3. ElevenLabs Productions
Human-verified dubbing service for professional needs.
Contact: productions@elevenlabs.io

## Supported Languages

| # | Language | Code |
|---|----------|------|
| 1 | English | en |
| 2 | Hindi | hi |
| 3 | Portuguese | pt |
| 4 | Chinese | zh |
| 5 | Spanish | es |
| 6 | French | fr |
| 7 | German | de |
| 8 | Japanese | ja |
| 9 | Arabic | ar |
| 10 | Russian | ru |
| 11 | Korean | ko |
| 12 | Indonesian | id |
| 13 | Italian | it |
| 14 | Dutch | nl |
| 15 | Turkish | tr |
| 16 | Polish | pl |
| 17 | Swedish | sv |
| 18 | Filipino | fil |
| 19 | Malay | ms |
| 20 | Romanian | ro |
| 21 | Ukrainian | uk |
| 22 | Greek | el |
| 23 | Czech | cs |
| 24 | Danish | da |
| 25 | Finnish | fi |
| 26 | Bulgarian | bg |
| 27 | Croatian | hr |
| 28 | Slovak | sk |
| 29 | Tamil | ta |

## Supported Sources

### File Uploads
- **Video**: MP4, AVI, MKV, MOV, WMV, FLV, WEBM, MPEG, 3GPP
- **Audio**: MP3, WAV, FLAC, AAC, OGG, M4A

### URL Sources
- YouTube
- X (Twitter)
- TikTok
- Vimeo
- Direct URLs to media files

## Key Features

### Speaker Separation
- Automatically detects multiple speakers
- Handles overlapping speech
- Each speaker maintains unique voice in translation
- Supports up to 9 speakers (recommended max)

### Voice Preservation
- Clones each speaker's voice characteristics
- Maintains emotional tone and delivery
- Preserves accent nuances where possible

### Background Audio Handling
- Separates dialogue from soundtrack
- Music and effects remain unchanged
- No need for re-mixing

### Transcript Editing
- Review and correct source transcription
- Edit translations before synthesis
- Regenerate individual segments
- Fine-tune timing

## Workflow

### Basic Dubbing
1. Upload video/audio or provide URL
2. Select source language (or auto-detect)
3. Select target language(s)
4. Wait for processing
5. Download dubbed content

### With Editing
1. Upload content
2. Review auto-generated transcript
3. Correct any transcription errors
4. Review auto-translation
5. Edit translations as needed
6. Adjust voice settings per segment
7. Regenerate problematic segments
8. Download final version

## Cost Optimization

### Reduce Credit Usage
- **Watermark**: Use watermark option for video (cheaper)
- **Partial dubbing**: Select only portions to dub
- **Segment regeneration**: Fix specific segments, not whole file
- **Audio only**: Dub audio track, less expensive than video

### Plan Requirements
- **Audio dubbing**: Creator plan or higher
- **Video with watermark**: Available at lower tiers
- **Full video dubbing**: Creator plan or higher

## Best Practices

### Source Content
- Clean audio quality produces better results
- Minimize background noise
- Clear speaker separation
- Consistent audio levels

### Speaker Management
- Specify expected number of speakers
- Maximum 9 speakers recommended
- Complex multi-speaker may need multiple passes

### Quality Assurance
- Always review transcripts
- Check critical terminology
- Verify emotional delivery in target language
- Test with native speakers when possible

### File Preparation
- Trim unnecessary content before dubbing
- Split very long content into chapters
- Ensure adequate audio quality

## Limitations

- **Max speakers**: 9 recommended for quality
- **UI limits**: 500MB, 45 minutes
- **API limits**: 1GB, 2.5 hours
- **Real-time**: Not available (batch processing only)

## Pricing

- Billed per minute of source content
- Target language count affects cost
- Watermarked video is cheaper
- See [elevenlabs.io/pricing](https://elevenlabs.io/pricing)

## API Endpoints

### Create Dubbing
```
POST /v1/dubbing
- file or url (required)
- target_lang (required)
- source_lang (optional)
- num_speakers (optional)
- watermark (optional)
```

### Get Status
```
GET /v1/dubbing/{dubbing_id}
```

### Get Transcript
```
GET /v1/dubbing/{dubbing_id}/transcript/{language_code}
```

### Download Dubbed File
```
GET /v1/dubbing/{dubbing_id}/audio/{language_code}
```

### Delete Project
```
DELETE /v1/dubbing/{dubbing_id}
```
