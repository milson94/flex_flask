import io
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, FrameBreak
from reportlab.platypus.flowables import KeepInFrame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, gray, lightgrey
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import letter

def build_frame_story(data, styles, frame_name):
    story = []
    if frame_name == 'left_col':
        story.append(Paragraph("Contact", styles['SectionTitleLeft']))
        if data.get('email'):
            story.append(Paragraph(data['email'], styles['ContactLeft']))
        if data.get('phone'):
            story.append(Paragraph(data['phone'], styles['ContactLeft']))
        if data.get('linkedin'):
            story.append(Paragraph(f"<u><font color='blue'>{data['linkedin']}</font></u>", styles['LinkLeft']))
        if data.get('github'):
            story.append(Paragraph(f"<u><font color='blue'>{data['github']}</font></u>", styles['LinkLeft']))
        story.append(Spacer(1, 0.2 * inch))

        if data.get('skills'):
            story.append(Paragraph("Skills", styles['SectionTitleLeft']))
            skills_list = [s.strip() for s in data['skills'].split(',')]
            for skill in skills_list:
                if skill:
                    story.append(Paragraph(f"• {skill}", styles['BulletLeft']))
            story.append(Spacer(1, 0.2 * inch))

        education_entries = data.get('education_entries', [])
        if education_entries:
            story.append(Paragraph("Education", styles['SectionTitleLeft']))
            for edu in education_entries:
                if edu.get('degree'):
                    story.append(Paragraph(edu['degree'], styles['DegreeLeft']))
                if edu.get('institution'):
                    story.append(Paragraph(edu['institution'], styles['InstitutionLeft']))
                if edu.get('edu_dates'):
                    story.append(Paragraph(edu['edu_dates'], styles['DatesLeft']))
                if edu.get('edu_details'):
                    story.append(Paragraph(edu['edu_details'], styles['DetailsLeft']))
                story.append(Spacer(1, 0.1 * inch))
            story.append(Spacer(1, 0.2 * inch))

        if data.get('hobbies'):
            story.append(Paragraph("Hobbies", styles['SectionTitleLeft']))
            hobbies_list = [h.strip() for h in data['hobbies'].split(',')]
            for hobby in hobbies_list:
                if hobby:
                    story.append(Paragraph(f"• {hobby}", styles['BulletLeft']))

    elif frame_name == 'right_col':
        if data.get('full_name'):
            story.append(Paragraph(data['full_name'].upper(), styles['NameHeaderRight']))
        story.append(Spacer(1, 0.1 * inch))

        if data.get('summary'):
            story.append(Paragraph("Summary", styles['SectionTitleRight']))
            story.append(Paragraph(data['summary'], styles['BodyTextRight']))
            story.append(Spacer(1, 0.2 * inch))

        experiences = data.get('experiences', [])
        if experiences:
            story.append(Paragraph("Experience", styles['SectionTitleRight']))
            for exp in experiences:
                if exp.get('title'):
                    story.append(Paragraph(exp['title'], styles['JobTitleRight']))
                if exp.get('company') or exp.get('dates'):
                    company_date_line = []
                    if exp.get('company'): company_date_line.append(exp['company'])
                    if exp.get('dates'): company_date_line.append(exp['dates'])
                    story.append(Paragraph(" | ".join(company_date_line), styles['CompanyDateRight']))

                if exp.get('description'):
                    desc_lines = exp['description'].split('\n')
                    for line in desc_lines:
                        line = line.strip()
                        if line.startswith(('-', '*', '•')):
                            story.append(Paragraph(line, styles['BulletRight'], bulletText=line[0]))
                        elif line:
                            story.append(Paragraph(line, styles['BodyTextRightIndented']))
                story.append(Spacer(1, 0.15 * inch))
    return story

class TwoColumnDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kwargs)

        frame_left_first = Frame(self.leftMargin, self.bottomMargin, self.width * 0.33, self.height, id='left_col_first')
        frame_right_first = Frame(self.leftMargin + self.width * 0.33 + 0.25 * inch, self.bottomMargin, self.width * 0.67 - 0.25 * inch, self.height, id='right_col_first')
        first_page_template = PageTemplate(id='FirstPage', frames=[frame_left_first, frame_right_first])

        frame_left_later = Frame(self.leftMargin, self.bottomMargin, self.width * 0.33, self.height, id='left_col_later')
        frame_right_later = Frame(self.leftMargin + self.width * 0.33 + 0.25 * inch, self.bottomMargin, self.width * 0.67 - 0.25 * inch, self.height, id='right_col_later')
        later_page_template_two_col = PageTemplate(id='LaterPageTwoCol', frames=[frame_left_later, frame_right_later])

        self.addPageTemplates([first_page_template, later_page_template_two_col])

    def beforeBuild(self):
        pass

    def afterFlowable(self, flowable):
        pass

def generate_pdf(data):
    buffer = io.BytesIO()

    margin = 0.75 * inch
    doc = TwoColumnDocTemplate(buffer, pagesize=letter, leftMargin=margin, rightMargin=margin, topMargin=margin, bottomMargin=margin)

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name='SectionTitleLeft', fontName='Helvetica-Bold', fontSize=11, spaceBefore=6, spaceAfter=3, textColor=HexColor('#2c5282')))
    styles.add(ParagraphStyle(name='ContactLeft', fontName='Helvetica', fontSize=9, leading=11, spaceAfter=2))
    styles.add(ParagraphStyle(name='LinkLeft', parent=styles['ContactLeft'], textColor=HexColor('#2b6cb0')))
    styles.add(ParagraphStyle(name='BulletLeft', parent=styles['ContactLeft'], bulletIndent=10, leftIndent=20, spaceAfter=1))
    styles.add(ParagraphStyle(name='DegreeLeft', fontName='Helvetica-Bold', fontSize=9.5, leading=11, spaceAfter=1))
    styles.add(ParagraphStyle(name='InstitutionLeft', fontName='Helvetica', fontSize=9, leading=11, spaceAfter=1))
    styles.add(ParagraphStyle(name='DatesLeft', fontName='Helvetica-Oblique', fontSize=8.5, leading=10, spaceAfter=1, textColor=gray))
    styles.add(ParagraphStyle(name='DetailsLeft', fontName='Helvetica', fontSize=8.5, leading=10, spaceAfter=3, leftIndent=10))

    styles.add(ParagraphStyle(name='NameHeaderRight', fontName='Helvetica-Bold', fontSize=26, leading=30, spaceAfter=2, textColor=HexColor('#1a202c')))
    styles.add(ParagraphStyle(name='TaglineRight', fontName='Helvetica', fontSize=11, leading=14, spaceAfter=10, textColor=gray))
    styles.add(ParagraphStyle(name='SectionTitleRight', fontName='Helvetica-Bold', fontSize=14, spaceBefore=10, spaceAfter=5, textColor=HexColor('#2c5282')))
    styles.add(ParagraphStyle(name='JobTitleRight', fontName='Helvetica-Bold', fontSize=11, leading=14, spaceAfter=1))
    styles.add(ParagraphStyle(name='CompanyDateRight', fontName='Helvetica', fontSize=10, leading=12, spaceAfter=3, textColor=gray))
    styles.add(ParagraphStyle(name='BodyTextRight', fontName='Helvetica', fontSize=10, leading=13, alignment=TA_JUSTIFY, spaceAfter=3))
    styles.add(ParagraphStyle(name='BodyTextRightIndented', parent=styles['BodyTextRight'], leftIndent=15))
    styles.add(ParagraphStyle(name='BulletRight', parent=styles['BodyTextRight'], bulletIndent=10, leftIndent=20, firstLineIndent=0, spaceAfter=2))

    side_story_content = build_frame_story(data, styles, 'left_col')
    main_story_content = build_frame_story(data, styles, 'right_col')

    final_platypus_story = []
    final_platypus_story.extend(side_story_content)
    final_platypus_story.append(FrameBreak())
    final_platypus_story.extend(main_story_content)

    doc.build(final_platypus_story)
    buffer.seek(0)
    return buffer
