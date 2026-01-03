---
name: shot-list
description: Generate professional shot lists from screenplays and scripts. Use when user uploads a screenplay (.fountain, .fdx, .txt, .pdf, .docx) or describes scenes for production planning. Parses scripts to extract scenes, helps determine camera setups, shot types, framing, and movement through collaborative discussion, then generates beautifully formatted PDF shot lists for production. Triggers include requests to create shot lists, plan shots, break down scripts for filming, or organize camera coverage.
---

# Shot List Generator

Parse screenplays, collaboratively determine shots, and generate production-ready PDF shot lists.

## Workflow Overview

1. **Parse Script** → Extract scenes, locations, characters, action
2. **Collaborate** → Discuss shot choices scene-by-scene with user
3. **Generate PDF** → Create professional, printable shot list

## Step 1: Parse the Script

Support formats: `.fountain`, `.fdx`, `.txt`, `.pdf`, `.docx`

### Scene Extraction Pattern

Extract from script:
- **Scene number** (auto-generate if missing)
- **Scene heading** (INT./EXT., location, time)
- **Characters** in scene
- **Key action beats** (story moments needing coverage)
- **Page/timing estimate**

### Fountain/Text Parsing

```python
import re

def parse_screenplay(text):
    """Extract scenes from screenplay text."""
    scenes = []
    scene_pattern = r'^((?:INT\.|EXT\.|INT\./EXT\.|I/E\.)\s+.+)$'
    
    lines = text.split('\n')
    current_scene = None
    scene_num = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if re.match(scene_pattern, line, re.IGNORECASE):
            if current_scene:
                scenes.append(current_scene)
            scene_num += 1
            current_scene = {
                'number': scene_num,
                'heading': line,
                'characters': set(),
                'action_beats': [],
                'content': []
            }
        elif current_scene:
            current_scene['content'].append(line)
            if line.isupper() and len(line) > 1 and len(line) < 40:
                if not any(t in line for t in ['CUT TO', 'FADE', 'DISSOLVE']):
                    current_scene['characters'].add(line.split('(')[0].strip())
    
    if current_scene:
        scenes.append(current_scene)
    
    for s in scenes:
        s['characters'] = list(s['characters'])
    
    return scenes
```

## Step 2: Collaborative Shot Planning

After parsing, present scenes and discuss coverage. For each scene ask:

1. **What's the emotional arc?** (Drives framing choices)
2. **Who has focus?** (Determines coverage priority)
3. **Key moments?** (Beats requiring specific shots)
4. **Practical constraints?** (Location, equipment, time)
5. **Visual style reference?** (Film/show inspiration)

### Shot Type Reference

| Type | Code | Use For |
|------|------|---------|
| Wide/Establishing | WS | Location, groups |
| Full Shot | FS | Full body, action |
| Medium Shot | MS | Dialogue, interaction |
| Medium Close-Up | MCU | Emotional dialogue |
| Close-Up | CU | Reaction, emotion |
| Extreme Close-Up | ECU | Critical detail |
| Over-the-Shoulder | OTS | Dialogue coverage |
| Two-Shot | 2S | Paired characters |
| Insert | INS | Props, details |
| POV | POV | Character perspective |

### Camera Movement Reference

| Movement | Code | Effect |
|----------|------|--------|
| Static | STATIC | Stability |
| Pan | PAN | Follow horizontally |
| Tilt | TILT | Reveal height |
| Dolly | DOLLY | Approach/retreat |
| Tracking | TRACK | Follow movement |
| Crane | CRANE | Epic scale |
| Handheld | HH | Tension, energy |
| Steadicam | STEDI | Fluid following |

### Angle Reference

| Angle | Effect |
|-------|--------|
| Eye Level | Neutral |
| Low Angle | Power |
| High Angle | Vulnerability |
| Dutch | Unease |

## Step 3: Building Shot Entries

```python
shot_entry = {
    'scene': 1,
    'shot': 'A',
    'setup': 1,
    'shot_type': 'MS',
    'framing': 'Medium on Sarah',
    'angle': 'Eye Level',
    'movement': 'STATIC',
    'lens': '50mm',
    'description': 'Sarah enters, sees the letter',
    'characters': ['SARAH'],
    'notes': 'Practical window light'
}
```

### Coverage Pattern
Master → Medium → Close-ups → Inserts

## Step 4: Generate PDF

Use `scripts/generate_shot_list_pdf.py` for professional output.

### PDF Columns

| Column | Content |
|--------|---------|
| Shot # | Scene.Shot ID |
| Setup | Camera setup |
| Type | Shot type code |
| Framing | Description |
| Move | Camera movement |
| Action | What happens |
| Notes | Technical notes |

Output to `/mnt/user-data/outputs/shot_list_{project}.pdf`

## References

- `references/shot_terminology.md` - Complete glossary
- `references/coverage_patterns.md` - Common coverage strategies
