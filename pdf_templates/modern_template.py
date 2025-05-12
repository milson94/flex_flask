# pdf_templates/modern_template.py
import io
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image, Table, TableStyle, FrameBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, white, transparent
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.graphics.shapes import Circle, Path # Make sure Path is actually used or remove
from reportlab.lib.utils import ImageReader # Make sure ImageReader is used or remove if using canvas.drawImage directly
import os # For checking image path
from datetime import datetime # For formatting dates

# --- Color Palette (approximations from image) ---
COLOR_PRIMARY_GREEN = HexColor('#36A083')
COLOR_SECONDARY_GREEN = HexColor('#A3D9C8')
COLOR_PROFILE_BG_LIGHT = HexColor('#D6F0E9')
COLOR_PROFILE_BG_DOT = HexColor('#6ABE9C')
COLOR_TEXT_DARK = HexColor('#4A5568')
COLOR_TEXT_MUTED = HexColor('#718096')
COLOR_TEXT_BLACK = HexColor('#1A202C')
COLOR_LINK = HexColor('#2B6CB0')

# --- Custom Document Template ---
class ModernDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        self.profile_image_path = kwargs.pop('profile_image_path', None)
        self.full_name = kwargs.pop('full_name', 'Your Name')
        
        BaseDocTemplate.__init__(self, filename, **kwargs)

        left_col_width = self.width * 0.32
        gap = 0.25 * inch
        right_col_width = self.width - left_col_width - gap

        frame_left = Frame(self.leftMargin, self.bottomMargin,
                           left_col_width, self.height, id='col_left', showBoundary=0)
        frame_right = Frame(self.leftMargin + left_col_width + gap, self.bottomMargin,
                            right_col_width, self.height, id='col_right', showBoundary=0)

        main_page_template = PageTemplate(id='MainPage', frames=[frame_left, frame_right], onPage=self.draw_page_background)
        self.addPageTemplates([main_page_template])

    def draw_page_background(self, canvas, doc):
        canvas.saveState()
        profile_area_height = 3.5 * inch
        canvas.setFillColor(COLOR_PROFILE_BG_LIGHT)
        canvas.rect(doc.leftMargin - 0.05*inch, doc.height + doc.topMargin - profile_area_height,
                    doc.width * 0.32 + 0.1*inch, profile_area_height, stroke=0, fill=1)

        img_center_x = doc.leftMargin + (doc.width * 0.32) / 2
        img_center_y = doc.height + doc.topMargin - (profile_area_height / 2) - 0.2*inch

        canvas.setFillColor(COLOR_PROFILE_BG_DOT)
        canvas.circle(img_center_x - 0.8*inch, img_center_y + 0.7*inch, 0.4*inch, stroke=0, fill=1)

        if self.profile_image_path and os.path.exists(self.profile_image_path):
            try:
                img_size = 1.8 * inch
                img_x = img_center_x - img_size / 2
                img_y = img_center_y - img_size / 2
                
                # Create a circular clipping path
                path = canvas.beginPath()
                path.circle(img_center_x, img_center_y + 0.05*inch, img_size / 2) # Center adjusted slightly for visual balance
                canvas.clipPath(path, stroke=0, fill=0)
                canvas.drawImage(self.profile_image_path, img_x, img_y, width=img_size, height=img_size, mask='auto')
                canvas.setFillColorRGB(1,1,1) # Reset fill color if needed after clipping
            except Exception as e:
                print(f"Error drawing profile image: {e}")
        
        canvas.restoreState()

        canvas.saveState()
        name_bg_height = 1.2 * inch
        name_bg_y = doc.height + doc.topMargin - name_bg_height - 0.1*inch
        right_col_start_x = doc.leftMargin + doc.width * 0.32 + 0.25 * inch
        canvas.setFillColor(COLOR_SECONDARY_GREEN)
        canvas.rect(right_col_start_x, name_bg_y,
                    doc.width * 0.67 - 0.25 * inch, name_bg_height, stroke=0, fill=1)
        canvas.restoreState()

def create_section_header(icon_char, title_text, style, icon_color=COLOR_PRIMARY_GREEN):
    # Ensure your font supports the icon_char or use an Image flowable.
    # This simple version might have alignment issues between icon and text.
    # A Table could offer better control: Table([[Image(...), Paragraph(...)]], colWidths=[...])
    return Paragraph(f'<font name="Helvetica" color="{icon_color.hexval()}">{icon_char}</font>  {title_text.upper()}', style)

def format_month_year(date_str_yyyy_mm):
    if not date_str_yyyy_mm:
        return ""
    try:
        dt_obj = datetime.strptime(date_str_yyyy_mm, "%Y-%m")
        return dt_obj.strftime("%m/%Y") # Output: MM/YYYY as in image
    except ValueError:
        return date_str_yyyy_mm # Return original if parsing fails


def generate_pdf(data): # 'data' is the main dictionary passed from Flask
    buffer = io.BytesIO()
    
    margin_val = 0.6 * inch
    doc = ModernDocTemplate(buffer, pagesize=letter,
                            leftMargin=margin_val, rightMargin=margin_val,
                            topMargin=margin_val, bottomMargin=margin_val,
                            profile_image_path=data.get('profile_image_path'),
                            full_name=data.get('full_name'))

    styles = getSampleStyleSheet()
    # --- Define Styles ---
    styles.add(ParagraphStyle(name='FullName', fontName='Helvetica-Bold', fontSize=28, textColor=COLOR_TEXT_BLACK, spaceBefore=0.15*inch, leading=32, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='JobTitle', fontName='Helvetica', fontSize=11, textColor=white, leading=14, spaceBefore=0, spaceAfter=0.1*inch, alignment=TA_LEFT))
    
    styles.add(ParagraphStyle(name='LeftColH1', fontName='Helvetica-Bold', fontSize=10, textColor=COLOR_PRIMARY_GREEN, spaceBefore=0.25*inch, spaceAfter=0.1*inch, leading=12))
    styles.add(ParagraphStyle(name='LeftColText', fontName='Helvetica', fontSize=8.5, textColor=COLOR_TEXT_DARK, leading=11, spaceAfter=2))
    styles.add(ParagraphStyle(name='LeftColLink', parent=styles['LeftColText'], textColor=COLOR_LINK)) # Not explicitly used, but kept for potential
    styles.add(ParagraphStyle(name='LeftColItemTitle', fontName='Helvetica-Bold', fontSize=9, textColor=COLOR_TEXT_DARK, leading=11, spaceBefore=4, spaceAfter=1))
    styles.add(ParagraphStyle(name='LeftColItemDesc', parent=styles['LeftColText'], fontSize=8, leading=10, leftIndent=0)) # No extra indent for description below title

    styles.add(ParagraphStyle(name='RightColH1', fontName='Helvetica-Bold', fontSize=11, textColor=COLOR_PRIMARY_GREEN, spaceBefore=0.15*inch, spaceAfter=0.05*inch, leading=14, borderPadding=0, leftIndent=0)) # Adjusted for icon handling in create_section_header
    styles.add(ParagraphStyle(name='RightColBody', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT_DARK, leading=12.5, spaceAfter=0.1*inch, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='ExpJobTitle', fontName='Helvetica-Bold', fontSize=10, textColor=COLOR_TEXT_BLACK, leading=13))
    styles.add(ParagraphStyle(name='ExpCompanyLocation', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT_MUTED, leading=11)) # Combined company & location
    styles.add(ParagraphStyle(name='ExpDates', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT_MUTED, leading=11, alignment=TA_RIGHT)) # Dates aligned right
    styles.add(ParagraphStyle(name='ExpBullet', parent=styles['RightColBody'], bulletIndent=10, leftIndent=15, firstLineIndent=0, spaceBefore=1, fontSize=8.5, leading=11))

    styles.add(ParagraphStyle(name='EduDegree', fontName='Helvetica-Bold', fontSize=10, textColor=COLOR_TEXT_BLACK, leading=13))
    styles.add(ParagraphStyle(name='EduInstitution', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT_DARK, leading=11))
    styles.add(ParagraphStyle(name='EduLocationDates', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT_MUTED, leading=11, alignment=TA_RIGHT))


    # --- Story for Left Column ---
    story_left = []
    story_left.append(Spacer(1, 2.9 * inch)) # Adjust this spacer to clear profile image area

    # CONTACTS
    story_left.append(create_section_header('✉', 'CONTACTS', styles['LeftColH1'])) # Icon: ✉ (envelope) or use an image
    if data.get('phone'):
        story_left.append(Paragraph(data['phone'], styles['LeftColText']))
    if data.get('email'):
        story_left.append(Paragraph(data['email'], styles['LeftColText']))
    if data.get('linkedin'):
        # For clickable link, you'd need HTML-like <a href="..."> or canvas drawing
        story_left.append(Paragraph(data['linkedin'], styles['LeftColText']))
    if data.get('location'):
        story_left.append(Paragraph(data['location'], styles['LeftColText']))
    story_left.append(Spacer(1, 0.2*inch))

    # KEY ACHIEVEMENTS
    if data.get('key_achievements'):
        story_left.append(create_section_header('🚩', 'KEY ACHIEVEMENTS', styles['LeftColH1'])) # Icon: 🚩 (flag)
        for ach in data['key_achievements']:
            # Using a simple bullet character. A custom bullet image or drawing could be used.
            story_left.append(Paragraph(f"<font color='{COLOR_PRIMARY_GREEN.hexval()}'>\u2022</font> {ach['title']}", styles['LeftColItemTitle']))
            story_left.append(Paragraph(ach['description'], styles['LeftColItemDesc']))
            story_left.append(Spacer(1, 0.05*inch))
        story_left.append(Spacer(1, 0.2*inch))

    # COURSES
    if data.get('courses'):
        story_left.append(create_section_header('📄', 'COURSES', styles['LeftColH1'])) # Icon: 📄 (document)
        for course in data['courses']:
            story_left.append(Paragraph(course['title'], styles['LeftColItemTitle']))
            story_left.append(Paragraph(course['description'], styles['LeftColItemDesc']))
            story_left.append(Spacer(1, 0.05*inch))

    # --- Story for Right Column ---
    story_right = []
    story_right.append(Spacer(1, 0.1*inch)) # Spacer to align with green background
    if data.get('full_name'):
        story_right.append(Paragraph(data['full_name'], styles['FullName']))
    if data.get('title_subtitle'):
        story_right.append(Paragraph(data['title_subtitle'], styles['JobTitle']))
    story_right.append(Spacer(1, 0.35*inch)) # Spacer after name block

    # SUMMARY
    story_right.append(create_section_header('👤', 'SUMMARY', styles['RightColH1']))
    if data.get('summary'):
        story_right.append(Paragraph(data['summary'], styles['RightColBody']))
    story_right.append(Spacer(1, 0.2*inch))

    # EXPERIENCE
    story_right.append(create_section_header('💼', 'EXPERIENCE', styles['RightColH1']))
    for exp in data.get('experiences', []):
        # Experience Title and Dates in a Table for side-by-side alignment
        exp_header_data = [
            [Paragraph(exp['title'], styles['ExpJobTitle']), 
             Paragraph(f"{format_month_year(exp.get('start_date'))} - {format_month_year(exp.get('end_date')) if not exp.get('is_present') else 'Present'}", styles['ExpDates'])]
        ]
        exp_header_table = Table(exp_header_data, colWidths=['70%', '30%'])
        exp_header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ]))
        story_right.append(exp_header_table)
        
        company_line = exp['company']
        if exp.get('location'): company_line += f" | {exp['location']}"
        story_right.append(Paragraph(company_line, styles['ExpCompanyLocation']))
        
        description_text = exp.get('description', '')
        if description_text:
            points = [p.strip() for p in description_text.split('\n') if p.strip()]
            for point in points:
                clean_point = point.lstrip('-*• ') 
                story_right.append(Paragraph(f"\u2022 {clean_point}", styles['ExpBullet'])) # Using bullet character
        story_right.append(Spacer(1, 0.15*inch))
    story_right.append(Spacer(1, 0.1*inch))

    # EDUCATION
    story_right.append(create_section_header('🎓', 'EDUCATION', styles['RightColH1']))
    for edu in data.get('education_entries', []):
        edu_header_data = [
            [Paragraph(edu['degree'], styles['EduDegree']),
             Paragraph(f"{format_month_year(edu.get('start_date'))} - {format_month_year(edu.get('end_date')) if not edu.get('is_present') else 'Present'}", styles['EduLocationDates'])]
        ]
        edu_header_table = Table(edu_header_data, colWidths=['70%', '30%'])
        edu_header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ]))
        story_right.append(edu_header_table)

        institution_line = edu['institution']
        if edu.get('edu_location'): institution_line += f" | {edu['edu_location']}"
        story_right.append(Paragraph(institution_line, styles['EduInstitution']))

        if edu.get('edu_details'):
            story_right.append(Paragraph(edu['edu_details'], styles['RightColBody']))
        story_right.append(Spacer(1, 0.15*inch))

    # --- Combine Stories ---
    full_story = []
    full_story.extend(story_left)
    full_story.append(FrameBreak()) # Move to the right column frame
    full_story.extend(story_right)

    doc.build(full_story)
    buffer.seek(0)
    return buffer