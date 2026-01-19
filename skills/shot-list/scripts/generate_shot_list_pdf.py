#!/usr/bin/env python3
"""Generate professional PDF shot lists from structured data."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from datetime import datetime
import json


def create_shot_list_pdf(
    shots: list,
    output_path: str,
    project_title: str = "Shot List",
    production: str = "",
    director: str = "",
    dp: str = "",
    date: str = None,
    orientation: str = "landscape"
):
    """
    Generate a professional PDF shot list.
    
    Args:
        shots: List of shot dictionaries with keys:
            - scene: Scene number
            - shot: Shot letter/number (A, B, C or 1, 2, 3)
            - setup: Camera setup number
            - shot_type: Shot type code (WS, MS, CU, etc.)
            - framing: Shot framing description
            - movement: Camera movement (STATIC, DOLLY, etc.)
            - description: What happens in the shot
            - notes: Technical/production notes (optional)
            - lens: Lens info (optional)
            - characters: List of characters (optional)
        output_path: Path to save PDF
        project_title: Production/project name
        production: Production company (optional)
        director: Director name (optional)
        dp: DP/Cinematographer name (optional)
        date: Date string (defaults to today)
        orientation: 'landscape' or 'portrait'
    """
    
    if date is None:
        date = datetime.now().strftime("%B %d, %Y")
    
    pagesize = landscape(letter) if orientation == "landscape" else letter
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=pagesize,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=6,
        textColor=colors.HexColor('#1a1a1a')
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        spaceAfter=12
    )
    
    scene_header_style = ParagraphStyle(
        'SceneHeader',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=16,
        spaceAfter=8,
        textColor=colors.HexColor('#1a1a1a'),
        backColor=colors.HexColor('#f0f0f0'),
        borderPadding=6
    )
    
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11
    )
    
    header_cell_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=TA_CENTER
    )
    
    elements = []
    
    # Header
    elements.append(Paragraph(project_title, title_style))
    
    header_parts = []
    if production:
        header_parts.append(production)
    if director:
        header_parts.append(f"Director: {director}")
    if dp:
        header_parts.append(f"DP: {dp}")
    header_parts.append(date)
    
    elements.append(Paragraph(" | ".join(header_parts), subtitle_style))
    elements.append(Spacer(1, 12))
    
    # Group shots by scene
    scenes = {}
    for shot in shots:
        scene_num = shot.get('scene', 1)
        if scene_num not in scenes:
            scenes[scene_num] = {
                'heading': shot.get('scene_heading', f'Scene {scene_num}'),
                'shots': []
            }
        scenes[scene_num]['shots'].append(shot)
    
    # Column widths (landscape)
    if orientation == "landscape":
        col_widths = [0.6*inch, 0.5*inch, 0.5*inch, 1.8*inch, 0.7*inch, 2.8*inch, 2.0*inch]
    else:
        col_widths = [0.5*inch, 0.4*inch, 0.4*inch, 1.4*inch, 0.6*inch, 2.2*inch, 1.6*inch]
    
    # Table header
    headers = ['SHOT', 'SETUP', 'TYPE', 'FRAMING', 'MOVE', 'DESCRIPTION', 'NOTES']
    
    for scene_num in sorted(scenes.keys()):
        scene = scenes[scene_num]
        
        # Scene heading
        elements.append(Paragraph(scene['heading'], scene_header_style))
        
        # Build table data
        table_data = [[Paragraph(h, header_cell_style) for h in headers]]
        
        for shot in scene['shots']:
            shot_id = f"{shot.get('scene', '')}{shot.get('shot', '')}"
            row = [
                Paragraph(shot_id, cell_style),
                Paragraph(str(shot.get('setup', '')), cell_style),
                Paragraph(shot.get('shot_type', ''), cell_style),
                Paragraph(shot.get('framing', ''), cell_style),
                Paragraph(shot.get('movement', ''), cell_style),
                Paragraph(shot.get('description', ''), cell_style),
                Paragraph(shot.get('notes', ''), cell_style)
            ]
            table_data.append(row)
        
        # Create table
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Table styling
        style = TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#2c3e50')),
            
            # Alignment
            ('ALIGN', (0, 0), (2, -1), 'CENTER'),
            ('ALIGN', (4, 0), (4, -1), 'CENTER'),
        ])
        
        # Alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa'))
        
        table.setStyle(style)
        elements.append(table)
        elements.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(elements)
    return output_path


def shots_from_json(json_path: str) -> list:
    """Load shots from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def shots_to_csv(shots: list, output_path: str):
    """Export shots to CSV for scheduling software."""
    import csv
    
    fieldnames = ['scene', 'shot', 'setup', 'shot_type', 'framing', 
                  'movement', 'description', 'notes', 'lens', 'characters']
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for shot in shots:
            row = {k: shot.get(k, '') for k in fieldnames}
            if isinstance(row.get('characters'), list):
                row['characters'] = ', '.join(row['characters'])
            writer.writerow(row)


if __name__ == "__main__":
    # Example usage
    example_shots = [
        {
            'scene': 1,
            'scene_heading': 'INT. COFFEE SHOP - DAY',
            'shot': 'A',
            'setup': 1,
            'shot_type': 'WS',
            'framing': 'Wide establishing',
            'movement': 'STATIC',
            'description': 'Coffee shop interior, morning rush. SARAH enters frame.',
            'notes': 'Practical lighting from windows'
        },
        {
            'scene': 1,
            'shot': 'B',
            'setup': 1,
            'shot_type': 'MS',
            'framing': 'Medium on Sarah',
            'movement': 'TRACK',
            'description': 'Follow Sarah as she scans the room looking for someone.',
            'notes': 'Steadicam or gimbal'
        },
        {
            'scene': 1,
            'shot': 'C',
            'setup': 2,
            'shot_type': 'OTS',
            'framing': 'Over Jake to Sarah',
            'movement': 'STATIC',
            'description': 'Sarah approaches table, dialogue begins.',
            'notes': '50mm lens'
        },
        {
            'scene': 1,
            'shot': 'D',
            'setup': 3,
            'shot_type': 'CU',
            'framing': 'Close on Sarah',
            'movement': 'STATIC',
            'description': 'Reaction to Jake\'s revelation.',
            'notes': '85mm, shallow DOF'
        },
    ]
    
    create_shot_list_pdf(
        shots=example_shots,
        output_path='/tmp/example_shot_list.pdf',
        project_title='THE MEETING',
        director='Jane Smith',
        dp='John Doe'
    )
    print("Example PDF created: /tmp/example_shot_list.pdf")
