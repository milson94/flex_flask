import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, gray, white
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER


def generate_pdf(data):
    """Gera um currículo em PDF usando ReportLab, considerando a ordem das seções e incluindo todos os dados do formulário."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=0.75 * inch, leftMargin=0.75 * inch,
                            topMargin=0.75 * inch, bottomMargin=0.75 * inch)

    styles = getSampleStyleSheet()

    # --- Estilos Customizados ---
    styles.add(ParagraphStyle(name='MainTitle',
                              fontName='Helvetica-Bold',
                              fontSize=28,
                              leading=32,
                              alignment=TA_CENTER,
                              spaceAfter=0.3 * inch))

    styles.add(ParagraphStyle(name='NameHeader',
                              fontName='Helvetica-Bold',
                              fontSize=24,
                              leading=28,
                              alignment=TA_LEFT,
                              spaceAfter=0.05 * inch))

    styles.add(ParagraphStyle(name='ContactHeader',
                              fontName='Helvetica',
                              fontSize=10,
                              leading=12,
                              alignment=TA_LEFT,
                              spaceAfter=0.1 * inch))

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

    styles.add(ParagraphStyle(name='NormalJustified',
                              parent=styles['Normal'],
                              alignment=TA_JUSTIFY))

    styles.add(ParagraphStyle(name='PersonalDetails',
                              parent=styles['Normal'],
                              alignment=TA_JUSTIFY,
                              spaceAfter=0.05 * inch))

    story = []

    # --- Título Principal ---
    story.append(Paragraph("CURRICULUM VITAE", styles['MainTitle']))

    # --- Seção de Detalhes Pessoais ---
    story.append(Paragraph("Detalhes Pessoais", styles['SectionTitle']))

    if data.get('full_name'):
        story.append(Paragraph(data['full_name'].upper(), styles['NameHeader']))

    contact_info = []
    if data.get('email'): contact_info.append(f"Email: {data['email']}")
    if data.get('phone'): contact_info.append(f"Telefone: {data['phone']}")
    if data.get('linkedin'): contact_info.append(f"LinkedIn: {data['linkedin']}")
    if data.get('github'): contact_info.append(f"GitHub: {data['github']}")
    if data.get('website'): contact_info.append(f"Website: {data['website']}")
    if data.get('address'): contact_info.append(f"Endereço: {data['address']}")

    if contact_info:
        story.append(Paragraph(" | ".join(contact_info), styles['ContactHeader']))

    additional_personal_details = []

    if data.get('birth_date'): additional_personal_details.append(f"Data de Nascimento: {data['birth_date']}")
    if data.get('place_of_birth'): additional_personal_details.append(f"Local de Nascimento: {data['place_of_birth']}")  # Novo
    if data.get('nationality'): additional_personal_details.append(f"Nacionalidade: {data['nationality']}")
    if data.get('gender'): additional_personal_details.append(f"Gênero: {data['gender']}")
    if data.get('driving_license'): additional_personal_details.append(f"Carta de Condução: {data['driving_license']}")
    if data.get('marital_status'): additional_personal_details.append(f"Estado Civil: {data['marital_status']}")
    if data.get('military_service'): additional_personal_details.append(f"Serviço Militar: {data['military_service']}")
    if data.get('cargo'): additional_personal_details.append(f"Cargo: {data['cargo']}") # Nova

    if additional_personal_details:
        for detail in additional_personal_details:
            story.append(Paragraph(detail, styles['PersonalDetails']))

    story.append(Spacer(1, 0.1 * inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=gray, spaceBefore=0.1 * inch, spaceAfter=0.1 * inch))

    # --- Ordenação das Seções ---
    section_order = data.get('section_order', ['summary', 'experience', 'education', 'achievements', 'courses', 'skills', 'hobbies', 'languages', 'additional_info', 'references', 'projects'])
    # Iterar pelas seções ordenadas

    for section_key in section_order:
        if section_key == 'summary':
            if data.get('summary'):
                story.append(Paragraph("Resumo", styles['SectionTitle']))
                story.append(Paragraph(data['summary'], styles['NormalJustified']))
                story.append(Spacer(1, 0.1 * inch))

        elif section_key == 'achievements':
            key_achievements = data.get('key_achievements', [])
            if key_achievements:
                story.append(Paragraph("Principais Conquistas", styles['SectionTitle']))
                for achievement in key_achievements:
                    if achievement.get('title'):
                        story.append(Paragraph(achievement['title'], styles['JobTitle']))
                        if achievement.get('description'):
                            story.append(Paragraph(achievement['description'], styles['NormalIndented']))
                        story.append(Spacer(1, 0.1 * inch))

        elif section_key == 'experience':
            experiences = data.get('experiences', [])
            if experiences:
                story.append(Paragraph("Experiência Profissional", styles['SectionTitle']))
                for exp in experiences:
                    if exp.get('title') and exp.get('company'):
                        story.append(Paragraph(exp['title'], styles['JobTitle']))
                        company_date_str = f"{exp['company']}"
                        if exp.get('start_date'):
                            company_date_str += f" | {exp.get('start_date')}"
                        if exp.get('end_date'):
                            company_date_str += f" - {exp.get('end_date')}"
                        else:
                            if exp.get("is_present"):
                                company_date_str += " - Presente"

                        story.append(Paragraph(company_date_str, styles['CompanyDate']))
                        if exp.get('description'):
                            desc_lines = exp['description'].split('\n')
                            for line in desc_lines:
                                line = line.strip()
                                if line.startswith(('-', '*', '•')):
                                    story.append(Paragraph(line, styles['BulletPoint'], bulletText=line[0]))
                                elif line:
                                    story.append(Paragraph(line, styles['NormalIndented']))
                        story.append(Spacer(1, 0.15 * inch))

        elif section_key == 'education':
            education_entries = data.get('education_entries', [])
            if education_entries:
                story.append(Paragraph("Formação Acadêmica", styles['SectionTitle']))
                for edu in education_entries:
                    if edu.get('degree') and edu.get('institution'):
                        story.append(Paragraph(edu['degree'], styles['JobTitle']))
                        edu_dates_str = f"{edu['institution']}"
                        if edu.get('start_date'):
                            edu_dates_str += f" | {edu.get('start_date')}"
                        if edu.get('end_date'):
                            edu_dates_str += f" - {edu.get('end_date')}"
                        else:
                            if edu.get("is_present"):
                                edu_dates_str += " - Presente"
                        story.append(Paragraph(edu_dates_str, styles['CompanyDate']))

                        if edu.get('edu_details'):
                            story.append(Paragraph(edu['edu_details'], styles['NormalIndented']))
                        story.append(Spacer(1, 0.1 * inch))

        elif section_key == 'courses':
            courses = data.get('courses', [])
            if courses:
                story.append(Paragraph("Cursos/Certificações", styles['SectionTitle']))
                for course in courses:
                    if course.get('title'):
                        story.append(Paragraph(course['title'], styles['JobTitle']))
                        if course.get('description'):
                            story.append(Paragraph(course['description'], styles['NormalIndented']))
                        story.append(Spacer(1, 0.1 * inch))

        elif section_key == 'skills':
            if data.get('skills'):
                story.append(Paragraph("Habilidades", styles['SectionTitle']))
                story.append(Paragraph(data['skills'], styles['NormalJustified']))
                story.append(Spacer(1, 0.1 * inch))

        elif section_key == 'hobbies':
            if data.get('hobbies'):
                story.append(Paragraph("Hobbies", styles['SectionTitle']))
                story.append(Paragraph(data['hobbies'], styles['NormalJustified']))
                story.append(Spacer(1, 0.1 * inch))

        elif section_key == 'languages':
            # --- Tabela de Proficiência em Línguas ---
            languages = data.get('languages', [])
            if languages:
                story.append(Paragraph("Proficiência em Línguas", styles['SectionTitle']))
                language_data = [["Língua", "Leitura", "Escrita", "Conversação"]]  # Cabeçalho
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
                    ('BACKGROUND', (0, 1), (-1, -1), white),  # Cor de fundo das células de dados
                    ('GRID', (0, 0), (-1, -1), 1, black)
                ]))
                story.append(language_table)
                story.append(Spacer(1, 0.1 * inch))

        elif section_key == 'additional_info':
            additional_info = data.get('additional_info', [])
            if additional_info:
                story.append(Paragraph("Informações Adicionais", styles['SectionTitle']))
                for info in additional_info:
                    if info.get('title'):
                        story.append(Paragraph(info['title'], styles['JobTitle']))
                        if info.get('description'):
                            story.append(Paragraph(info['description'], styles['NormalIndented']))
                        story.append(Spacer(1, 0.1 * inch))

        elif section_key == 'references':
            references = data.get('references', [])
            if references:
                story.append(Paragraph("Referências", styles['SectionTitle']))
                for ref in references:
                    if ref.get('name'):
                        story.append(Paragraph(ref['name'], styles['JobTitle']))
                        story.append(Paragraph(f"{ref.get('title', 'N/A')}", styles['CompanyDate']))
                        if ref.get('phone'):
                            story.append(Paragraph(f"Telefone: {ref['phone']}", styles['NormalIndented']))
                        if ref.get('description'):
                            story.append(Paragraph(ref['description'], styles['NormalIndented']))
                        story.append(Spacer(1, 0.1 * inch))

        elif section_key == 'projects':
            projects = data.get('projects', [])
            if projects:
                story.append(Paragraph("Projetos", styles['SectionTitle']))
                for project in projects:
                    if project.get('title'):
                        story.append(Paragraph(project['title'], styles['JobTitle']))
                        if project.get('description'):
                            story.append(Paragraph(project['description'], styles['NormalIndented']))
                        if project.get('dates'):
                            story.append(Paragraph(f"Datas: {project['dates']}", styles['CompanyDate']))
                        story.append(Spacer(1, 0.1 * inch))

    doc.build(story)
    buffer.seek(0)
    return buffer