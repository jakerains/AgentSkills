#!/usr/bin/env python3
"""Parse screenplays from various formats to extract scene structure."""

import re
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_screenplay(file_path: str) -> dict:
    """
    Parse screenplay from supported formats.
    
    Returns dict with:
        - title: Project title if found
        - scenes: List of scene dicts
        - characters: Set of all characters
        - page_count: Estimated pages
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    if ext == '.fdx':
        return parse_fdx(content)
    elif ext == '.fountain':
        return parse_fountain(content)
    else:  # .txt or other text formats
        return parse_text(content)


def parse_text(text: str) -> dict:
    """Parse plain text screenplay format."""
    scenes = []
    characters = set()
    
    # Scene heading patterns
    scene_pattern = r'^[\s]*((?:INT\.|EXT\.|INT\./EXT\.|EXT\./INT\.|I/E\.)\s+.+?)(?:\s+-\s+|\s+)?(DAY|NIGHT|MORNING|EVENING|CONTINUOUS|LATER|SAME)?[\s]*$'
    
    lines = text.split('\n')
    current_scene = None
    scene_num = 0
    in_dialogue = False
    current_character = None
    
    for line in lines:
        stripped = line.strip()
        
        # Check for scene heading
        match = re.match(scene_pattern, stripped, re.IGNORECASE)
        if match:
            if current_scene:
                scenes.append(current_scene)
            scene_num += 1
            current_scene = {
                'number': scene_num,
                'heading': stripped.upper(),
                'location': extract_location(stripped),
                'time': match.group(2) if match.group(2) else '',
                'int_ext': 'INT' if 'INT' in stripped.upper() else 'EXT',
                'characters': set(),
                'action': [],
                'dialogue': []
            }
            in_dialogue = False
            current_character = None
            continue
        
        if not current_scene:
            continue
        
        # Check for character cue (ALL CAPS, typically indented)
        if stripped.isupper() and 2 < len(stripped) < 45:
            # Filter out transitions and formatting elements
            exclude = ['CUT TO', 'FADE', 'DISSOLVE', 'SMASH', 'MATCH', 'INSERT', 
                      'BACK TO', 'END OF', 'TITLE CARD', 'SUPER:', 'INTERCUT',
                      'FLASHBACK', 'DREAM', 'MONTAGE', 'SERIES OF', 'THE END',
                      'CONTINUED', 'MORE', 'CONT\'D']
            if not any(t in stripped for t in exclude):
                # Extract character name (remove parentheticals)
                char_name = re.sub(r'\s*\(.*?\)\s*', '', stripped).strip()
                if char_name:
                    characters.add(char_name)
                    current_scene['characters'].add(char_name)
                    current_character = char_name
                    in_dialogue = True
                    continue
        
        # Dialogue (indented text after character)
        if in_dialogue and stripped:
            # Parenthetical
            if stripped.startswith('(') and stripped.endswith(')'):
                current_scene['dialogue'].append({
                    'character': current_character,
                    'type': 'parenthetical',
                    'text': stripped
                })
            else:
                current_scene['dialogue'].append({
                    'character': current_character,
                    'type': 'dialogue',
                    'text': stripped
                })
                in_dialogue = False  # Reset after dialogue block
        elif stripped and not in_dialogue:
            # Action line
            current_scene['action'].append(stripped)
    
    # Don't forget the last scene
    if current_scene:
        scenes.append(current_scene)
    
    # Convert character sets to lists
    for s in scenes:
        s['characters'] = list(s['characters'])
    
    return {
        'title': extract_title(text),
        'scenes': scenes,
        'characters': list(characters),
        'page_count': estimate_pages(text)
    }


def parse_fountain(text: str) -> dict:
    """Parse Fountain markup format."""
    scenes = []
    characters = set()
    title = ""
    
    # Extract title page
    title_match = re.search(r'^Title:\s*(.+)$', text, re.MULTILINE | re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
    
    # Split by page break or scene headings
    scene_pattern = r'^(\.?(?:INT\.|EXT\.|INT\./EXT\.|EXT\./INT\.|I/E\.).+)$'
    
    lines = text.split('\n')
    current_scene = None
    scene_num = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Forced scene heading (starts with .)
        if stripped.startswith('.') and len(stripped) > 1:
            heading = stripped[1:].strip()
            if current_scene:
                scenes.append(current_scene)
            scene_num += 1
            current_scene = create_scene_dict(scene_num, heading)
            continue
        
        # Standard scene heading
        if re.match(r'^(?:INT\.|EXT\.|INT\./EXT\.|I/E\.)', stripped, re.IGNORECASE):
            if current_scene:
                scenes.append(current_scene)
            scene_num += 1
            current_scene = create_scene_dict(scene_num, stripped)
            continue
        
        if not current_scene:
            continue
        
        # Character (ALL CAPS line, not a transition)
        if stripped.isupper() and len(stripped) > 1 and len(stripped) < 45:
            if not stripped.endswith(':') and not any(t in stripped for t in ['CUT TO', 'FADE']):
                char_name = re.sub(r'\s*[\^@].*', '', stripped)  # Remove dual dialogue markers
                char_name = re.sub(r'\s*\(.*?\)', '', char_name).strip()
                if char_name:
                    characters.add(char_name)
                    current_scene['characters'].add(char_name)
        
        # Track action
        elif stripped and not stripped.startswith('>') and not stripped.startswith('('):
            current_scene['action'].append(stripped)
    
    if current_scene:
        scenes.append(current_scene)
    
    for s in scenes:
        s['characters'] = list(s['characters'])
    
    return {
        'title': title,
        'scenes': scenes,
        'characters': list(characters),
        'page_count': estimate_pages(text)
    }


def parse_fdx(xml_content: str) -> dict:
    """Parse Final Draft XML format."""
    scenes = []
    characters = set()
    title = ""
    
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return parse_text(xml_content)  # Fallback to text parsing
    
    # Get title
    title_page = root.find('.//TitlePage')
    if title_page is not None:
        title_elem = title_page.find('.//Paragraph[@Type="Title"]/Text')
        if title_elem is not None and title_elem.text:
            title = title_elem.text.strip()
    
    current_scene = None
    scene_num = 0
    
    content = root.find('Content')
    if content is None:
        return {'title': title, 'scenes': [], 'characters': [], 'page_count': 0}
    
    for para in content.findall('Paragraph'):
        para_type = para.get('Type', '')
        text_elem = para.find('Text')
        text = text_elem.text if text_elem is not None and text_elem.text else ''
        
        if para_type == 'Scene Heading':
            if current_scene:
                scenes.append(current_scene)
            scene_num += 1
            current_scene = create_scene_dict(scene_num, text)
        
        elif para_type == 'Character' and current_scene:
            char_name = re.sub(r'\s*\(.*?\)', '', text).strip()
            if char_name:
                characters.add(char_name)
                current_scene['characters'].add(char_name)
        
        elif para_type == 'Action' and current_scene:
            current_scene['action'].append(text)
    
    if current_scene:
        scenes.append(current_scene)
    
    for s in scenes:
        s['characters'] = list(s['characters'])
    
    return {
        'title': title,
        'scenes': scenes,
        'characters': list(characters),
        'page_count': len(scenes)  # Rough estimate
    }


def create_scene_dict(num: int, heading: str) -> dict:
    """Create a new scene dictionary."""
    return {
        'number': num,
        'heading': heading.upper(),
        'location': extract_location(heading),
        'time': extract_time(heading),
        'int_ext': 'INT' if 'INT' in heading.upper() else 'EXT',
        'characters': set(),
        'action': [],
        'dialogue': []
    }


def extract_location(heading: str) -> str:
    """Extract location from scene heading."""
    # Remove INT./EXT. prefix and time suffix
    loc = re.sub(r'^(?:INT\.|EXT\.|INT\./EXT\.|I/E\.)\s*', '', heading, flags=re.IGNORECASE)
    loc = re.sub(r'\s*-\s*(DAY|NIGHT|MORNING|EVENING|CONTINUOUS|LATER|SAME).*$', '', loc, flags=re.IGNORECASE)
    return loc.strip()


def extract_time(heading: str) -> str:
    """Extract time of day from scene heading."""
    match = re.search(r'-\s*(DAY|NIGHT|MORNING|EVENING|DUSK|DAWN|CONTINUOUS|LATER|SAME)', 
                      heading, re.IGNORECASE)
    return match.group(1).upper() if match else ''


def extract_title(text: str) -> str:
    """Try to extract title from script text."""
    # Look for centered title at start
    lines = text.strip().split('\n')[:20]
    for line in lines:
        stripped = line.strip()
        if stripped and stripped.isupper() and len(stripped) < 60:
            if not any(t in stripped for t in ['INT.', 'EXT.', 'FADE', 'CUT']):
                return stripped
    return ""


def estimate_pages(text: str) -> int:
    """Estimate page count (roughly 55 lines per page)."""
    lines = [l for l in text.split('\n') if l.strip()]
    return max(1, len(lines) // 55)


def summarize_script(parsed: dict) -> str:
    """Create a readable summary of parsed script."""
    lines = []
    lines.append(f"Title: {parsed['title'] or 'Untitled'}")
    lines.append(f"Scenes: {len(parsed['scenes'])}")
    lines.append(f"Characters: {len(parsed['characters'])}")
    lines.append(f"Est. Pages: {parsed['page_count']}")
    lines.append("")
    lines.append("Scene Breakdown:")
    
    for scene in parsed['scenes']:
        chars = ', '.join(scene['characters'][:4])
        if len(scene['characters']) > 4:
            chars += f" (+{len(scene['characters'])-4} more)"
        lines.append(f"  {scene['number']}. {scene['heading']}")
        if chars:
            lines.append(f"      Characters: {chars}")
    
    return '\n'.join(lines)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = parse_screenplay(sys.argv[1])
        print(summarize_script(result))
    else:
        print("Usage: parse_screenplay.py <script_file>")
