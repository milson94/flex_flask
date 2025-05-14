# app.py
from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash
import io
import os
import traceback
from pdf_templates import classic_template, modern_template # Assuming modern_template is the one we are focusing on

app = Flask(__name__)
# IMPORTANT: Change this secret key for production!
app.secret_key = os.urandom(24) # For session management and flash messages

# --- Template Configuration ---
AVAILABLE_TEMPLATES = {
    "template_1_classic": {
        "name": "Template 1 (Classic)",
        "generator": classic_template.generate_pdf, # MAKE SURE this function is updated for A4/Ordering
        "preview_image": "images/classic_preview.png" # Ensure this image exists in static/images/
    },
    "template_2_modern": {
        "name": "Template 2 (Modern Design)",
        "generator": modern_template.generate_pdf,   # Updated function below handles A4/Ordering
        "preview_image": "images/modern_preview.png" # Ensure this image exists in static/images/
    }, 
    "template_3": {
        "name": "Template 3 (Classic)",
        "generator": classic_template.generate_pdf, # MAKE SURE this function is updated for A4/Ordering
        "preview_image": "images/classic_preview.png" # Ensure this image exists in static/images/
    },
    "template_4": {
        "name": "Template 4 (Modern Design)",
        "generator": modern_template.generate_pdf,   # Updated function below handles A4/Ordering
        "preview_image": "images/modern_preview.png" # Ensure this image exists in static/images/
    }, 
        "template_5_professional": {
        "name": "Template 5 (Professional)",
        "generator": modern_template.generate_pdf, # Assuming 'modern_template' can handle the structure, otherwise change to professional_template.generate_pdf once you've adapted it
        "preview_image": "images/professional_preview.png" # You'll need to create this preview image
    }
    # Add more templates here
}

    # Add more templates here

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
    # section_order will be added dynamically
}

# Define the sections that can be reordered and their display names
# NOTE: Adjust keys based on how they are handled in your templates (e.g., modern template has left/right col sections)
REORDERABLE_SECTIONS = {
    'summary': 'Professional Summary',
    'experience': 'Professional Experience',
    'education': 'Education',
    'achievements': 'Key Achievements', # Add logic in PDF template to place correctly (e.g., left col)
    'courses': 'Courses'               # Add logic in PDF template to place correctly (e.g., left col)
}
# Define a default order - adjust based on common preference
DEFAULT_SECTION_ORDER = ['summary', 'experience', 'education', 'achievements', 'courses']


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
            'profile_image_path': existing_profile_path, # Keep existing image path for now
            'summary': request.form.get('summary', '').strip(),
            'key_achievements': [],
            'courses': [],
            'experiences': [],
            'education_entries': []
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
                'description': request.form.get(f'exp_description[{i}]', '').strip()
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
                resume_data['section_order'] = submitted_keys # Update order in data
                session['resume_data'] = resume_data # Save updated data to session
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
         ordered_sections_for_template.append((key, REORDERABLE_SECTIONS[key])) # Append missing ones at the end

    return render_template('order_sections.html',
                           title="Order Resume Sections",
                           sections=ordered_sections_for_template)


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
    app.run(debug=True, host='0.0.0.0', port=5000) # Make sure port is accessible if using Docker/VM