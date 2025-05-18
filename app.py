# app.py
from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash
import io
import os
import traceback

# Import the specific template files based on your project structure image
# Assuming each template_X.py file contains a 'generate_pdf' function
# You only need to import the templates you list in AVAILABLE_TEMPLATES
# Let's import all shown in the image up to 20 for completeness in the AVAILABLE_TEMPLATES config
from pdf_templates import (
    template_1, template_2, template_3, template_4, template_5,
    template_6, template_7, template_8, template_9, template_10,
    template_11, template_12, template_14, template_15,
    template_16, template_17, template_18, template_19, template_20
)


app = Flask(__name__)
# IMPORTANT: Change this secret key for production!
app.secret_key = os.urandom(24) # For session management and flash messages

# --- Template Configuration ---
# Update keys and generators to match the filenames template_X.py
AVAILABLE_TEMPLATES = {
    "template_1": {
        "name": "Template 1",
        "generator": template_1.generate_pdf, # Use generator from template_1.py
        "preview_image": "images/classic_preview.png" # Keep preview image name
    },
    "template_2": {
        "name": "Template 2",
        "generator": template_2.generate_pdf,   # Use generator from template_2.py
        "preview_image": "images/modern_preview.png" # Keep preview image name
    },
    "template_3": {
        "name": "Template 3",
        "generator": template_3.generate_pdf,   # Use generator from template_2.py
        "preview_image": "images/modern_preview.png" # Keep preview image name
    },
     
    "template_4": {
        "name": "Template 4 (Alternative Modern)",
        "generator": template_4.generate_pdf, # Use generator from template_4.py
        "preview_image": "images/modern_preview.png" # Reusing preview
    },
    "template_5": {
        "name": "Template 5 (Professional)",
        "generator": template_5.generate_pdf, # Use generator from template_5.py
        "preview_image": "images/professional_preview.png" # Keep preview image name
    },
    # Add placeholders for other templates shown in the image (6-20)
    # You would need to add actual generator functions and preview images for these
    # Assuming they also have a generate_pdf function in their respective files
     "template_6": { "name": "Template 6", "generator": template_6.generate_pdf, "preview_image": "images/modern_preview.png" },
     "template_7": { "name": "Template 7", "generator": template_7.generate_pdf, "preview_image": "images/modern_preview.png" },
     "template_8": { "name": "Template 8", "generator": template_8.generate_pdf, "preview_image": "images/modern_preview.png" },
     "template_9": { "name": "Template 9", "generator": template_9.generate_pdf, "preview_image": "images/modern_preview.png" },
     "template_10": { "name": "Template 10", "generator": template_10.generate_pdf, "preview_image": "images/modern_preview.png" },
     "template_11": { "name": "Template 11", "generator": template_11.generate_pdf, "preview_image": "images/modern_preview.png" },
     "template_12": { "name": "Template 12", "generator": template_12.generate_pdf, "preview_image": "images/modern_preview.png" },
     "template_14": { "name": "Template 14", "generator": template_14.generate_pdf, "preview_image": "images/modern_preview.png" },
     "template_15": { "name": "Template 15", "generator": template_15.generate_pdf, "preview_image": "images/modern_preview.png" },
     "template_16": { "name": "Template 16", "generator": template_16.generate_pdf, "preview_image": "images/modern_preview.png" },
     "template_17": { "name": "Template 17", "generator": template_17.generate_pdf, "preview_image": "images/modern_preview.png" },
     "template_18": { "name": "Template 18", "generator": template_18.generate_pdf, "preview_image": "images/modern_preview.png" },
     "template_19": { "name": "Template 19", "generator": template_19.generate_pdf, "preview_image": "images/modern_preview.png" },
     "template_20": { "name": "Template 20", "generator": template_20.generate_pdf, "preview_image": "images/modern_preview.png" },
}


# --- Default Data & Structure ---
SAMPLE_RESUME_DATA = {
    'full_name': 'Maeve Delaney',
    'title_subtitle': 'Strategic Sourcing Leader | Procurement Specialist | Team Management',
    'email': 'help@enhancv.com',
    'phone': '+1-(234)-555-1234',
    'linkedin': 'linkedin.com/in/maevedelaney',
    'location': 'Charlotte, North Carolina',
    'profile_image_path': 'static/images/sample_profile.jpg', # Ensure this image exists

    'summary': 'Dynamic procurement specialist with over 5 years of experience in strategic sourcing and team management. Highly skilled in supply chain optimization and developing category strategies. Proven leader with an MBA and a solid track record in transformative sourcing initiatives, delivering significant cost savings and operational efficiencies.',

    'key_achievements': [
        {'title': 'Implemented Supplier Performance Management System', 'description': 'Successfully introduced a systematic approach to evaluating and improving supplier performance, elevating efficiency by 10%.'},
        {'title': 'Managed $500M Indirect Spend Portfolio', 'description': 'Directed strategic allocation and cost-saving initiatives across diverse departments, optimizing the company’s substantial indirect spend.'},
        {'title': 'Achieved 15% Annual Cost Savings', 'description': 'Strategized and executed a category management plan for medical supplies that slashed annual costs significantly.'}
    ],
    'courses': [
        {'title': 'Certified Professional in Supply Management', 'description': 'Intensive course covering strategic sourcing and supply chain management, provided by the Institute for Supply Management.'}
    ],
    'experiences': [
        {
            'title': 'Senior Sourcing Manager',
            'company': 'Premier Inc.',
            'location': 'Charlotte, NC',
            'start_date': '2018-06', # YYYY-MM
            'end_date': '',          # Empty if present
            'is_present': True,
            'description': '- Developed and executed category strategy for medical supplies, reducing annual costs by 15% through strategic supplier consolidation.\n- Led cross-functional teams in the successful negotiation of complex service contracts, yielding a 20% improvement in service level agreements.\n- Implemented a supplier performance management system, enhancing supplier quality and compliance, and resulting in a 10% increase in supplier scorecard performance.' # Newline separated points
        },
        {
            'title': 'Category Manager',
            'company': 'Honeywell',
            'location': 'Fort Mill, SC',
            'start_date': '2015-01',
            'end_date': '2018-05',
            'is_present': False,
            'description': '- Executed multi-year growth plans for the electronics category, delivering a sustained 10% year-over-year cost reduction.\n- Conducted extensive market trends analysis leading to the early identification of cost-saving opportunities.'
        },
    ],
    'education_entries': [
        {
            'degree': 'Master of Business Administration',
            'institution': 'Duke University',
            'edu_location': 'Durham, NC',
            'start_date': '2007-01', # YYYY-MM
            'end_date': '2009-01',   # YYYY-MM
            'is_present': False,
            'edu_details': 'Relevant coursework in strategic finance and operations management.'
        },
        {
            'degree': 'Bachelor of Science in Supply Chain Management',
            'institution': 'North Carolina State University',
            'edu_location': 'Raleigh, NC',
            'start_date': '2003-01',
            'end_date': '2007-01',
            'is_present': False,
            'edu_details': 'Graduated with Honors.'
        }
    ],
     'languages': [], # ADDED
    # section_order will be added dynamically
}

# Define the sections that can be reordered and their display names
# NOTE: Adjust keys based on how they are handled in your templates (e.g., modern template has left/right col sections)
REORDERABLE_SECTIONS = {
    'summary': 'Professional Summary',
    'experience': 'Professional Experience',
    'education': 'Education',
    'achievements': 'Key Achievements',
    'courses': 'Courses',
    'skills': 'Skills',
    'hobbies': 'Hobbies',
    'languages': 'Languages',
    'additional_info': 'Additional Information',
    'references': 'References',
    'projects': 'Projects',
}

# Define a default order - adjust based on common preference
DEFAULT_SECTION_ORDER = list(REORDERABLE_SECTIONS.keys())


# --- Routes ---

@app.route('/')
def home():
    """Renders the landing page."""
    return render_template('home.html', title="Resume Builder Home")


@app.route('/create', methods=['GET', 'POST'])
def resume_form():
    """Handles the resume data input form."""
    if request.method == 'POST':
        # Retrieve existing profile image path from session if available
        existing_profile_path = session.get('resume_data', {}).get('profile_image_path', SAMPLE_RESUME_DATA.get('profile_image_path'))

        resume_data = {
            'full_name': request.form.get('full_name', '').strip(),
            'title_subtitle': request.form.get('title_subtitle', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'linkedin': request.form.get('linkedin', '').strip(),
            'location': request.form.get('location', '').strip(),
            'nationality': request.form.get('nationality', '').strip(),
            'birth_date': request.form.get('birth_date', '').strip(),
            'gender': request.form.get('gender', '').strip(),
            'profile_image_path': existing_profile_path, # Keep existing image path for now
            'summary': request.form.get('summary', '').strip(),
            'place_of_birth': request.form.get('place_of_birth', '').strip(),  # Novo
            'cargo': request.form.get('cargo', '').strip(),
            'driving_license': request.form.get('driving_license', '').strip(),
            'marital_status': request.form.get('marital_status', '').strip(),
            'military_service': request.form.get('military_service', '').strip(),
            'website': request.form.get('website', '').strip(),
            'address': request.form.get('address', '').strip(),
            'skills': request.form.get('skills', '').strip(),
            'hobbies': request.form.get('hobbies', '').strip(),
            'key_achievements': [],
            'courses': [],
            'experiences': [],
            'education_entries': [],
            'languages': [],
            'additional_info': [],
            'references': [],
            'projects': [],
        }

        # --- Parsing logic for lists ---
        # Key Achievements (fixed number)
        for i in range(1, 4):
            ach_title = request.form.get(f'ach_title_{i}', '').strip()
            if ach_title: # Only add if title is present
                resume_data['key_achievements'].append({
                    'title': ach_title,
                    'description': request.form.get(f'ach_description_{i}', '').strip()
                })

        # Courses (fixed number)
        for i in range(1, 3):
            course_title = request.form.get(f'course_title_{i}', '').strip()
            if course_title: # Only add if title is present
                resume_data['courses'].append({
                    'title': course_title,
                    'description': request.form.get(f'course_description_{i}', '').strip()
                })

        # Experiences (dynamic number)
        i = 0
        while True:
            title_key = f'exp_title[{i}]'
            if title_key not in request.form or not request.form[title_key].strip():
                break # Stop if title is missing or empty for this index
            is_present_val = request.form.get(f'exp_present[{i}]') == 'on'
            resume_data['experiences'].append({
                'title': request.form[title_key].strip(),
                'company': request.form.get(f'exp_company[{i}]', '').strip(),
                'location': request.form.get(f'exp_location[{i}]', '').strip(),
                'start_date': request.form.get(f'exp_start_date[{i}]', ''),
                'end_date': request.form.get(f'exp_end_date[{i}]', '') if not is_present_val else '',
                'is_present': is_present_val,
                'description': request.form.get(f'exp_description[{i}]', '').strip(),
                'achievements': request.form.get(f'exp_achievements[{i}]', '').strip(),
                'responsibilities': request.form.get(f'exp_responsibilities[{i}]', '').strip(),
            })
            i += 1

        # Education (dynamic number)
        i = 0
        while True:
            degree_key = f'edu_degree[{i}]'
            if degree_key not in request.form or not request.form[degree_key].strip():
                break # Stop if degree is missing or empty for this index
            is_present_val_edu = request.form.get(f'edu_present[{i}]') == 'on'
            resume_data['education_entries'].append({
                'degree': request.form[degree_key].strip(),
                'institution': request.form.get(f'edu_institution[{i}]', '').strip(),
                'edu_location': request.form.get(f'edu_location[{i}]', '').strip(),
                'start_date': request.form.get(f'edu_start_date[{i}]', ''),
                'end_date': request.form.get(f'edu_end_date[{i}]', '') if not is_present_val_edu else '',
                'is_present': is_present_val_edu,
                'edu_details': request.form.get(f'edu_details[{i}]', '').strip()
            })
            i += 1

        # Languages (dynamic number)
        i = 0
        while True:
            lang_name_key = f'lang_name[{i}]'
            if lang_name_key not in request.form or not request.form[lang_name_key].strip():
                break
            resume_data['languages'].append({
                'name': request.form[lang_name_key].strip(),
                'level': request.form.get(f'lang_level[{i}]', '').strip(),
                'reading': request.form.get(f'lang_reading[{i}]', '').strip(),
                'writing': request.form.get(f'lang_writing[{i}]', '').strip()
            })
            i += 1

        # Additional Info (dynamic number)
        i = 0
        while True:
            info_title_key = f'info_title[{i}]'
            if info_title_key not in request.form or not request.form[info_title_key].strip():
                break
            resume_data['additional_info'].append({
                'title': request.form[info_title_key].strip(),
                'description': request.form.get(f'info_description[{i}]', '').strip()
            })
            i += 1

        # References (dynamic number)
        i = 0
        while True:
            ref_name_key = f'ref_name[{i}]'
            if ref_name_key not in request.form or not request.form[ref_name_key].strip():
                break
            resume_data['references'].append({
                'name': request.form[ref_name_key].strip(),
                'title': request.form.get(f'ref_title[{i}]', '').strip(),
                'phone': request.form.get(f'ref_phone[{i}]', '').strip(),
                'description': request.form.get(f'ref_description[{i}]', '').strip()
            })
            i += 1

        # Projects (dynamic number)
        i = 0
        while True:
            proj_title_key = f'proj_title[{i}]'
            if proj_title_key not in request.form or not request.form[proj_title_key].strip():
                break
            resume_data['projects'].append({
                'title': request.form[proj_title_key].strip(),
                'description': request.form.get(f'proj_description[{i}]', '').strip(),
                'dates': request.form.get(f'proj_dates[{i}]', '').strip()
            })
            i += 1

        # --- End of Parsing Logic ---

        # Add default section order when saving data
        resume_data['section_order'] = session.get('resume_data', {}).get('section_order', DEFAULT_SECTION_ORDER)
        session['resume_data'] = resume_data

        # Redirect to the section ordering step
        flash("Resume details saved. Now, order your sections.", "success")
        return redirect(url_for('order_sections'))

    # GET request: display the form, pre-filled with session or sample data
    form_data = session.get('resume_data', SAMPLE_RESUME_DATA.copy())
    # Ensure default order is present if loading from session or sample
    if 'section_order' not in form_data:
        form_data['section_order'] = DEFAULT_SECTION_ORDER
    return render_template('form.html', title="Create Your Resume", data=form_data)


@app.route('/order-sections', methods=['GET', 'POST'])
def order_sections():
    """Allows user to reorder resume sections."""
    if 'resume_data' not in session:
        flash("Please fill out your resume details first.", "warning")
        return redirect(url_for('resume_form'))

    resume_data = session['resume_data']
    current_order = resume_data.get('section_order', DEFAULT_SECTION_ORDER)

    if request.method == 'POST':
        new_order_str = request.form.get('section_order')
        if new_order_str:
            # Get keys submitted, ensure they are valid section keys
            submitted_keys = [key.strip() for key in new_order_str.split(',') if key.strip() in REORDERABLE_SECTIONS]

            # Validate: Check if all reorderable sections are present exactly once
            if set(submitted_keys) == set(REORDERABLE_SECTIONS.keys()) and len(submitted_keys) == len(REORDERABLE_SECTIONS):
                resume_data['section_order'] = submitted_keys  # Update order in data
                session['resume_data'] = resume_data  # Save updated data to session
                flash("Section order updated.", "success")
                return redirect(url_for('select_pdf_template'))
            else:
                flash("Invalid section order received. Please ensure all sections are present and try again.", "error")
                # Let it fall through to render the GET page again with the error
        else:
            flash("No section order was submitted.", "error")
            # Fall through

    # GET request or POST failed: Render the ordering page
    # Prepare sections for template based on the *current* order in session/default
    ordered_sections_for_template = []
    for key in current_order:
        if key in REORDERABLE_SECTIONS:
            ordered_sections_for_template.append((key, REORDERABLE_SECTIONS[key]))

    # Check if any reorderable sections defined were missing from the current order (e.g., old session data)
    current_keys_set = set(current_order)
    missing_keys = [key for key in REORDERABLE_SECTIONS if key not in current_keys_set]
    for key in missing_keys:
        ordered_sections_for_template.append((key, REORDERABLE_SECTIONS[key]))  # Append missing ones at the end
    print("ordered_sections_for_template: ", ordered_sections_for_template) # for debugging
    return render_template('order_sections.html',
                           title="Order Resume Sections",
                           sections=ordered_sections_for_template,
                           available_sections=REORDERABLE_SECTIONS)

@app.route('/select-template', methods=['GET'])
def select_pdf_template():
    """Displays available templates for selection."""
    if 'resume_data' not in session:
        flash("Please fill out your resume details first.", "warning")
        return redirect(url_for('resume_form'))

    # Ensure data exists before showing templates
    if 'section_order' not in session.get('resume_data', {}):
         flash("Section order missing. Please re-submit your details.", "warning")
         # Potentially redirect back to ordering or form?
         return redirect(url_for('order_sections'))

    return render_template('select_template.html',
                           title="Select a Template",
                           templates=AVAILABLE_TEMPLATES)


@app.route('/download-resume/<template_id>', methods=['GET'])
def download_resume(template_id):
    """Generates and serves the resume PDF for download."""
    if 'resume_data' not in session:
        flash("Session expired or data missing. Please start over.", "error")
        return redirect(url_for('resume_form'))
    if template_id not in AVAILABLE_TEMPLATES:
        flash("Invalid template selected.", "error")
        return redirect(url_for('select_pdf_template')) # Redirect back to selection

    resume_data = session['resume_data']
    template_info = AVAILABLE_TEMPLATES[template_id]

    # Ensure section_order exists, provide default as fallback just in case session got corrupted
    if 'section_order' not in resume_data:
        resume_data['section_order'] = DEFAULT_SECTION_ORDER
        app.logger.warning("section_order missing in session data for download, using default.")

    try:
        # The generator function MUST handle the section_order within resume_data
        pdf_buffer = template_info['generator'](resume_data)

        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        # Set Content-Disposition to 'attachment' to force download
        safe_filename = resume_data.get("full_name", "resume").replace(" ", "_").replace("/", "_") # Basic sanitization
        response.headers['Content-Disposition'] = \
            f'attachment; filename="{safe_filename}_{template_id}.pdf"'
        return response
    except Exception as e:
        app.logger.error(f"Error generating PDF for download (template {template_id}): {e}\n{traceback.format_exc()}")
        flash(f"An error occurred while generating the PDF for template '{template_info['name']}'. Please try again or choose another template.", "error")
        # Redirect back to template selection on error
        return redirect(url_for('select_pdf_template'))


if __name__ == '__main__':
    # Make sure this is set correctly for deployment environments
    app.run(debug=True, host='0.0.0.0', port=5000)