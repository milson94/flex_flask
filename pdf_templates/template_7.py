import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, gray

def generate_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)

    styles = getSampleStyleSheet()

    # --- Custom Styles ---
    styles.add(ParagraphStyle(name='NameHeader',
                              fontName='Helvetica-Bold',
                              fontSize=24,
                              leading=28,
                              alignment=1, # Center
                              spaceAfter=0.1*inch))

    styles.add(ParagraphStyle(name='ContactHeader',
                              fontName='Helvetica',
                              fontSize=10,
                              leading=12,
                              alignment=1, # Center
                              spaceAfter=0.2*inch))

    styles.add(ParagraphStyle(name='SectionTitle',
                              fontName='Helvetica-Bold',
                              fontSize=14,
                              leading=18,
                              spaceBefore=0.2*inch,
                              spaceAfter=0.1*inch,
                              textColor=HexColor('#333333')))

    styles.add(ParagraphStyle(name='JobTitle',
                              fontName='Helvetica-Bold',
                              fontSize=11,
                              leading=14))

    styles.add(ParagraphStyle(name='CompanyDate',
                              fontName='Helvetica-Oblique',
                              fontSize=10,
                              leading=12,
                              textColor=gray,
                              spaceAfter=0.05*inch))

    styles.add(ParagraphStyle(name='BulletPoint',
                              parent=styles['Normal'],
                              leftIndent=0.25*inch,
                              bulletIndent=0.1*inch,
                              firstLineIndent=0,
                              spaceBefore=0.05*inch))

    styles.add(ParagraphStyle(name='NormalIndented',
                              parent=styles['Normal'],
                              leftIndent=0.25*inch))

    story = []

    # --- Personal Details ---
    if data.get('full_name'):
        story.append(Paragraph(data['full_name'].upper(), styles['NameHeader']))

    contact_info = []
    if data.get('email'): contact_info.append(data['email'])
    if data.get('phone'): contact_info.append(data['phone'])
    if data.get('linkedin'): contact_info.append(f"LinkedIn: {data['linkedin']}")
    if data.get('github'): contact_info.append(f"GitHub: {data['github']}")
    if contact_info:
        story.append(Paragraph(" | ".join(contact_info), styles['ContactHeader']))

    story.append(HRFlowable(width="100%", thickness=0.5, color=gray, spaceBefore=0.1*inch, spaceAfter=0.1*inch))

    # --- Summary ---
    if data.get('summary'):
        story.append(Paragraph("Summary", styles['SectionTitle']))
        story.append(Paragraph(data['summary'], styles['Normal']))
        story.append(Spacer(1, 0.1*inch))

    # --- Professional Experience ---
    experiences = data.get('experiences', [])
    if experiences:
        story.append(Paragraph("Professional Experience", styles['SectionTitle']))
        for exp in experiences:
            if exp.get('title') and exp.get('company'):
                story.append(Paragraph(exp['title'], styles['JobTitle']))
                story.append(Paragraph(f"{exp['company']} | {exp.get('dates', 'N/A')}", styles['CompanyDate']))
                if exp.get('description'):
                    # Basic handling for bullet points (assuming user types '-' or similar)
                    desc_lines = exp['description'].split('\n')
                    for line in desc_lines:
                        line = line.strip()
                        if line.startswith(('-', '*', '•')):
                            story.append(Paragraph(line, styles['BulletPoint'], bulletText=line[0]))
                        elif line:
                             story.append(Paragraph(line, styles['NormalIndented']))
                story.append(Spacer(1, 0.15*inch))

    # --- Education ---
    education_entries = data.get('education_entries', [])
    if education_entries:
        story.append(Paragraph("Education", styles['SectionTitle']))
        for edu in education_entries:
            if edu.get('degree') and edu.get('institution'):
                story.append(Paragraph(edu['degree'], styles['JobTitle']))
                story.append(Paragraph(f"{edu['institution']} | {edu.get('edu_dates', 'N/A')}", styles['CompanyDate']))
                if edu.get('edu_details'):
                    story.append(Paragraph(edu['edu_details'], styles['NormalIndented']))
                story.append(Spacer(1, 0.1*inch))

    # --- Skills ---
    if data.get('skills'):
        story.append(Paragraph("Skills", styles['SectionTitle']))
        story.append(Paragraph(data['skills'], styles['Normal'])) # Assuming comma-separated
        story.append(Spacer(1, 0.1*inch))

    # --- Hobbies ---
    if data.get('hobbies'):
        story.append(Paragraph("Hobbies", styles['SectionTitle']))
        story.append(Paragraph(data['hobbies'], styles['Normal']))
        story.append(Spacer(1, 0.1*inch))

    doc.build(story)
    buffer.seek(0)
    return buffer
