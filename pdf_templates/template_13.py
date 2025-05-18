import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Frame, PageTemplate, Table, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, gray
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Helper function to potentially round corners of an image (requires Pillow)
# This is complex and often better done outside ReportLab if needed precisely.
# For this example, we'll just use the standard rectangular image.
# If you need a circular image, preprocess it with Pillow using a circular mask.

def generate_resume_pdf(data, profile_image_path=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=0.5*inch, leftMargin=0.5*inch, # Adjusted margins slightly based on image
                            topMargin=0.5*inch, bottomMargin=0.5*inch)

    styles = getSampleStyleSheet()

    # --- Custom Colors ---
    color_primary = HexColor('#007BFF') # Example primary color (blueish) - adjust based on image if needed
    color_text_dark = HexColor('#333333')
    color_text_light = HexColor('#555555')
    color_line = HexColor('#E0E0E0') # Light grey line color

    # --- Custom Styles ---
    styles.add(ParagraphStyle(name='Name',
                              fontName='Helvetica-Bold',
                              fontSize=28, # Adjusted size
                              leading=34,
                              textColor=HexColor('#000000'))) # Assuming black or very dark grey

    styles.add(ParagraphStyle(name='Headline',
                              fontName='Helvetica',
                              fontSize=12, # Adjusted size
                              leading=14,
                              textColor=color_primary,
                              spaceAfter=0.1*inch)) # Space after headline

    styles.add(ParagraphStyle(name='ContactInfo',
                              fontName='Helvetica',
                              fontSize=10,
                              leading=12,
                              textColor=color_text_dark))

    styles.add(ParagraphStyle(name='SectionTitle',
                              fontName='Helvetica-Bold',
                              fontSize=12, # Smaller section title
                              leading=15,
                              spaceBefore=0.25*inch, # More space before sections
                              spaceAfter=0.1*inch, # Space after title before content
                              textColor=color_text_dark))

    styles.add(ParagraphStyle(name='JobTitle',
                              fontName='Helvetica-Bold',
                              fontSize=12,
                              leading=14,
                              spaceBefore=0.15*inch, # Space before each job
                              textColor=color_text_dark))

    styles.add(ParagraphStyle(name='CompanyLocationDate',
                              fontName='Helvetica',
                              fontSize=10,
                              leading=12,
                              textColor=color_text_light,
                              spaceAfter=0.05*inch))

    styles.add(ParagraphStyle(name='BulletPoint',
                              parent=styles['Normal'], # Inherit most properties from Normal
                              fontName='Helvetica',
                              fontSize=10,
                              leading=12,
                              leftIndent=0.15*inch, # Indent bullet text
                              bulletIndent=0.05*inch, # Indent bullet symbol
                              spaceBefore=0.02*inch, # Small space between bullets
                              textColor=color_text_dark))

    styles.add(ParagraphStyle(name='EducationDegree',
                              fontName='Helvetica-Bold',
                              fontSize=12,
                              leading=14,
                              spaceBefore=0.15*inch,
                              textColor=color_text_dark))

    styles.add(ParagraphStyle(name='InstitutionDate',
                              fontName='Helvetica',
                              fontSize=10,
                              leading=12,
                              textColor=color_text_light,
                              spaceAfter=0.05*inch))

    styles.add(ParagraphStyle(name='EducationDetails',
                              parent=styles['Normal'],
                              fontName='Helvetica',
                              fontSize=10,
                              leading=12,
                              leftIndent=0.15*inch,
                              textColor=color_text_dark))

    styles.add(ParagraphStyle(name='KeyAchievementTitle',
                              fontName='Helvetica-Bold',
                              fontSize=10,
                              leading=12,
                              spaceBefore=0.1*inch, # Space before achievement title
                              textColor=color_text_dark))

    styles.add(ParagraphStyle(name='KeyAchievementDescription',
                              parent=styles['Normal'],
                              fontName='Helvetica',
                              fontSize=10,
                              leading=12,
                              leftIndent=0.15*inch, # Indent description slightly
                              spaceAfter=0.15*inch, # Space after achievement block
                              textColor=color_text_dark))

    styles.add(ParagraphStyle(name='SkillPill', # Approximation of the pill style
                                fontName='Helvetica',
                                fontSize=9, # Smaller font for pills
                                leading=11,
                                backColor=HexColor('#E0F2F7'), # Light blue background
                                borderWidth=0.5,
                                borderColor=HexColor('#B3E5FC'), # Slightly darker border
                                borderPadding=3, # Padding inside the border
                                cornerRadius=5, # Rounded corners
                                spaceBefore=3, # Space before each skill
                                spaceAfter=3, # Space after each skill
                                leftIndent=0, # Important for flowable in table cell
                                rightIndent=0,
                                alignment=TA_CENTER # Center text in pill
                                ))
    # Note: SkillPill style is conceptually defined but applying it directly
    # to Paragraphs in a flowing text won't create the border/background effect.
    # This style definition is more useful if each skill was a Flowable in a Table cell.
    # For simplicity in a flowing column, we'll list skills comma-separated with Normal style.

    styles.add(ParagraphStyle(name='Language',
                              fontName='Helvetica',
                              fontSize=10,
                              leading=12,
                              textColor=color_text_dark))

    styles.add(ParagraphStyle(name='FooterText',
                              fontName='Helvetica',
                              fontSize=8,
                              leading=10,
                              textColor=gray,
                              alignment=TA_LEFT))

    styles.add(ParagraphStyle(name='SummaryText',
                              parent=styles['Normal'],
                              fontName='Helvetica',
                              fontSize=10,
                              leading=12,
                              textColor=color_text_dark))


    story = []

    # --- Header Section (Name, Title, Contact Info + Image) ---
    header_table_data = []

    # Left cell: Name, Headline, Contact Info
    header_text_story = []
    if data.get('full_name'):
        header_text_story.append(Paragraph(data['full_name'].upper(), styles['Name']))
    if data.get('headline'):
         header_text_story.append(Paragraph(data['headline'], styles['Headline']))

    contact_info_items = []
    if data.get('email'): contact_info_items.append(f"help@{data.get('email_domain', 'domain.com')}") # Assuming example format
    if data.get('linkedin'): contact_info_items.append(f"linkedin.com/in/{data['linkedin']}")
    if data.get('location'): contact_info_items.append(data['location'])

    contact_paragraph_text = " • ".join(contact_info_items) # Use bullet separator as in image
    if contact_paragraph_text:
        header_text_story.append(Paragraph(contact_paragraph_text, styles['ContactInfo']))

    # Right cell: Profile Image
    img_flowable = None
    if profile_image_path:
        try:
            img = ImageReader(profile_image_path)
            # Determine image size - let's make it approx 1 inch wide
            img_width = 1.0 * inch
            img_height = img_width * img.getSize()[1] / img.getSize()[0] # Maintain aspect ratio
            img_flowable = Image(profile_image_path, width=img_width, height=img_height)
        except Exception as e:
            print(f"Could not load image {profile_image_path}: {e}")
            img_flowable = None # Don't add if loading fails

    # Add content to the table data row
    if img_flowable:
         header_table_data.append([header_text_story, img_flowable])
         # Define column widths: text column takes remaining space after image
         header_col_widths = [letter[0] - doc.leftMargin - doc.rightMargin - img_width - 0.2*inch, img_width] # Added a small gap
    else:
         header_table_data.append([header_text_story])
         header_col_widths = [letter[0] - doc.leftMargin - doc.rightMargin]


    header_table_style = [
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Vertically center content in cells
        # ('GRID', (0,0), (-1,-1), 0.5, gray) # Uncomment to see table boundaries
    ]

    header_table = Table(header_table_data, colWidths=header_col_widths, style=header_table_style)
    story.append(header_table)
    story.append(Spacer(1, 0.1*inch)) # Small space after header block

    # --- Horizontal Line after Header ---
    story.append(HRFlowable(width="100%", thickness=1, color=color_line, spaceBefore=0, spaceAfter=0.1*inch, hAlign='CENTER'))


    # --- Define Two-Column Layout Frames ---
    column_gap = 0.3 * inch # Gap between columns
    page_width, page_height = letter

    # Calculate available height below header/HR line
    # Estimate header height + HR height + space after HR
    # A more robust way is to calculate the actual height of header flowables,
    # but for a fixed layout, estimation is often sufficient.
    # Let's just use the standard top margin for the frame start Y.
    # The header content is already added to the story *before* the frames activate,
    # so the frames will start below wherever the header content ends.

    # Frame Y start is bottom margin
    frame_y_start = doc.bottomMargin

    # Frame height is from bottom margin up to top margin
    frame_height = page_height - doc.topMargin - doc.bottomMargin

    # Calculate available width for columns (total width minus margins)
    usable_width = page_width - doc.leftMargin - doc.rightMargin

    # Calculate the width of each column (total usable width minus gap, divided by 2)
    column_width = (usable_width - column_gap) / 2

    # Define the first column frame (left margin to [left margin + column width])
    frame1 = Frame(doc.leftMargin, frame_y_start, column_width, frame_height, id='col1')

    # Define the second column frame (left margin + column width + gap to right margin)
    frame2 = Frame(doc.leftMargin + column_width + column_gap, frame_y_start, column_width, frame_height, id='col2')

    # Create a page template with the two columns
    # Frames listed in the order content should flow: frame1 (left) then frame2 (right)
    page_template = PageTemplate(id='TwoColumns', frames=[frame1, frame2]) # No onPage for vertical line as image doesn't show one
    doc.addPageTemplates([page_template])


    # --- Body Content (Flows into Columns: Left -> Right) ---

    # Content that should flow into the LEFT column first
    left_column_story = []

    # --- Professional Experience (Left Column) ---
    experiences = data.get('experiences', [])
    if experiences:
        left_column_story.append(Paragraph("EXPERIENCE", styles['SectionTitle']))
        left_column_story.append(HRFlowable(width="100%", thickness=1, color=color_line, spaceBefore=0, spaceAfter=0.1*inch))
        for i, exp in enumerate(experiences):
            if exp.get('title'):
                left_column_story.append(Paragraph(exp['title'], styles['JobTitle']))
            company_loc_date = []
            if exp.get('company'): company_loc_date.append(exp['company'])
            if exp.get('dates'): company_loc_date.append(f"🗓️ {exp['dates']}") # Using calendar icon emoji - might not render
            if exp.get('location'): company_loc_date.append(f"📍 {exp['location']}") # Using location icon emoji
            if company_loc_date:
                # Join with spaces, add special formatting for company/dates/location part if needed
                 company_line_parts = []
                 if exp.get('company'): company_line_parts.append(f"<font color='{color_primary}'>{exp['company']}</font>")
                 if exp.get('dates'): company_line_parts.append(f"🗓️ {exp['dates']}")
                 if exp.get('location'): company_line_parts.append(f"📍 {exp['location']}")

                 left_column_story.append(Paragraph(" ".join(company_line_parts), styles['CompanyLocationDate']))

            if exp.get('description'):
                # Split description by newlines and add as bullet points
                desc_lines = exp['description'].split('\n')
                for line in desc_lines:
                    line = line.strip()
                    if line: # Only add non-empty lines
                         # Assume lines starting with '-' are bullet points, others are normal indented
                         if line.startswith('-'):
                              left_column_story.append(Paragraph(line[1:].strip(), styles['BulletPoint'], bulletText='•'))
                         else:
                              # If lines don't start with '-', maybe they are just paragraphs within the job
                               left_column_story.append(Paragraph(line, styles['NormalIndented'])) # Or another style


            if i < len(experiences) - 1: # Add space after each experience except the last one
                 left_column_story.append(Spacer(1, 0.1*inch))


    # --- Education (Left Column) ---
    education_entries = data.get('education_entries', [])
    if education_entries:
        left_column_story.append(Paragraph("EDUCATION", styles['SectionTitle']))
        left_column_story.append(HRFlowable(width="100%", thickness=1, color=color_line, spaceBefore=0, spaceAfter=0.1*inch))
        for i, edu in enumerate(education_entries):
            if edu.get('degree'):
                left_column_story.append(Paragraph(edu['degree'], styles['EducationDegree']))

            institution_date_parts = []
            if edu.get('institution'): institution_date_parts.append(f"<font color='{color_primary}'>{edu['institution']}</font>")
            if edu.get('edu_dates'): institution_date_parts.append(f"🗓️ {edu['edu_dates']}")
            if edu.get('edu_location'): institution_date_parts.append(f"📍 {edu['edu_location']}")

            if institution_date_parts:
                 left_column_story.append(Paragraph(" ".join(institution_date_parts), styles['InstitutionDate']))

            if edu.get('edu_details'):
                left_column_story.append(Paragraph(edu['edu_details'], styles['EducationDetails']))

            if i < len(education_entries) - 1: # Add space after each education entry except the last one
                left_column_story.append(Spacer(1, 0.1*inch))


    # --- Languages (Left Column) ---
    languages = data.get('languages', [])
    if languages:
        left_column_story.append(Paragraph("LANGUAGES", styles['SectionTitle']))
        left_column_story.append(HRFlowable(width="100%", thickness=1, color=color_line, spaceBefore=0, spaceAfter=0.1*inch))

        # Languages section layout (Name SkillLevel)
        # This can be done with a simple table or just joined text
        language_flowables = []
        for i, lang in enumerate(languages):
            lang_text = f"{lang.get('name', 'Language')} {lang.get('level_dots', '•••••')}" # Use dots or level text
            language_flowables.append(Paragraph(lang_text, styles['Language']))
            if i < len(languages) -1:
                 language_flowables.append(Spacer(1, 0.05*inch)) # Small space between languages

        left_column_story.extend(language_flowables)


    # Content that should flow into the RIGHT column second
    right_column_story = []

    # --- Summary (Right Column) ---
    if data.get('summary'):
        right_column_story.append(Paragraph("SUMMARY", styles['SectionTitle']))
        right_column_story.append(HRFlowable(width="100%", thickness=1, color=color_line, spaceBefore=0, spaceAfter=0.1*inch))
        right_column_story.append(Paragraph(data['summary'], styles['SummaryText']))


    # --- Key Achievements (Right Column) ---
    achievements = data.get('achievements', [])
    if achievements:
        right_column_story.append(Paragraph("KEY ACHIEVEMENTS", styles['SectionTitle']))
        right_column_story.append(HRFlowable(width="100%", thickness=1, color=color_line, spaceBefore=0, spaceAfter=0.1*inch))
        for i, ach in enumerate(achievements):
            # Icon is challenging - using star character as placeholder
            icon_char = ach.get('icon', '★') # Use star or get from data
            if ach.get('title'):
                 # Add icon and title in the same paragraph
                 right_column_story.append(Paragraph(f"<font color='{color_primary}'>{icon_char}</font> <b>{ach['title']}</b>", styles['KeyAchievementTitle']))
            if ach.get('description'):
                 right_column_story.append(Paragraph(ach['description'], styles['KeyAchievementDescription']))

            # No space after the last achievement description due to KeyAchievementDescription spaceAfter

    # --- Skills (Right Column) ---
    skills = data.get('skills', [])
    if skills:
        right_column_story.append(Paragraph("SKILLS", styles['SectionTitle']))
        right_column_story.append(HRFlowable(width="100%", thickness=1, color=color_line, spaceBefore=0, spaceAfter=0.1*inch))

        # Approximating the skills layout. Using a table where each cell contains a skill Paragraph.
        # This makes the skills flow horizontally then wrap. The 'pill' look is *not* achieved this way.
        # To get the pill look would require drawing shapes or custom flowables.
        # Simple comma-separated list:
        # skills_text = ", ".join(skills)
        # right_column_story.append(Paragraph(skills_text, styles['Normal']))

        # Using a table for skills to make them wrap somewhat like the image layout
        skill_table_data = []
        row = []
        # Estimate how many skills fit per row based on an average skill width
        # This is heuristic; precise wrapping depends on font and text.
        # A better way might be to pre-calculate paragraph widths.
        # Let's just dump all skills into a single row initially, ReportLab will handle cell wrapping.
        # Each skill gets its own cell.
        for skill in skills:
             # Put each skill in its own cell with basic styling (not pill)
             # To get the pill look, you'd need to draw the background/border *in* the cell or use a custom Flowable.
             row.append(Paragraph(skill, styles['Normal'])) # Using Normal style for simplicity

        if row:
             skill_table_data.append(row)

        if skill_table_data:
             # Use dynamic column widths for the table, allowing cells to be sized by content
             # colWidths can be None or a list of None to auto-size
             skill_table = Table(skill_table_data, style=[('VALIGN', (0,0), (-1,-1), 'TOP')]) # , ('GRID', (0,0), (-1,-1), 0.5, gray)])
             right_column_story.append(skill_table)
             right_column_story.append(Spacer(1, 0.1*inch)) # Space after skills table


    # --- Certification (Right Column) ---
    certifications = data.get('certifications', [])
    if certifications:
        right_column_story.append(Paragraph("CERTIFICATION", styles['SectionTitle']))
        right_column_story.append(HRFlowable(width="100%", thickness=1, color=color_line, spaceBefore=0, spaceAfter=0.1*inch))
        for i, cert in enumerate(certifications):
            if cert.get('name'):
                # Assuming certificate name might be a link or distinct - use color_primary
                 right_column_story.append(Paragraph(f"<font color='{color_primary}'>{cert['name']}</font>", styles['JobTitle'])) # Using JobTitle style for name
            if cert.get('details'):
                 right_column_story.append(Paragraph(cert['details'], styles['EducationDetails'])) # Using EducationDetails style for details
            if i < len(certifications) -1:
                 right_column_story.append(Spacer(1, 0.1*inch))


    # --- Combine Left and Right Column Content ---
    # ReportLab's flowable engine handles flowing these sequentially into the defined frames.
    # Add the left column content first, then the right.
    story.extend(left_column_story)
    story.extend(right_column_story)


    # --- Footer ---
    def footer_on_page(canvas, doc):
        canvas.saveState()
        # Draw the horizontal line just above the bottom margin
        canvas.setStrokeColor(color_line)
        canvas.setLineWidth(1)
        line_y = doc.bottomMargin - 0.1*inch # Position the line slightly above the margin bottom
        canvas.line(doc.leftMargin, line_y, letter[0] - doc.rightMargin, line_y)

        # Footer text
        footer_text = data.get('footer_link', 'www.enhancv.com') # Example footer text
        footer_power = "Powered by"
        # Assuming a logo file is available for 'Enhancv'
        logo_path = data.get('power_logo_path') # Path to the 'Enhancv' logo image

        # Position footer text (left aligned) and Powered By + Logo (right aligned)
        text_x = doc.leftMargin
        text_y = doc.bottomMargin - 0.3*inch # Position text below the line

        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(gray)

        # Draw the left footer text
        canvas.drawString(text_x, text_y, footer_text)

        # Draw "Powered by" text
        power_text_width = canvas.stringWidth(footer_power, 'Helvetica', 8)
        power_x = letter[0] - doc.rightMargin - power_text_width
        canvas.drawString(power_x, text_y, footer_power)

        # Add logo next to "Powered by"
        if logo_path:
            try:
                logo_img = ImageReader(logo_path)
                logo_height = 0.15 * inch # Set a fixed small height for the logo
                logo_width = logo_height * logo_img.getSize()[0] / logo_img.getSize()[1] # Maintain aspect ratio
                logo_x = power_x + power_text_width + 0.05*inch # Position logo after text with a gap
                logo_y = text_y # Align bottom of logo with text baseline (approx)
                canvas.drawImage(logo_img, logo_x, logo_y, width=logo_width, height=logo_height, mask='auto')

            except Exception as e:
                print(f"Could not load footer logo {logo_path}: {e}")


        canvas.restoreState()

    # Build the document, applying the footer to all pages
    doc.build(story, onFirstPage=footer_on_page, onLaterPages=footer_on_page)

    buffer.seek(0)
    return buffer

# --- Example Usage ---
if __name__ == '__main__':
    # Sample data mimicking the structure needed by the function
    example_data = {
        'full_name': 'ELLEN JOHNSON',
        'headline': 'Digital Marketing Manager | Growth Hacking | Data Analysis',
        'email_domain': 'enhancv.com', # Just the domain part for the contact line
        'linkedin': 'ellen-johnson',
        'location': 'San Francisco, California',
        'profile_image_path': 'ellen_johnson_profile.jpg', # Replace with actual path to an image file
        'summary': 'Motivated Digital Marketing Manager with over 3 years of experience in driving user acquisition and growth through strategic paid campaigns. Expert in data analysis, creative optimization, and cross-functional collaboration to achieve business objectives. Proven track record of scaling campaigns and enhancing ROI.',
        'achievements': [
            {'icon': '★', 'title': '45% User Acquisition Increase', 'description': 'Spearheaded digital marketing initiatives at Tech Innovate that led to a 45% increase in user acquisition.'},
            {'icon': '✏️', 'title': '30% ROAS Improvement', 'description': 'Optimized ad spend across digital platforms at Tech Innovate, resulting in a 30% improvement in ROAS.'},
            {'icon': '⚙️', 'title': 'Market Share Expansion', 'description': 'Identified and captured a new user segment, contributing to a 35% increase in market share.'},
            {'icon': '❤️', 'title': 'Conversion Rate Optimization', 'description': 'Implemented a successful landing page optimization strategy, lifting conversion rates by 18%.'},
        ],
        'skills': ['Data Analysis', 'Paid Acquisition', 'Retargeting', 'ROAS Optimization', 'Cross-Functional Collaboration', 'Google Analytics', 'Looker', 'Appsflyer', 'Meta Advertising', 'Google Ads', 'TikTok Ads', 'Snapchat Ads', 'SQL'],
        'experiences': [
            {
                'title': 'Senior Digital Marketing Specialist',
                'company': 'Tech Innovate',
                'dates': '01/2022 - Present',
                'location': 'San Francisco, CA',
                'description': '- Led the development and execution of comprehensive digital marketing campaigns across Meta, Google, and TikTok, increasing user acquisition by 45% within 12 months.\n- Managed a $500K quarterly budget for paid acquisition channels, optimizing spend for a 30% improvement in ROAS.\n- Implemented advanced targeting and retargeting strategies that reduced CPA by 20%, while increasing conversion rates by 15%.\n- Conducted A/B testing on over 100 ad creatives, identifying top performers that led to a 25% increase in engagement.\n- Collaborated with cross-functional teams to align marketing efforts with product launches, resulting in a 40% increase in product adoption.\n- Analyzed campaign data to provide actionable insights, leading to a strategic pivot that captured a new user segment and contributed to a 35% increase in market share.'
            },
            {
                'title': 'Digital Marketing Manager',
                'company': 'MarketGuru',
                'dates': '06/2019 - 12/2021',
                'location': 'San Francisco, CA',
                'description': '- Managed and scaled paid search and social campaigns across Snapchat and Apple Search Ads, achieving a 50% increase in leads.\n- Designed and executed a landing page optimization strategy that lifted conversion rates by 18%.\n- Utilized Looker and Google Analytics to monitor campaign performance, driving a 10% decrease in bounce rates.\n- Orchestrated the creative testing process, enhancing ad performance and contributing to a 22% increase in CTR.\n- Collaborated with engineering to integrate new tracking systems, improving data accuracy and campaign efficiency.'
            },
            {
                'title': 'Performance Marketing Analyst',
                'company': 'AdVantage Media',
                'dates': '03/2017 - 05/2019',
                'location': 'San Francisco, CA',
                'description': '- Analyzed performance data across multiple digital channels, identifying trends that informed strategic decisions.\n- Supported the execution of campaigns that resulted in a 15% increase in user engagement.\n- Developed and maintained reporting dashboards for real-time performance tracking, enhancing team responsiveness.\n- Assisted in managing a portfolio of digital ads, optimizing for a 10% improvement in ad efficiency.'
            },
        ],
        'education_entries': [
            {
                'degree': 'Master of Science in Marketing Analytics',
                'institution': 'University of California, Berkeley',
                'edu_dates': '01/2015 - 01/2017',
                'edu_location': 'Berkeley, CA',
                'edu_details': 'Specialization in Data-Driven Marketing.'
            },
            {
                'degree': 'Bachelor of Science in Business Administration',
                'institution': 'San Francisco State University',
                'edu_dates': '01/2011 - 01/2015',
                'edu_location': 'San Francisco, CA',
                'edu_details': 'Emphasis on Marketing.'
            }
        ],
        'languages': [
            {'name': 'English', 'level_dots': '••••• Native'}, # Combine name and level/dots
            {'name': 'Spanish', 'level_dots': '••• Advanced'}
        ],
        'certifications': [
            {'name': 'Advanced Google Analytics', 'details': 'Focused on mastering Google Analytics for deep insights into user behavior, provided by Google.'},
            {'name': 'Effective Creative Testing', 'details': 'Specialized in evaluating ad creative performance to maximize engagement, offered by Coursera.'}
        ],
        'footer_link': 'www.enhancv.com',
        'power_logo_path': 'enhancv_logo.png' # Replace with path to Enhancv logo image file
    }

    # Create dummy image files if they don't exist for testing
    # You would replace these with your actual images
    try:
        from PIL import Image as PILImage
        # Profile Image
        img = PILImage.new('RGB', (100, 100), color = 'red')
        img.save(example_data['profile_image_path'])
        # Logo Image
        logo = PILImage.new('RGB', (100, 30), color = 'blue')
        logo.save(example_data['power_logo_path'])
        print(f"Created dummy images: {example_data['profile_image_path']}, {example_data['power_logo_path']}")
    except ImportError:
        print("Pillow not installed. Cannot create dummy images. Image placeholders might be missing.")
        example_data['profile_image_path'] = None
        example_data['power_logo_path'] = None
    except Exception as e:
        print(f"Could not create dummy images: {e}")
        example_data['profile_image_path'] = None
        example_data['power_logo_path'] = None


    pdf_buffer = generate_resume_pdf(example_data, profile_image_path=example_data['profile_image_path'])

    with open('ellen_johnson_resume.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())

    print("PDF generated: ellen_johnson_resume.pdf")