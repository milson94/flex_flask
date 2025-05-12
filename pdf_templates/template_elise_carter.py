# pdf_templates/template_elise_carter.py
import io
import os
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image, FrameBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, grey, lightgrey
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.graphics.shapes import Circle # For potential advanced drawing

# --- Color Palette (approximations) ---
COLOR_TEXT_MAIN = HexColor('#333333')
COLOR_TEXT_MUTED = HexColor('#666666')
COLOR_TEXT_HEADER = HexColor('#2c3e50')
COLOR_ACCENT_GREEN = HexColor('#16a085') # A teal/green
COLOR_BACKGROUND_LIGHT = HexColor('#f8f9fa') # Very light page background if desired

class EliseCarterDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        self.profile_image_path = kwargs.pop('profile_image_path', None)
        BaseDocTemplate.__init__(self, filename, **kwargs)

        # Define Frames: Main content slightly wider, right sidebar narrower
        main_col_width = self.width * 0.62 # Main content
        sidebar_width = self.width * 0.33 # Sidebar
        gap = self.width - main_col_width - sidebar_width # Calculate gap based on remaining width

        # Order of frames matters for FrameBreak flow
        # For Elise Carter, content flows left (main) then right (sidebar)
        frame_main = Frame(self.leftMargin, self.bottomMargin,
                           main_col_width, self.height, id='col_main', showBoundary=0)
        frame_sidebar = Frame(self.leftMargin + main_col_width + gap, self.bottomMargin,
                              sidebar_width, self.height, id='col_sidebar', showBoundary=0)
        
        main_page = PageTemplate(id='MainPageElise', frames=[frame_main, frame_sidebar], onPage=self.draw_header_and_profile)
        self.addPageTemplates([main_page])

    def draw_header_and_profile(self, canvas, doc):
        canvas.saveState()
        
        # Profile Image (Top Right)
        if self.profile_image_path and os.path.exists(self.profile_image_path):
            try:
                img_size = 1.3 * inch
                img_x = doc.width + doc.leftMargin - img_size - (0.1 * inch) # Position from right edge
                img_y = doc.height + doc.topMargin - img_size - (0.2 * inch) # Position from top edge
                
                # Circular clipping (simple version, more advanced would use canvas.clipPath)
                # For a true circle, drawImage doesn't have a direct mask for circle.
                # We can draw a white circle behind a square image to fake it, or use canvas.clipPath.
                # Let's try canvas.clipPath for better quality.
                path = canvas.beginPath()
                path.circle(img_x + img_size/2, img_y + img_size/2, img_size/2)
                canvas.clipPath(path, stroke=0, fill=0)
                canvas.drawImage(self.profile_image_path, img_x, img_y, width=img_size, height=img_size, mask='auto')
                canvas.setFillColorRGB(1,1,1) # Reset clipping path by drawing a full page rect or similar
            except Exception as e:
                print(f"Error drawing Elise Carter profile image: {e}")
        canvas.restoreState()


def generate_pdf(data):
    buffer = io.BytesIO()
    
    doc = EliseCarterDocTemplate(buffer, pagesize=letter,
                                 leftMargin=0.75*inch, rightMargin=0.5*inch, # Asymmetric margins
                                 topMargin=0.75*inch, bottomMargin=0.75*inch,
                                 profile_image_path=data.get('profile_image_path'))

    styles = getSampleStyleSheet()
    # --- Define Styles ---
    styles.add(ParagraphStyle(name='FullName', fontName='Helvetica-Bold', fontSize=24, textColor=COLOR_TEXT_HEADER, spaceBefore=0, leading=28, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='JobTitleHeader', fontName='Helvetica', fontSize=11, textColor=COLOR_TEXT_MAIN, spaceAfter=3, leading=14))
    styles.add(ParagraphStyle(name='ContactInfo', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT_MUTED, leading=12, spaceAfter=0.1*inch))

    styles.add(ParagraphStyle(name='MainSectionTitle', fontName='Helvetica-Bold', fontSize=10, textColor=COLOR_TEXT_HEADER, spaceBefore=0.15*inch, spaceAfter=0.05*inch, leading=12, alignment=TA_LEFT, textTransform='uppercase'))
    styles.add(ParagraphStyle(name='MainBodyText', fontName='Helvetica', fontSize=9.5, textColor=COLOR_TEXT_MAIN, leading=13, spaceAfter=3, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='ExpJobTitle', fontName='Helvetica-Bold', fontSize=11, textColor=COLOR_TEXT_MAIN, leading=14))
    styles.add(ParagraphStyle(name='ExpCompanyDate', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT_MUTED, leading=12, spaceAfter=3))
    styles.add(ParagraphStyle(name='ExpBullet', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT_MAIN, leading=12, leftIndent=15, firstLineIndent=0, spaceBefore=1, bulletIndent=5))
    styles.add(ParagraphStyle(name='EduDegree', fontName='Helvetica-Bold', fontSize=10, textColor=COLOR_TEXT_MAIN, leading=13))
    styles.add(ParagraphStyle(name='EduInstitutionDate', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT_MUTED, leading=12))

    styles.add(ParagraphStyle(name='SidebarSectionTitle', fontName='Helvetica-Bold', fontSize=9, textColor=COLOR_ACCENT_GREEN, spaceBefore=0.2*inch, spaceAfter=0.08*inch, leading=11, textTransform='uppercase'))
    styles.add(ParagraphStyle(name='SidebarItemTitle', fontName='Helvetica-Bold', fontSize=9, textColor=COLOR_TEXT_MAIN, leading=12, spaceAfter=1))
    styles.add(ParagraphStyle(name='SidebarItemDesc', fontName='Helvetica', fontSize=8.5, textColor=COLOR_TEXT_MUTED, leading=11, spaceAfter=0.1*inch))
    styles.add(ParagraphStyle(name='SidebarSkill', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT_MAIN, leading=12, spaceAfter=2))


    # --- Story for Main Column (Left) ---
    story_main = []
    
    # Header section (Name, Title, Contact) - This needs to be at the very top of the flow
    if data.get('full_name'):
        story_main.append(Paragraph(data['full_name'], styles['FullName']))
    if data.get('title_subtitle'):
        story_main.append(Paragraph(data['title_subtitle'], styles['JobTitleHeader']))
    
    contact_items = []
    if data.get('email'): contact_items.append(f"📧 {data['email']}") # Using emoji, ensure font support
    if data.get('linkedin'): contact_items.append(f"🔗 {data['linkedin']}")
    if data.get('location'): contact_items.append(f"📍 {data['location']}")
    if contact_items:
        story_main.append(Paragraph(" | ".join(contact_items), styles['ContactInfo']))
    story_main.append(Spacer(1, 0.2*inch))


    # SUMMARY
    story_main.append(Paragraph('Summary', styles['MainSectionTitle']))
    if data.get('summary'):
        story_main.append(Paragraph(data['summary'], styles['MainBodyText']))
    story_main.append(Spacer(1, 0.15*inch))

    # EXPERIENCE
    story_main.append(Paragraph('Experience', styles['MainSectionTitle']))
    for exp in data.get('experiences', []):
        story_main.append(Paragraph(exp['title'], styles['ExpJobTitle']))
        date_str = f"{exp.get('start_date','')} - {exp.get('end_date','') if not exp.get('is_present') else 'Present'}"
        story_main.append(Paragraph(f"{exp['company']} | {date_str} | {exp.get('location','')}", styles['ExpCompanyDate']))
        
        description_text = exp.get('description', '')
        if description_text:
            points = [p.strip() for p in description_text.split('\n') if p.strip()]
            for point in points:
                story_main.append(Paragraph(point, styles['ExpBullet'], bulletText='-')) # Using '-' as bullet
        story_main.append(Spacer(1, 0.1*inch))
    story_main.append(Spacer(1, 0.15*inch))

    # EDUCATION
    story_main.append(Paragraph('Education', styles['MainSectionTitle']))
    for edu in data.get('education_entries', []):
        story_main.append(Paragraph(edu['degree'], styles['EduDegree']))
        date_str = f"{edu.get('start_date','')} - {edu.get('end_date','') if not edu.get('is_present') else 'Present'}"
        story_main.append(Paragraph(f"{edu['institution']} | {date_str} | {edu.get('edu_location','')}", styles['EduInstitutionDate']))
        if edu.get('edu_details'):
            story_main.append(Paragraph(edu['edu_details'], styles['MainBodyText']))
        story_main.append(Spacer(1, 0.1*inch))

    # --- Story for Sidebar (Right) ---
    story_sidebar = []
    # Add a spacer at the top of the sidebar to clear the profile image area if it overlaps,
    # or adjust frame starting Y position. For now, let's assume the image is drawn by canvas and flow starts below.
    story_sidebar.append(Spacer(1, 0.5 * inch)) # Adjust if profile image overlaps this frame

    # STRENGTHS
    if data.get('strengths'):
        story_sidebar.append(Paragraph('Strengths', styles['SidebarSectionTitle']))
        for item in data['strengths']:
            story_sidebar.append(Paragraph(item['title'], styles['SidebarItemTitle']))
            story_sidebar.append(Paragraph(item['description'], styles['SidebarItemDesc']))
        story_sidebar.append(Spacer(1, 0.15*inch))

    # SKILLS
    if data.get('skills_list_detailed'):
        story_sidebar.append(Paragraph('Skills', styles['SidebarSectionTitle']))
        # Display skills perhaps in a flow, or simple list
        skills_text = ", ".join(data['skills_list_detailed'])
        story_sidebar.append(Paragraph(skills_text, styles['SidebarSkill'])) # Simple comma list for now
        story_sidebar.append(Spacer(1, 0.15*inch))

    # PROJECTS
    if data.get('projects'):
        story_sidebar.append(Paragraph('Projects', styles['SidebarSectionTitle']))
        for proj in data['projects']:
            story_sidebar.append(Paragraph(proj['title'], styles['SidebarItemTitle']))
            if proj.get('subtitle'):
                 story_sidebar.append(Paragraph(proj['subtitle'], styles['SidebarItemDesc'])) # Style as desc
            story_sidebar.append(Paragraph(proj['description'], styles['SidebarItemDesc']))
        story_sidebar.append(Spacer(1, 0.15*inch))

    # HOW I SPLIT MY TIME (Simplified List)
    if data.get('how_i_split_my_time'):
        story_sidebar.append(Paragraph('How I Split My Time', styles['SidebarSectionTitle']))
        for item in data['how_i_split_my_time']:
            story_sidebar.append(Paragraph(f"{item['label']}: {item['activity']}", styles['SidebarItemDesc']))

    # --- Combine Stories for Build ---
    full_story = []
    full_story.extend(story_main)
    full_story.append(FrameBreak()) # Move to the sidebar frame
    full_story.extend(story_sidebar)

    doc.build(full_story)
    buffer.seek(0)
    return buffer