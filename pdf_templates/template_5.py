import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

def generate_pdf(resume_data):
    """Generates a professional-style PDF resume using ReportLab."""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    # Define custom styles
    styles.add(ParagraphStyle(name='Normal', fontName='Helvetica', fontSize=10, leading=12))
    styles.add(ParagraphStyle(name='Heading1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, leading=18, spaceAfter=2 * mm))
    styles.add(ParagraphStyle(name='Heading2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=14, leading=16, spaceBefore=5 * mm, spaceAfter=1 * mm))
    styles.add(ParagraphStyle(name='Heading3', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=14, spaceBefore=2 * mm))
    styles.add(ParagraphStyle(name='Detail', parent=styles['Normal'], fontSize=9, textColor=colors.darkgrey))
    styles.add(ParagraphStyle(name='Bullet', parent=styles['Normal'], leftIndent=5 * mm, bulletText='•'))

    story = []

    # Header Section
    header_parts = []
    if resume_data.get('full_name'):
        header_parts.append(Paragraph(resume_data['full_name'], styles['Heading1']))
    if resume_data.get('title_subtitle'):
        header_parts.append(Paragraph(resume_data['title_subtitle'], styles['Heading3']))
    if header_parts:
        story.extend(header_parts)
        story.append(Spacer(1, 2 * mm))

    # Contact Information
    contact_info = []
    if resume_data.get('phone'):
        contact_info.append(f"Phone: {resume_data['phone']}")
    if resume_data.get('email'):
        contact_info.append(f"Email: {resume_data['email']}")
    if resume_data.get('linkedin'):
        contact_info.append(f"LinkedIn: {resume_data['linkedin']}")
    if resume_data.get('location'):
        contact_info.append(f"Location: {resume_data['location']}")

    if contact_info:
        story.append(Paragraph(" | ".join(contact_info), styles['Detail']))
        story.append(Spacer(1, 8 * mm))

    # Body Sections based on order
    section_order = resume_data.get('section_order', ['summary', 'experience', 'education', 'achievements', 'courses'])

    for section in section_order:
        if section == 'summary' and resume_data.get('summary'):
            story.append(Paragraph("Summary", styles['Heading2']))
            story.append(Paragraph(resume_data['summary'], styles['Normal']))
            story.append(Spacer(1, 10 * mm))
        elif section == 'experience' and resume_data.get('experiences'):
            story.append(Paragraph("Experience", styles['Heading2']))
            for exp in resume_data['experiences']:
                title_company = f"{exp['title']}, <font name='Helvetica-Bold'>{exp['company']}</font>"
                if exp.get('location'):
                    title_company += f", {exp['location']}"
                story.append(Paragraph(title_company, styles['Normal']))
                date_range = f"<font size='9'>{exp['start_date']} - {exp['end_date'] if not exp.get('is_present') else 'Present'}</font>"
                story.append(Paragraph(date_range, styles['Detail']))
                if exp.get('description'):
                    for item in exp['description'].split('\n'):
                        story.append(Paragraph(item.strip(), styles['Bullet']))
                story.append(Spacer(1, 5 * mm))
            story.append(Spacer(1, 10 * mm))
        elif section == 'education' and resume_data.get('education_entries'):
            story.append(Paragraph("Education", styles['Heading2']))
            for edu in resume_data['education_entries']:
                degree_institution = f"{edu['degree']}, <font name='Helvetica-Bold'>{edu['institution']}</font>"
                if edu.get('edu_location'):
                    degree_institution += f", {edu['edu_location']}"
                story.append(Paragraph(degree_institution, styles['Normal']))
                date_range = f"<font size='9'>{edu['start_date']} - {edu['end_date'] if not edu.get('is_present') else 'Present'}</font>"
                story.append(Paragraph(date_range, styles['Detail']))
                if edu.get('edu_details'):
                    story.append(Paragraph(edu['edu_details'], styles['Detail']))
                story.append(Spacer(1, 5 * mm))
            story.append(Spacer(1, 10 * mm))
        elif section == 'achievements' and resume_data.get('key_achievements'):
            story.append(Paragraph("Key Achievements", styles['Heading2']))
            for ach in resume_data['key_achievements']:
                if ach.get('title'):
                    story.append(Paragraph(f"<bullet>•</bullet> <font name='Helvetica-Bold'>{ach['title']}</font>", styles['Bullet']))
                    if ach.get('description'):
                        story.append(Paragraph(ach['description'], styles['Detail'], bulletText=''))
            story.append(Spacer(1, 10 * mm))
        elif section == 'courses' and resume_data.get('courses'):
            story.append(Paragraph("Courses/Certifications", styles['Heading2']))
            for course in resume_data['courses']:
                if course.get('title'):
                    story.append(Paragraph(f"<bullet>•</bullet> <font name='Helvetica-Bold'>{course['title']}</font>", styles['Bullet']))
                    if course.get('description'):
                        story.append(Paragraph(course['description'], styles['Detail'], bulletText=''))
            story.append(Spacer(1, 10 * mm))

    doc.build(story)
    buffer.seek(0)
    return buffer
