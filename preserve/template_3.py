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

    # --- Section Ordering ---
    section_order = data.get('section_order', ['personal_details','summary', 'experience', 'education', 'skills', 'hobbies', 'languages', 'additional_info', 'references', 'projects','achievements','courses']) # Add more sections
    # Start with an empty story
    story = []
    col1_elements = []
    col2_elements = []
    current_column = 'col1'

    def add_to_column(element, column):
      if column == 'col1':
        col1_elements.append(element)
      else:
        col2_elements.append(element)

    # --- Adding elements to columns ---
    for section_key in section_order:

      if section_key == 'personal_details':
          personal_details_list = []
          if data.get('title_subtitle'):
              personal_details_list.append(f"<b>Job Title:</b> {data['title_subtitle']}")
          if data.get('location'):
              personal_details_list.append(f"<b>Location:</b> {data['location']}")
          if data.get('nationality'):
              personal_details_list.append(f"<b>Nationality:</b> {data['nationality']}")
          if data.get('birth_date'):
              personal_details_list.append(f"<b>Birth Date:</b> {data['birth_date']}")
          if data.get('gender'):
              personal_details_list.append(f"<b>Gender:</b> {data['gender']}")

          if personal_details_list:
              col_title = "col1" if current_column == 'col1' else "col2"
              add_to_column(Paragraph("Personal Details", styles['SectionTitle']),col_title)
              for detail in personal_details_list:
                  add_to_column(Paragraph(detail, styles['PersonalDetails']), col_title)
              add_to_column(Spacer(1, 0.1 * inch), col_title)

      if section_key == 'summary':
          if data.get('summary'):
              col_title = "col1" if current_column == 'col1' else "col2"

              add_to_column(Paragraph("Summary", styles['SectionTitle']),col_title)
              add_to_column(Paragraph(data['summary'], styles['Justified']), col_title)
              add_to_column(Spacer(1, 0.1 * inch), col_title)

      elif section_key == 'experience':
          experiences = data.get('experiences', [])
          if experiences:
              col_title = "col1" if current_column == 'col1' else "col2"

              add_to_column(Paragraph("Professional Experience", styles['SectionTitle']),col_title)
              for exp in experiences:
                  if exp.get('title') and exp.get('company'):
                      add_to_column(Paragraph(exp['title'], styles['JobTitle']), col_title)
                      add_to_column(Paragraph(f"{exp['company']} | {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'Present')}", styles['CompanyDate']), col_title)
                      if exp.get('description'):
                          desc_lines = exp['description'].split('\n')
                          for line in desc_lines:
                              line = line.strip()
                              if line.startswith(('-', '*', '•')):
                                  add_to_column(Paragraph(line, styles['BulletPoint'], bulletText=line[0]), col_title)
                              elif line:
                                  add_to_column(Paragraph(line, styles['Justified']), col_title)
                      add_to_column(Spacer(1, 0.15 * inch), col_title)

      elif section_key == 'education':
          education_entries = data.get('education_entries', [])
          if education_entries:
              col_title = "col1" if current_column == 'col1' else "col2"

              add_to_column(Paragraph("Education", styles['SectionTitle']),col_title)
              for edu in education_entries:
                  if edu.get('degree') and edu.get('institution'):
                      add_to_column(Paragraph(edu['degree'], styles['JobTitle']), col_title)
                      add_to_column(Paragraph(f"{edu['institution']} | {edu.get('start_date', 'N/A')} - {edu.get('end_date', 'Present')}", styles['CompanyDate']), col_title)
                      if edu.get('edu_details'):
                          add_to_column(Paragraph(edu['edu_details'], styles['Justified']), col_title)
                      add_to_column(Spacer(1, 0.1 * inch), col_title)

      elif section_key == 'skills':
          if data.get('skills'):
              col_title = "col1" if current_column == 'col1' else "col2"

              add_to_column(Paragraph("Skills", styles['SectionTitle']),col_title)
              add_to_column(Paragraph(data['skills'], styles['Justified']), col_title)
              add_to_column(Spacer(1, 0.1 * inch), col_title)

      elif section_key == 'hobbies':
          if data.get('hobbies'):
              col_title = "col1" if current_column == 'col1' else "col2"
              add_to_column(Paragraph("Hobbies", styles['SectionTitle']),col_title)
              add_to_column(Paragraph(data['hobbies'], styles['Justified']),col_title)
              add_to_column(Spacer(1, 0.1 * inch), col_title)

      elif section_key == 'achievements':
          key_achievements = data.get('key_achievements', [])
          if key_achievements:
              col_title = "col1" if current_column == 'col1' else "col2"
              add_to_column(Paragraph("Key Achievements", styles['SectionTitle']),col_title)
              for achievement in key_achievements:
                  if achievement.get('title'):
                      add_to_column(Paragraph(achievement['title'], styles['JobTitle']),col_title)
                      if achievement.get('description'):
                          add_to_column(Paragraph(achievement['description'], styles['NormalIndented']),col_title)
                      add_to_column(Spacer(1, 0.1 * inch),col_title)

      elif section_key == 'courses':
          courses = data.get('courses', [])
          if courses:
              col_title = "col1" if current_column == 'col1' else "col2"

              add_to_column(Paragraph("Courses", styles['SectionTitle']),col_title)
              for course in courses:
                  if course.get('title'):
                      add_to_column(Paragraph(course['title'], styles['JobTitle']),col_title)
                      if course.get('description'):
                          add_to_column(Paragraph(course['description'], styles['NormalIndented']), col_title)
                      add_to_column(Spacer(1, 0.1 * inch), col_title)

      elif section_key == 'languages':
          languages = data.get('languages', [])
          if languages:
              col_title = "col1" if current_column == 'col1' else "col2"
              add_to_column(Paragraph("Languages", styles['SectionTitle']),col_title)
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
              add_to_column(language_table, col_title)
              add_to_column(Spacer(1, 0.1 * inch), col_title)

      elif section_key == 'additional_info':
          additional_info = data.get('additional_info', [])
          if additional_info:
              col_title = "col1" if current_column == 'col1' else "col2"
              add_to_column(Paragraph("Additional Info", styles['SectionTitle']),col_title)
              for info in additional_info:
                  if info.get('title'):
                      add_to_column(Paragraph(info['title'], styles['JobTitle']),col_title)
                      if info.get('description'):
                          add_to_column(Paragraph(info['description'], styles['NormalIndented']),col_title)
                      add_to_column(Spacer(1, 0.1 * inch), col_title)

      elif section_key == 'references':
          references = data.get('references', [])
          if references:
              col_title = "col1" if current_column == 'col1' else "col2"
              add_to_column(Paragraph("References", styles['SectionTitle']),col_title)
              for ref in references:
                  if ref.get('name'):
                      add_to_column(Paragraph(ref['name'], styles['JobTitle']),col_title)
                      add_to_column(Paragraph(f"{ref.get('title', 'N/A')}", styles['CompanyDate']),col_title)
                      if ref.get('phone'):
                          add_to_column(Paragraph(f"Phone: {ref['phone']}", styles['NormalIndented']),col_title)
                      if ref.get('description'):
                          add_to_column(Paragraph(ref['description'], styles['NormalIndented']), col_title)
                      add_to_column(Spacer(1, 0.1 * inch), col_title)

      elif section_key == 'projects':
          projects = data.get('projects', [])
          if projects:
              col_title = "col1" if current_column == 'col1' else "col2"
              add_to_column(Paragraph("Projects", styles['SectionTitle']),col_title)
              for project in projects:
                  if project.get('title'):
                      add_to_column(Paragraph(project['title'], styles['JobTitle']),col_title)
                      if project.get('description'):
                          add_to_column(Paragraph(project['description'], styles['NormalIndented']),col_title)
                      if project.get('dates'):
                          add_to_column(Paragraph(f"Dates: {project['dates']}", styles['CompanyDate']), col_title)
                  add_to_column(Spacer(1, 0.1 * inch), col_title)
      # Toggle to the next column, making it go col1, col2 ,col1, col2
      current_column = 'col2' if current_column == 'col1' else 'col1'
    story.extend(header_content)  # Add header content first
    story.extend(col1_elements)
    story.extend(col2_elements)
    # Build the document
    doc.build(story)
    buffer.seek(0)
    return buffer

# Example usage
data = {
    'full_name': 'Ellen Johnson',
    'title_subtitle': 'Marketing Manager',  # Added title_subtitle
    'location': 'Los Angeles, CA',  # Added location
    'nationality': 'American',  # Added nationality
    'birth_date': '1990-01-01',  # Added birth_date
    'gender': 'Female',  # Added gender
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
    'key_achievements': [
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