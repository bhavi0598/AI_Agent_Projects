from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black, blue, darkblue, HexColor

def export_pdf(markdown_text):
    # Set up document
    doc = SimpleDocTemplate("travel_plan.pdf", pagesize=A4,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TravelTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=darkblue,
        spaceAfter=20,
        alignment=1 # Center
    )
    
    heading_style = ParagraphStyle(
        'TravelHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#007bff'), # Your brand blue
        spaceAfter=10,
        spaceBefore=15
    )
    
    body_style = ParagraphStyle(
        'TravelBody',
        parent=styles['BodyText'],
        fontSize=12,
        leading=16, # Line height
        spaceAfter=8
    )

    story = []
    
    # Process text line by line to mimic "parsing" Markdown
    # This is a simple heuristic:
    # # -> Title or Heading
    # ** -> Bold (handled by ReportLab <b/> tag if we convert, but simple text is fine)
    # - -> Bullet
    
    # Add Default Title
    story.append(Paragraph("Personalized Travel Itinerary", title_style))
    story.append(Spacer(1, 10))

    if isinstance(markdown_text, dict):
        # Fallback if somehow it's still JSON (for legacy resets)
        raw_text = str(markdown_text)
    else:
        raw_text = markdown_text

    lines = raw_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 5))
            continue
            
        # Detect Headings (Markdown #)
        if line.startswith('#'):
            # Remove # and trim
            clean_line = line.lstrip('#').strip()
            story.append(Paragraph(clean_line, heading_style))
        # Detect Bold Headers (Day 1:, etc)
        elif line.startswith('**') or "Day" in line and ":" in line:
             story.append(Paragraph(f"<b>{line}</b>", body_style))
        # Detect Bullets
        elif line.startswith('- ') or line.startswith('* '):
            # Indent bullet slightly
            bullet_text = line[2:]
            story.append(Paragraph(f"• {bullet_text}", body_style))
        else:
            # Normal text
            story.append(Paragraph(line, body_style))

    # Build PDF
    try:
        doc.build(story)
        print("PDF Exported Successfully")
    except Exception as e:
        print(f"PDF Export Error: {e}")
