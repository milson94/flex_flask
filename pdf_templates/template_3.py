import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Frame, PageTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, gray, white
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor, gray, white, black  # Import black


def generate_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=0.75 * inch, leftMargin=0.75 * inch,
                            topMargin=0.75 * inch, bottomMargin=0.75 * inch)

    styles = getSampleStyleSheet()

    # --- Custom Styles ---
    styles.add(ParagraphStyle(name='NameHeader',
                              fontName='Helvetica-Bold',
                              fontSize=24,
                              leading=28,
                              alignment=TA_LEFT,  # Left
                              spaceAfter=0.1 * inch))

    styles.add(ParagraphStyle(name='ContactHeader',
                              fontName='Helvetica',
                              fontSize=10,
                              leading=12,
                              alignment=TA_LEFT,  # Left
                              spaceAfter=0.2 * inch))

    styles.add(ParagraphStyle(name='SectionTitle',
                              fontName='Helvetica-Bold',
                              fontSize=14,
                              leading=18,
                              spaceBefore=0.2 * inch,
                              spaceAfter=0.1 * inch,
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
                              spaceAfter=0.05 * inch))

    styles.add(ParagraphStyle(name='BulletPoint',
                              parent=styles['Normal'],
                              leftIndent=0.25 * inch,
                              bulletIndent=0.1 * inch,
                              firstLineIndent=0,
                              spaceBefore=0.05 * inch))

    styles.add(ParagraphStyle(name='NormalIndented',
                              parent=styles['Normal'],
                              leftIndent=0.25 * inch))

    styles.add(ParagraphStyle(name='Justified',
                              parent=styles['Normal'],
                              alignment=TA_JUSTIFY))  # 4 for justified

    styles.add(ParagraphStyle(name='PersonalDetails',
                              parent=styles['Normal'],
                              alignment=TA_LEFT,  # Personal details stay left aligned in this layout
                              spaceAfter=0.05 * inch))

    story = []

    # --- Two Column Layout ---
    def two_column_layout(canvas, doc):
        canvas.saveState()
        # Draw a vertical line to separate columns
        canvas.setStrokeColor(gray)
        canvas.setLineWidth(0.5)
        # Adjust the y-coordinates to match the column height
        canvas.line(A4[0] / 2, doc.bottomMargin, A4[0] / 2, A4[1] - doc.topMargin - 1.5 * inch)
        canvas.restoreState()

    # Create a frame for the header
    frame_header = Frame(doc.leftMargin, A4[1] - doc.topMargin - 1.5 * inch,  # Top of page - 1.5 inch height
                         A4[0] - doc.leftMargin - doc.rightMargin, 1.5 * inch,
                         id='header')

    # Create a frame for the first column
    frame1 = Frame(doc.leftMargin, doc.bottomMargin, A4[0] / 2 - doc.leftMargin - doc.rightMargin / 2,
                   A4[1] - doc.topMargin - doc.bottomMargin - 1.5 * inch,
                   id='col1')

    # Create a frame for the second column
    frame2 = Frame(A4[0] / 2 + doc.rightMargin / 2, doc.bottomMargin, A4[0] / 2 - doc.rightMargin / 2 - doc.rightMargin,
                   A4[1] - doc.topMargin - doc.bottomMargin - 1.5 * inch,
                   id='col2')

    # Create a page template with header and two columns
    page_template = PageTemplate(id='TwoColumns', frames=[frame_header, frame1, frame2], onPage=two_column_layout)
    doc.addPageTemplates([page_template])

    # --- Header ---
    header_content = []

    if data.get('full_name'):
        header_content.append(Paragraph(data['full_name'].upper(), styles['NameHeader']))

    contact_info = []
    if data.get('email'): contact_info.append(data['email'])
    if data.get('phone'): contact_info.append(data['phone'])
    if data.get('linkedin'): contact_info.append(f"LinkedIn: {data['linkedin']}")
    if data.get('github'): contact_info.append(f"GitHub: {data['github']}")
    if data.get('website'): contact_info.append(f"Website: {data['website']}")
    if data.get('address'): contact_info.append(data['address']) # Ensure you handle multiline addresses well

    if contact_info:
        header_content.append(Paragraph(" | ".join(contact_info), styles['ContactHeader']))

    header_content.append(HRFlowable(width="100%", thickness=0.5, color=gray, spaceBefore=0.1 * inch,
                                   spaceAfter=0.1 * inch))
    # Put all the header elements
    for element in header_content:
        story.append(element)
    # ---

    # Start with an empty story and add elements later to the columns
    story = [] # start empty.

    # --- Section Ordering ---
    section_order = data.get('section_order', ['summary', 'experience', 'education', 'skills', 'hobbies', 'languages', 'additional_info', 'references', 'projects','achievements','courses']) # Add more sections
    # Keep track of current frame
    current_frame = 'col1'
    def add_to_column(element):
        story.append(element)

    for section_key in section_order:
        if section_key == 'summary':
            if data.get('summary'):
                add_to_column(Paragraph("Summary", styles['SectionTitle']))
                add_to_column(Paragraph(data['summary'], styles['Justified']))
                add_to_column(Spacer(1, 0.1 * inch))

        elif section_key == 'experience':
            experiences = data.get('experiences', [])
            if experiences:
                add_to_column(Paragraph("Professional Experience", styles['SectionTitle']))
                for exp in experiences:
                    if exp.get('title') and exp.get('company'):
                        add_to_column(Paragraph(exp['title'], styles['JobTitle']))
                        add_to_column(Paragraph(f"{exp['company']} | {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'Present')}", styles['CompanyDate']))
                        if exp.get('description'):
                            desc_lines = exp['description'].split('\n')
                            for line in desc_lines:
                                line = line.strip()
                                if line.startswith(('-', '*', '•')):
                                    add_to_column(Paragraph(line, styles['BulletPoint'], bulletText=line[0]))
                                elif line:
                                    add_to_column(Paragraph(line, styles['Justified']))
                        add_to_column(Spacer(1, 0.15 * inch))

        elif section_key == 'education':
            education_entries = data.get('education_entries', [])
            if education_entries:
                add_to_column(Paragraph("Education", styles['SectionTitle']))
                for edu in education_entries:
                    if edu.get('degree') and edu.get('institution'):
                        add_to_column(Paragraph(edu['degree'], styles['JobTitle']))
                        add_to_column(Paragraph(f"{edu['institution']} | {edu.get('start_date', 'N/A')} - {edu.get('end_date', 'Present')}", styles['CompanyDate']))
                        if edu.get('edu_details'):
                            add_to_column(Paragraph(edu['edu_details'], styles['Justified']))
                        add_to_column(Spacer(1, 0.1 * inch))

        elif section_key == 'skills':
            if data.get('skills'):
                add_to_column(Paragraph("Skills", styles['SectionTitle']))
                add_to_column(Paragraph(data['skills'], styles['Justified']))
                add_to_column(Spacer(1, 0.1 * inch))

        elif section_key == 'hobbies':
            if data.get('hobbies'):
                add_to_column(Paragraph("Hobbies", styles['SectionTitle']))
                add_to_column(Paragraph(data['hobbies'], styles['Justified']))
                add_to_column(Spacer(1, 0.1 * inch))
        elif section_key == 'achievements':
            key_achievements = data.get('key_achievements', [])
            if key_achievements:
                add_to_column(Paragraph("Key Achievements", styles['SectionTitle']))
                for achievement in key_achievements:
                    if achievement.get('title'):
                        add_to_column(Paragraph(achievement['title'], styles['JobTitle']))
                        if achievement.get('description'):
                            add_to_column(Paragraph(achievement['description'], styles['NormalIndented']))
                        add_to_column(Spacer(1, 0.1 * inch))

        elif section_key == 'courses':
            courses = data.get('courses', [])
            if courses:
                add_to_column(Paragraph("Courses", styles['SectionTitle']))
                for course in courses:
                    if course.get('title'):
                        add_to_column(Paragraph(course['title'], styles['JobTitle']))
                        if course.get('description'):
                            add_to_column(Paragraph(course['description'], styles['NormalIndented']))
                        add_to_column(Spacer(1, 0.1 * inch))

        elif section_key == 'languages':
            languages = data.get('languages', [])
            if languages:
                add_to_column(Paragraph("Languages", styles['SectionTitle']))
                language_data = [["Language", "Reading", "Writing", "Conversation"]]  # Header
                for lang in languages:
                    language_data.append([
                        lang.get('name', ''),
                        lang.get('reading', 'N/A'),
                        lang.get('writing', 'N/A'),
                        lang.get('level', 'N/A')
                    ])

                language_table = Table(language_data)
                language_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor("#333333")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), white),  # Background color for data cells
                    ('GRID', (0, 0), (-1, -1), 1, black)
                ]))
                add_to_column(language_table)
                add_to_column(Spacer(1, 0.1 * inch))

        elif section_key == 'additional_info':
            additional_info = data.get('additional_info', [])
            if additional_info:
                add_to_column(Paragraph("Additional Info", styles['SectionTitle']))
                for info in additional_info:
                    if info.get('title'):
                        add_to_column(Paragraph(info['title'], styles['JobTitle']))
                        if info.get('description'):
                            add_to_column(Paragraph(info['description'], styles['NormalIndented']))
                        add_to_column(Spacer(1, 0.1 * inch))

        elif section_key == 'references':
            references = data.get('references', [])
            if references:
                add_to_column(Paragraph("References", styles['SectionTitle']))
                for ref in references:
                    if ref.get('name'):
                        add_to_column(Paragraph(ref['name'], styles['JobTitle']))
                        add_to_column(Paragraph(f"{ref.get('title', 'N/A')}", styles['CompanyDate']))
                        if ref.get('phone'):
                            add_to_column(Paragraph(f"Phone: {ref['phone']}", styles['NormalIndented']))
                        if ref.get('description'):
                            add_to_column(Paragraph(ref['description'], styles['NormalIndented']))
                        add_to_column(Spacer(1, 0.1 * inch))

        elif section_key == 'projects':
            projects = data.get('projects', [])
            if projects:
                add_to_column(Paragraph("Projects", styles['SectionTitle']))
                for project in projects:
                    if project.get('title'):
                        add_to_column(Paragraph(project['title'], styles['JobTitle']))
                        if project.get('description'):
                            add_to_column(Paragraph(project['description'], styles['NormalIndented']))
                        if project.get('dates'):
                            add_to_column(Paragraph(f"Dates: {project['dates']}", styles['CompanyDate']))
                        add_to_column(Spacer(1, 0.1 * inch))

    # Build the document
    doc.build(story)
    buffer.seek(0)
    return buffer

# Example usage
data = {
    'full_name': 'Ellen Johnson',
    'email': 'help@enhancv.com',
    'linkedin': 'linkedin.com',
    'summary': 'Motivated Digital Marketing Manager with over 3 years of experience in driving user acquisition and growth through strategic paid campaigns. Expert in data analysis, creative optimization, and cross-functional collaboration to achieve business objectives. Proven track record of scaling campaigns and enhancing ROI.',
    'experiences': [
        {
            'title': 'Senior Digital Marketing Specialist',
            'company': 'Tech Innovate',
            'start_date': '01/2022',
            'end_date': 'Present',
            'description': '- Led the development and execution of comprehensive digital marketing campaigns across Meta, Google, and TikTok, increasing user acquisition by 45% within 12 months.\n- Managed a $500K quarterly budget for paid acquisition channels, optimizing spend for a 30% improvement in ROAS.\n- Implemented advanced targeting and retargeting strategies that reduced CPA by 20%, while increasing conversion rates by 15%.'
        },
        # Add more experiences as needed
    ],
    'education_entries': [
        {
            'degree': 'Master of Science in Marketing Analytics',
            'institution': 'University of California, Berkeley',
            'start_date': '01/2015',
            'end_date': '01/2017',
            'edu_details': 'Relevant coursework in strategic finance and operations management.'
        },
        # Add more education entries as needed
    ],
    'skills': 'Data Analysis, Paid Acquisition, Retargeting, ROAS Optimization, Cross-Functional Collaboration, Google Analytics, Looker, Appsflyer, Meta Advertising, Google Ads, TikTok Ads, Snapchat Ads, SQL',
    'hobbies': 'Reading, Hiking, Photography',
    'languages': [
        {'name': 'English', 'reading': 'Fluent', 'writing': 'Advanced', 'level': 'Fluent'},
        {'name': 'Spanish', 'reading': 'Intermediate', 'writing': 'Basic', 'level': 'Conversational'}
    ],
    'achievements': [
            {'title': 'Increased Sales by 20%', 'description': 'Successfully increased sales figures by 20% within the first quarter.'},
            {'title': 'Improved Customer Satisfaction', 'description': 'Enhanced customer satisfaction through strategic service improvements.'},
            {'title': 'Reduced Operational Costs', 'description': 'Implemented cost-saving measures that significantly reduced operational expenses.'}
        ],
    'courses': [
            {'title': 'Marketing Strategy', 'description': 'Advanced marketing strategy course by renowned industry experts.'},
            {'title': 'Financial Analysis', 'description': 'Comprehensive course on financial analysis and investment strategies.'}
        ],
}

pdf_buffer = generate_pdf(data)

# Save the PDF to a file
with open('resume_a4.pdf', 'wb') as f:
    f.write(pdf_buffer.read())