import io
import os # Import os for path handling

from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Spacer, HRFlowable, KeepTogether, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, gray, black, white
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.platypus.frames import Frame
from reportlab.platypus import BaseDocTemplate, PageTemplate

class TwoColumnDocument(BaseDocTemplate):
    """
    A custom document template for a two-column layout.
    Content automatically flows from the first column to the second,
    and then to a new page if both columns are full.
    """
    def __init__(self, filename, **kwargs):
        BaseDocTemplate.__init__(self, filename, **kwargs)
        self.pageSize = letter
        margin = 0.5 * inch # Page margins
        column_gap = 0.4 * inch # Space between columns
        
        # Calculate width of each column
        column_width = (self.pageSize[0] - 2 * margin - column_gap) / 2
        
        # Define the two frames for the columns
        frame1 = Frame(
            x1=margin,  # X-coordinate of the left edge
            y1=self.bottomMargin, # Y-coordinate of the bottom edge
            width=column_width,
            height=self.height, # Height of the frame
            id='col1',
            showBoundary=0 # Set to 1 for debugging frame boundaries
        )
        frame2 = Frame(
            x1=margin + column_width + column_gap, # X-coordinate for the second column
            y1=self.bottomMargin,
            width=column_width,
            height=self.height,
            id='col2',
            showBoundary=0
        )
        
        # Add a page template that uses both frames.
        # ReportLab will automatically flow content into frame1, then frame2,
        # and then create a new page using this template if both frames are full.
        self.addPageTemplates(
            [PageTemplate(id='TwoColumn', frames=[frame1, frame2])]
        )

# Define a mapping for section icons
# IMPORTANT: Ensure these image files exist at the specified relative paths
# For example, if your script is in 'my_project/' and icons are in 'my_project/static/images/template_02/',
# this path will work.
BASE_ICON_PATH = 'static/images/template_02/'
SECTION_ICONS = {
    'personal': os.path.join(BASE_ICON_PATH, 'personal.png'),
    'summary': os.path.join(BASE_ICON_PATH, 'summary.png'),
    'experience': os.path.join(BASE_ICON_PATH, 'experience.png'),
    'education': os.path.join(BASE_ICON_PATH, 'education.png'),
    'achievements': os.path.join(BASE_ICON_PATH, 'achievements.png'),
    'courses': os.path.join(BASE_ICON_PATH, 'courses.png'),
    'skills': os.path.join(BASE_ICON_PATH, 'skills.png'),
    'hobbies': os.path.join(BASE_ICON_PATH, 'hobbies.png'),
    'languages': os.path.join(BASE_ICON_PATH, 'languages.png'),
    'additional_info': os.path.join(BASE_ICON_PATH, 'info.png'),
    'references': os.path.join(BASE_ICON_PATH, 'references.png'),
    'projects': os.path.join(BASE_ICON_PATH, 'projects.png'),
}

def generate_pdf(data):
    """Generates a two-column resume PDF using ReportLab from the given data."""
    buffer = io.BytesIO()
    doc = TwoColumnDocument(buffer) # Use the custom two-column document template
    styles = getSampleStyleSheet()

    # --- Custom Styles ---
    # Adjusted MainTitle for "CURRÍCULO VITAE"
    styles.add(ParagraphStyle(name='MainTitle', fontName='Helvetica-Bold', fontSize=26, leading=30, alignment=TA_LEFT, spaceAfter=0.2 * inch))
    
    # New style for the name with green background
    styles.add(ParagraphStyle(name='NameBoxParagraph', fontName='Helvetica-Bold', fontSize=20, leading=24, alignment=TA_LEFT, 
                                backColor=HexColor('#4CAF50'), textColor=white, 
                                spaceBefore=0.1 * inch, spaceAfter=0.1 * inch,
                                leftIndent=0.1 * inch, rightIndent=0.1 * inch, # Small padding
                                borderPadding=(4, 4, 4, 4) # padding inside the 'box'
                                ))
    
    # Original ContactHeader remains as it was
    styles.add(ParagraphStyle(name='ContactHeader', fontName='Helvetica', fontSize=9, leading=11, alignment=TA_LEFT, spaceAfter=0.08 * inch))
    
    # SectionTitle now green
    styles.add(ParagraphStyle(name='SectionTitle', fontName='Helvetica-Bold', fontSize=13, leading=16, spaceBefore=0.15 * inch, spaceAfter=0.08 * inch, textColor=HexColor('#4CAF50')))
    
    styles.add(ParagraphStyle(name='JobTitle', fontName='Helvetica-Bold', fontSize=10, leading=13))
    styles.add(ParagraphStyle(name='CompanyDate', fontName='Helvetica-Oblique', fontSize=9, leading=11, textColor=gray, spaceAfter=0.04 * inch))
    styles.add(ParagraphStyle(name='BulletPoint', parent=styles['Normal'], leftIndent=0.2 * inch, bulletIndent=0.1 * inch, firstLineIndent=0, spaceBefore=0.04 * inch, splitLongWords=True,))
    styles.add(ParagraphStyle(name='NormalIndented', parent=styles['Normal'], leftIndent=0.2 * inch, splitLongWords=True,))
    styles.add(ParagraphStyle(name='NormalJustified', parent=styles['Normal'], alignment=TA_JUSTIFY, splitLongWords=True,))
    styles.add(ParagraphStyle(name='PersonalDetails', parent=styles['Normal'], alignment=TA_LEFT, spaceAfter=0.04 * inch, splitLongWords=True,))

    story = [] # This list will hold all the flowables for the PDF

    # --- Main Title ---
    story.append(Paragraph("CURRÍCULO VITAE", styles['MainTitle']))

    # --- Personal Details Section ---
    personal_details_elements = [] # Collect elements for KeepTogether
    
    # Section title with icon
    personal_details_elements.append(
        Table([[
            Image(SECTION_ICONS.get('personal', ''), width=0.18*inch, height=0.18*inch),
            Paragraph("Detalhes Pessoais", styles['SectionTitle'])
        ]], colWidths=[0.25*inch, None], hAlign='LEFT', style=TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (0,0), 0),
            ('RIGHTPADDING', (0,0), (0,0), 0.1*inch),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
    )

    if data.get('full_name'):
        # Name with greenish background box
        personal_details_elements.append(Paragraph(data['full_name'].upper(), styles['NameBoxParagraph']))
        
    contact_info_parts = []
    if data.get('email'): contact_info_parts.append(f"Email: {data['email']}")
    if data.get('phone'): contact_info_parts.append(f"Telefone: {data['phone']}")
    if data.get('linkedin'): contact_info_parts.append(f"LinkedIn: {data['linkedin']}")
    if data.get('github'): contact_info_parts.append(f"GitHub: {data['github']}")
    if data.get('website'): contact_info_parts.append(f"Website: {data['website']}")
    if data.get('address'): contact_info_parts.append(f"Endereço: {data['address']}")

    if contact_info_parts:
        personal_details_elements.append(Paragraph(" | ".join(contact_info_parts), styles['ContactHeader']))

    additional_personal_details = []
    if data.get('birth_date'): additional_personal_details.append(f"Data de Nascimento: {data['birth_date']}")
    if data.get('place_of_birth'): additional_personal_details.append(f"Local de Nascimento: {data['place_of_birth']}")
    if data.get('nationality'): additional_personal_details.append(f"Nacionalidade: {data['nationality']}")
    if data.get('gender'): additional_personal_details.append(f"Gênero: {data['gender']}")
    if data.get('driving_license'): additional_personal_details.append(f"Carta de Condução: {data['driving_license']}")
    if data.get('marital_status'): additional_personal_details.append(f"Estado Civil: {data['marital_status']}")
    if data.get('military_service'): additional_personal_details.append(f"Serviço Militar: {data['military_service']}")
    if data.get('cargo'): additional_personal_details.append(f"Cargo: {data['cargo']}")

    if additional_personal_details:
        for detail in additional_personal_details:
            personal_details_elements.append(Paragraph(detail, styles['PersonalDetails']))

    personal_details_elements.append(Spacer(1, 0.1 * inch))
    personal_details_elements.append(HRFlowable(width="100%", thickness=0.5, color=gray, spaceBefore=0.1 * inch, spaceAfter=0.1 * inch))
    
    # Wrap the entire personal details section in KeepTogether to prevent it from splitting
    story.append(KeepTogether(personal_details_elements))

    # --- Section Ordering ---
    section_order = data.get('section_order', ['summary', 'experience', 'education', 'achievements', 'courses', 'skills', 'hobbies', 'languages', 'additional_info', 'references', 'projects'])

    # Add content for all sections to the single 'story' list
    for section_key in section_order:
        # Create a helper function to add section title with icon
        def add_section_title(title_text, section_key_for_icon):
            icon_path = SECTION_ICONS.get(section_key_for_icon, '')
            # Check if icon file exists to avoid errors and fallback if not
            if icon_path and os.path.exists(icon_path):
                return Table([[
                    Image(icon_path, width=0.18*inch, height=0.18*inch),
                    Paragraph(title_text, styles['SectionTitle'])
                ]], colWidths=[0.25*inch, None], hAlign='LEFT', style=TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (0,0), 0),
                    ('RIGHTPADDING', (0,0), (0,0), 0.1*inch),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ]))
            else:
                # Fallback to just the paragraph if icon not found
                return Paragraph(title_text, styles['SectionTitle'])


        if section_key == 'summary':
            if data.get('summary'):
                story.append(add_section_title("Resumo", 'summary'))
                story.append(Paragraph(data['summary'], styles['NormalJustified']))
                story.append(Spacer(1, 0.1 * inch))

        elif section_key == 'experience':
            experiences = data.get('experiences', [])
            if experiences:
                story.append(add_section_title("Experiência Profissional", 'experience'))
                for exp in experiences:
                    exp_block = [] # Elements for a single experience entry
                    if exp.get('title') and exp.get('company'):
                        exp_block.append(Paragraph(exp['title'], styles['JobTitle']))
                        company_date_str = f"{exp['company']}"
                        if exp.get('start_date'):
                            company_date_str += f" | {exp.get('start_date')}"
                        if exp.get('end_date'):
                            company_date_str += f" - {exp.get('end_date')}"
                        else:
                            if exp.get("is_present"):
                                company_date_str += " - Presente"

                        exp_block.append(Paragraph(company_date_str, styles['CompanyDate']))
                        if exp.get('description'):
                            desc_lines = exp['description'].split('\n')
                            for line in desc_lines:
                                line = line.strip()
                                if line.startswith(('-', '*', '•')):
                                    exp_block.append(Paragraph(line, styles['BulletPoint'], bulletText=line[0]))
                                elif line:
                                    exp_block.append(Paragraph(line, styles['NormalIndented']))
                        exp_block.append(Spacer(1, 0.15 * inch))
                    story.append(KeepTogether(exp_block)) # Keep each experience block together

        elif section_key == 'education':
            education_entries = data.get('education_entries', [])
            if education_entries:
                story.append(add_section_title("Formação Acadêmica", 'education'))
                for edu in education_entries:
                    edu_block = [] # Elements for a single education entry
                    if edu.get('degree') and edu.get('institution'):
                        edu_block.append(Paragraph(edu['degree'], styles['JobTitle']))
                        edu_dates_str = f"{edu['institution']}"
                        if edu.get('start_date'):
                            edu_dates_str += f" | {edu.get('start_date')}"
                        if edu.get('end_date'):
                            edu_dates_str += f" - {edu.get('end_date')}"
                        else:
                            if edu.get("is_present"):
                                edu_dates_str += " - Presente" 
                        edu_block.append(Paragraph(edu_dates_str, styles['CompanyDate']))

                        if edu.get('edu_details'):
                            edu_block.append(Paragraph(edu['edu_details'], styles['NormalIndented']))
                        edu_block.append(Spacer(1, 0.1 * inch))
                    story.append(KeepTogether(edu_block)) # Keep each education entry together

        elif section_key == 'achievements':
            key_achievements = data.get('key_achievements', [])
            if key_achievements:
                story.append(add_section_title("Principais Conquistas", 'achievements'))
                for achievement in key_achievements:
                    achievement_block = [] # Elements for a single achievement entry
                    if achievement.get('title'):
                        achievement_block.append(Paragraph(achievement['title'], styles['JobTitle']))
                        if achievement.get('description'):
                            achievement_block.append(Paragraph(achievement['description'], styles['NormalIndented']))
                        achievement_block.append(Spacer(1, 0.1 * inch))
                    story.append(KeepTogether(achievement_block)) # Keep each achievement together

        elif section_key == 'courses':
            courses = data.get('courses', [])
            if courses:
                story.append(add_section_title("Cursos/Certificações", 'courses'))
                for course in courses:
                    course_block = [] # Elements for a single course entry
                    if course.get('title'):
                        course_block.append(Paragraph(course['title'], styles['JobTitle']))
                        if course.get('description'):
                            course_block.append(Paragraph(course['description'], styles['NormalIndented']))
                        course_block.append(Spacer(1, 0.1 * inch))
                    story.append(KeepTogether(course_block)) # Keep each course entry together

        elif section_key == 'skills':
            if data.get('skills'):
                story.append(add_section_title("Habilidades", 'skills'))
                story.append(Paragraph(data['skills'], styles['NormalJustified']))
                story.append(Spacer(1, 0.1 * inch))

        elif section_key == 'hobbies':
            if data.get('hobbies'):
                story.append(add_section_title("Hobbies", 'hobbies'))
                story.append(Paragraph(data['hobbies'], styles['NormalJustified']))
                story.append(Spacer(1, 0.1 * inch))

        elif section_key == 'languages':
            languages = data.get('languages', [])
            if languages:
                story.append(add_section_title("Proficiência em Línguas", 'languages'))
                language_data = [["Língua", "Leitura", "Escrita", "Conversação"]]
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
                    ('BACKGROUND', (0, 1), (-1, -1), white),
                    ('GRID', (0, 0), (-1, -1), 1, black)
                ]))
                story.append(language_table)
                story.append(Spacer(1, 0.1 * inch))

        elif section_key == 'additional_info':
            additional_info = data.get('additional_info', [])
            if additional_info:
                story.append(add_section_title("Informações Adicionais", 'additional_info'))
                for info in additional_info:
                    info_block = []
                    if info.get('title'):
                        info_block.append(Paragraph(info['title'], styles['JobTitle']))
                        if info.get('description'):
                            info_block.append(Paragraph(info['description'], styles['NormalIndented']))
                        info_block.append(Spacer(1, 0.1 * inch))
                    story.append(KeepTogether(info_block))

        elif section_key == 'references':
            references = data.get('references', [])
            if references:
                story.append(add_section_title("Referências", 'references'))
                for ref in references:
                    ref_block = []
                    if ref.get('name'):
                        ref_block.append(Paragraph(ref['name'], styles['JobTitle']))
                        ref_block.append(Paragraph(f"{ref.get('title', 'N/A')}", styles['CompanyDate']))
                        if ref.get('phone'):
                            ref_block.append(Paragraph(f"Telefone: {ref['phone']}", styles['NormalIndented']))
                        if ref.get('description'):
                            ref_block.append(Paragraph(ref['description'], styles['NormalIndented']))
                        ref_block.append(Spacer(1, 0.1 * inch))
                    story.append(KeepTogether(ref_block))

        elif section_key == 'projects':
            projects = data.get('projects', [])
            if projects:
                story.append(add_section_title("Projetos", 'projects'))
                for project in projects:
                    project_block = []
                    if project.get('title'):
                        project_block.append(Paragraph(project['title'], styles['JobTitle']))
                        if project.get('description'):
                            project_block.append(Paragraph(project['description'], styles['NormalIndented']))
                        if project.get('dates'):
                            project_block.append(Paragraph(f"Datas: {project['dates']}", styles['CompanyDate']))
                        project_block.append(Spacer(1, 0.1 * inch))
                    story.append(KeepTogether(project_block))

    # Build the PDF document with the generated story
    doc.build(story)
    buffer.seek(0)
    return buffer