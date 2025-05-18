# pdf_templates/modern_template.py
import io
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image, Table, TableStyle, FrameBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, white, transparent
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4 # <-- USE A4
from reportlab.graphics.shapes import Circle
# from reportlab.lib.utils import ImageReader # Not strictly needed if using canvas.drawImage
import os
from datetime import datetime

# --- Color Palette ---
COLOR_PRIMARY_GREEN = HexColor('#36A083')
COLOR_SECONDARY_GREEN = HexColor('#A3D9C8')
COLOR_PROFILE_BG_LIGHT = HexColor('#D6F0E9')
COLOR_PROFILE_BG_DOT = HexColor('#6ABE9C')
COLOR_TEXT_DARK = HexColor('#4A5568')
COLOR_TEXT_MUTED = HexColor('#718096')
COLOR_TEXT_BLACK = HexColor('#1A202C')
COLOR_LINK = HexColor('#2B6CB0')

# --- Default Order Constant (can be imported or redefined) ---
# This should ideally match the one in app.py
DEFAULT_SECTION_ORDER = ['summary', 'experience', 'education', 'achievements', 'courses']

# --- Custom Document Template ---
class ModernDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        self.profile_image_path = kwargs.pop('profile_image_path', None)
        # Store other data if needed for page drawing, like full_name if used in header/footer
        # self.full_name = kwargs.pop('full_name', 'Your Name')

        # Set A4 page size directly here
        kwargs['pagesize'] = A4
        BaseDocTemplate.__init__(self, filename, **kwargs)

        # Define frames based on A4 dimensions (adjust widths/gaps if needed)
        # A4 dimensions: 8.27 x 11.69 inches
        # Using page dimensions after margins
        content_width = self.width # width available after margins
        content_height = self.height # height available after margins

        left_col_width = content_width * 0.32 # Approx 32% for left column
        gap = 0.25 * inch
        right_col_width = content_width - left_col_width - gap

        # Ensure frames fit within the page margins
        frame_left = Frame(self.leftMargin, self.bottomMargin,
                           left_col_width, content_height, id='col_left', showBoundary=0)
        frame_right = Frame(self.leftMargin + left_col_width + gap, self.bottomMargin,
                            right_col_width, content_height, id='col_right', showBoundary=0)

        main_page_template = PageTemplate(id='MainPage', frames=[frame_left, frame_right], onPage=self.draw_page_background)
        self.addPageTemplates([main_page_template])

    def draw_page_background(self, canvas, doc):
        """Draws the static background elements like colored areas and profile pic circle"""
        canvas.saveState()
        # --- Profile Area Background ---
        profile_area_height = 3.5 * inch # Height of the light green area
        # Position from top-left corner of the *page* (not margin)
        profile_bg_y = doc.pagesize[1] - doc.topMargin - profile_area_height # Top edge Y coord
        profile_bg_width = doc.leftMargin + (doc.width * 0.32) # Width extending slightly past left margin if needed

        canvas.setFillColor(COLOR_PROFILE_BG_LIGHT)
        # Draw rect slightly outside margin for full bleed effect if desired
        canvas.rect(0, profile_bg_y, profile_bg_width, profile_area_height, stroke=0, fill=1)

        # --- Decorative Dot ---
        img_center_x = doc.leftMargin + (doc.width * 0.32) / 2 # Center of left column frame
        img_center_y = doc.pagesize[1] - doc.topMargin - (profile_area_height / 2) - 0.1*inch # Vertical center adjusted slightly

        canvas.setFillColor(COLOR_PROFILE_BG_DOT)
        canvas.circle(img_center_x - 0.8*inch, img_center_y + 0.7*inch, 0.4*inch, stroke=0, fill=1) # Example position

        # --- Profile Image (Circular) ---
        if self.profile_image_path and os.path.exists(self.profile_image_path):
            try:
                img_size = 1.8 * inch # Diameter of the image
                img_radius = img_size / 2
                img_draw_x = img_center_x - img_radius
                img_draw_y = img_center_y - img_radius

                # Create a circular clipping path centered correctly
                path = canvas.beginPath()
                path.circle(img_center_x, img_center_y, img_radius)
                canvas.clipPath(path, stroke=0, fill=0)

                # Draw the image within the clipped circle
                canvas.drawImage(self.profile_image_path, img_draw_x, img_draw_y,
                                 width=img_size, height=img_size, mask='auto')
                # IMPORTANT: Must restore state after clipping if other drawing happens later
                # canvas.restoreState() # Don't restore here, restore outside the if/else

            except Exception as e:
                print(f"Error drawing profile image: {e}")
                # Maybe draw a placeholder circle?
                canvas.setFillColor(COLOR_PROFILE_BG_DOT) # Fallback color
                canvas.circle(img_center_x, img_center_y, img_radius, stroke=1, fill=1)

        # No else needed, if no image, nothing is drawn in that spot.

        canvas.restoreState() # Restore state after profile area drawing

        # --- Name Background (Right Column) ---
        canvas.saveState()
        name_bg_height = 1.2 * inch
        # Y position relative to top margin
        name_bg_y = doc.pagesize[1] - doc.topMargin - name_bg_height - 0.1*inch # Adjust vertical position as needed
        right_col_start_x = doc.leftMargin + doc.width * 0.32 + 0.25 * inch # Start of right column frame area
        right_col_actual_width = doc.width - (doc.width * 0.32) - (0.25 * inch) # Actual width of right frame

        canvas.setFillColor(COLOR_SECONDARY_GREEN)
        canvas.rect(right_col_start_x, name_bg_y,
                    right_col_actual_width, name_bg_height, stroke=0, fill=1)
        canvas.restoreState()


# --- Helper Functions ---
def create_section_header(icon_char, title_text, style, icon_color=COLOR_PRIMARY_GREEN):
    # Using a Paragraph with HTML-like font tag for basic icon inclusion.
    # For complex icons/alignment, consider Table or custom Flowable.
    # Ensure the font used supports the icon_char (e.g., use ZapfDingbats or an icon font).
    # Using Helvetica might not render all icons.
    # For reliability, using basic Unicode symbols or bullet points is safer.
    icon_font_name = 'Helvetica' # Or 'ZapfDingbats' for some symbols
    return Paragraph(f'<font name="{icon_font_name}" color="{icon_color.hexval()}">{icon_char}</font>  {title_text.upper()}', style)


def format_month_year(date_str_yyyy_mm):
    """Formats YYYY-MM to MM/YYYY. Returns original on error."""
    if not date_str_yyyy_mm: return ""
    try:
        dt_obj = datetime.strptime(date_str_yyyy_mm, "%Y-%m")
        return dt_obj.strftime("%m/%Y") # Output: MM/YYYY
    except ValueError:
        return date_str_yyyy_mm # Return original if parsing fails

# --- PDF Generation Function ---
def generate_pdf(data):
    buffer = io.BytesIO()

    margin_val = 0.6 * inch # Re-evaluate margins visually for A4
    doc = ModernDocTemplate(buffer,
                            # pagesize=A4 is now set in ModernDocTemplate class
                            leftMargin=margin_val, rightMargin=margin_val,
                            topMargin=margin_val, bottomMargin=margin_val,
                            profile_image_path=data.get('profile_image_path'),
                            title=f"Resume - {data.get('full_name', 'Applicant')}") # Set PDF title metadata

    styles = getSampleStyleSheet()
    # --- Define Styles (Adjust font sizes/leading slightly if needed for A4) ---
    styles.add(ParagraphStyle(name='FullName', fontName='Helvetica-Bold', fontSize=26, textColor=COLOR_TEXT_BLACK, spaceBefore=0.15*inch, leading=30, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='JobTitle', fontName='Helvetica', fontSize=10.5, textColor=white, leading=13, spaceBefore=0, spaceAfter=0.1*inch, alignment=TA_LEFT))

    styles.add(ParagraphStyle(name='LeftColH1', fontName='Helvetica-Bold', fontSize=9.5, textColor=COLOR_PRIMARY_GREEN, spaceBefore=0.25*inch, spaceAfter=0.1*inch, leading=11))
    styles.add(ParagraphStyle(name='LeftColText', fontName='Helvetica', fontSize=8, textColor=COLOR_TEXT_DARK, leading=10, spaceAfter=2))
    # styles.add(ParagraphStyle(name='LeftColLink', parent=styles['LeftColText'], textColor=COLOR_LINK)) # Example if needed
    styles.add(ParagraphStyle(name='LeftColItemTitle', fontName='Helvetica-Bold', fontSize=8.5, textColor=COLOR_TEXT_DARK, leading=10, spaceBefore=4, spaceAfter=1))
    styles.add(ParagraphStyle(name='LeftColItemDesc', parent=styles['LeftColText'], fontSize=7.5, leading=9, leftIndent=0))

    styles.add(ParagraphStyle(name='RightColH1', fontName='Helvetica-Bold', fontSize=10.5, textColor=COLOR_PRIMARY_GREEN, spaceBefore=0.15*inch, spaceAfter=0.05*inch, leading=13))
    styles.add(ParagraphStyle(name='RightColBody', fontName='Helvetica', fontSize=8.5, textColor=COLOR_TEXT_DARK, leading=12, spaceAfter=0.1*inch, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='ExpJobTitle', fontName='Helvetica-Bold', fontSize=9.5, textColor=COLOR_TEXT_BLACK, leading=12))
    styles.add(ParagraphStyle(name='ExpCompanyLocation', fontName='Helvetica', fontSize=8.5, textColor=COLOR_TEXT_MUTED, leading=10, spaceBefore=1)) # Added spaceBefore
    styles.add(ParagraphStyle(name='ExpDates', fontName='Helvetica', fontSize=8.5, textColor=COLOR_TEXT_MUTED, leading=10, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='ExpBullet', parent=styles['RightColBody'], bulletIndent=10, leftIndent=15, firstLineIndent=0, spaceBefore=1, fontSize=8, leading=10.5))

    styles.add(ParagraphStyle(name='EduDegree', fontName='Helvetica-Bold', fontSize=9.5, textColor=COLOR_TEXT_BLACK, leading=12))
    styles.add(ParagraphStyle(name='EduInstitution', fontName='Helvetica', fontSize=8.5, textColor=COLOR_TEXT_DARK, leading=10, spaceBefore=1)) # Added spaceBefore
    styles.add(ParagraphStyle(name='EduLocationDates', fontName='Helvetica', fontSize=8.5, textColor=COLOR_TEXT_MUTED, leading=10, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='EduDetails', parent=styles['RightColBody'], fontSize=8, leading=10.5, spaceBefore=2)) # Style for Edu details


    # --- Section Building Functions (Encapsulated Logic) ---
    # These functions return a list of flowables for a given section

    def build_contact_story(data, styles):
        """Builds the 'Contacts' section (typically fixed in left column)"""
        story = []
        # Using simple unicode symbols as icons for better font compatibility
        story.append(create_section_header('☎', 'CONTACTS', styles['LeftColH1'])) # Phone icon
        if data.get('phone'): story.append(Paragraph(data['phone'], styles['LeftColText']))
        if data.get('email'): story.append(Paragraph(data['email'], styles['LeftColText']))
        if data.get('linkedin'):
             # Attempt basic link creation (PDF viewers may auto-link)
             link = data['linkedin']
             if not link.startswith(('http://', 'https://')):
                 link = 'https://' + link
             story.append(Paragraph(f'<link href="{link}">{data["linkedin"]}</link>', styles['LeftColText']))
        if data.get('location'): story.append(Paragraph(data['location'], styles['LeftColText']))
        story.append(Spacer(1, 0.2*inch))
        return story

    def build_achievements_story(data, styles):
        """Builds the 'Key Achievements' section"""
        story = []
        if data.get('key_achievements'):
            story.append(create_section_header('★', 'KEY ACHIEVEMENTS', styles['LeftColH1'])) # Star icon
            for ach in data['key_achievements']:
                story.append(Paragraph(ach['title'], styles['LeftColItemTitle']))
                story.append(Paragraph(ach['description'], styles['LeftColItemDesc']))
                story.append(Spacer(1, 0.08*inch)) # Slightly more space between items
            story.append(Spacer(1, 0.2*inch))
        return story

    def build_courses_story(data, styles):
        """Builds the 'Courses' section"""
        story = []
        if data.get('courses'):
            story.append(create_section_header('📄', 'COURSES & CERTIFICATIONS', styles['LeftColH1'])) # Document icon
            for course in data['courses']:
                story.append(Paragraph(course['title'], styles['LeftColItemTitle']))
                story.append(Paragraph(course['description'], styles['LeftColItemDesc']))
                story.append(Spacer(1, 0.08*inch))
            story.append(Spacer(1, 0.2*inch))
        return story

    def build_summary_story(data, styles):
        """Builds the 'Summary' section"""
        story = []
        story.append(create_section_header('👤', 'SUMMARY', styles['RightColH1'])) # Person icon
        if data.get('summary'):
            story.append(Paragraph(data['summary'], styles['RightColBody']))
        story.append(Spacer(1, 0.2*inch))
        return story

    def build_experience_story(data, styles):
        """Builds the 'Experience' section"""
        story = []
        if data.get('experiences'):
            story.append(create_section_header('💼', 'EXPERIENCE', styles['RightColH1'])) # Briefcase icon
            for exp in data['experiences']:
                # Header Table (Title | Dates)
                start_date_f = format_month_year(exp.get('start_date'))
                end_date_f = format_month_year(exp.get('end_date')) if not exp.get('is_present') else 'Present'
                date_range = f"{start_date_f} - {end_date_f}" if start_date_f else end_date_f # Handle missing start date

                exp_header_data = [[
                    Paragraph(exp['title'], styles['ExpJobTitle']),
                    Paragraph(date_range, styles['ExpDates'])
                ]]
                exp_header_table = Table(exp_header_data, colWidths=['70%', '30%'], style=TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1), # Space below title/date row
                ]))
                story.append(exp_header_table)

                # Company & Location Line
                company_line = exp.get('company', '')
                if exp.get('location'): company_line += f" | {exp['location']}"
                if company_line: story.append(Paragraph(company_line, styles['ExpCompanyLocation']))

                # Description Bullet Points
                description_text = exp.get('description', '')
                if description_text:
                    # Split by newline, filter empty, remove leading hyphens/bullets
                    points = [p.strip().lstrip('-*• ') for p in description_text.split('\n') if p.strip()]
                    for point in points:
                        story.append(Paragraph(f"• {point}", styles['ExpBullet'])) # Use standard bullet
                story.append(Spacer(1, 0.15*inch)) # Space between experiences
            # story.append(Spacer(1, 0.1*inch)) # Optional spacer after the whole section
        return story

    def build_education_story(data, styles):
        """Builds the 'Education' section"""
        story = []
        if data.get('education_entries'):
            story.append(create_section_header('🎓', 'EDUCATION', styles['RightColH1'])) # Graduation cap icon
            for edu in data['education_entries']:
                 # Header Table (Degree | Dates)
                start_date_f = format_month_year(edu.get('start_date'))
                end_date_f = format_month_year(edu.get('end_date')) if not edu.get('is_present') else 'Present'
                date_range = f"{start_date_f} - {end_date_f}" if start_date_f else end_date_f

                edu_header_data = [[
                    Paragraph(edu['degree'], styles['EduDegree']),
                    Paragraph(date_range, styles['EduLocationDates'])
                ]]
                edu_header_table = Table(edu_header_data, colWidths=['70%', '30%'], style=TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ]))
                story.append(edu_header_table)

                # Institution & Location Line
                institution_line = edu.get('institution', '')
                if edu.get('edu_location'): institution_line += f" | {edu['edu_location']}"
                if institution_line: story.append(Paragraph(institution_line, styles['EduInstitution']))

                # Education Details
                if edu.get('edu_details'):
                    story.append(Paragraph(edu['edu_details'], styles['EduDetails'])) # Use specific style if needed
                story.append(Spacer(1, 0.15*inch)) # Space between education entries
        return story

    # --- Map Section Keys to Builder Functions ---
    # This mapping determines which function generates which part of the resume.
    # Some sections might belong logically to left or right columns in this template.
    section_builders = {
        'contact': build_contact_story,       # Left Column in this template
        'achievements': build_achievements_story, # Left Column in this template
        'courses': build_courses_story,         # Left Column in this template
        'summary': build_summary_story,         # Right Column
        'experience': build_experience_story,     # Right Column
        'education': build_education_story,       # Right Column
    }

    # --- Get Section Order ---
    # Retrieve the user-defined order from the data, fallback to default
    section_order = data.get('section_order', DEFAULT_SECTION_ORDER)
    print(f"Using section order: {section_order}") # Debugging output

    # --- Build Stories based on Order ---
    story_left = []
    story_right = []

    # Add fixed elements first (if any)
    story_left.append(Spacer(1, doc.pagesize[1] - doc.topMargin - (3.0 * inch))) # Approximate spacer to clear profile area - ADJUST MANUALLY

    # Add Name/Title Block to Right Column (fixed position)
    story_right.append(Spacer(1, 0.1*inch)) # Align with top of green name background
    if data.get('full_name'): story_right.append(Paragraph(data['full_name'], styles['FullName']))
    if data.get('title_subtitle'): story_right.append(Paragraph(data['title_subtitle'], styles['JobTitle']))
    story_right.append(Spacer(1, 0.35*inch)) # Space below name block

    # Iterate through the desired section order and build stories
    # This template design puts specific sections in specific columns.
    # A more flexible template might just append all ordered sections to one story.
    for section_key in section_order:
        builder = section_builders.get(section_key)
        if builder:
            # Determine which column this section belongs to in this template
            if section_key in ['contact', 'achievements', 'courses']:
                story_left.extend(builder(data, styles))
            elif section_key in ['summary', 'experience', 'education']:
                 story_right.extend(builder(data, styles))
            else:
                 # Handle unknown section key? Maybe log a warning.
                 print(f"Warning: Unknown section key '{section_key}' in section_order.")
                 # Optionally, append to a default column (e.g., right)
                 # story_right.extend(builder(data, styles))
        else:
             print(f"Warning: No builder found for section key '{section_key}'.")

    # --- Combine Left and Right Stories for the Page ---
    full_story = []
    full_story.extend(story_left)
    full_story.append(FrameBreak()) # IMPORTANT: Move to the next frame (right column)
    full_story.extend(story_right)

    # --- Build the PDF Document ---
    try:
        doc.build(full_story)
    except Exception as e:
        print(f"Error during doc.build: {e}")
        # Consider raising the exception or returning an error indicator
        raise # Re-raise the exception to be caught by Flask route

    buffer.seek(0)
    return buffer