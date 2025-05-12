# app.py
from flask import Flask, render_template, request, redirect, url_for, session, make_response
import io
import os
from pdf_templates import classic_template, modern_template # Assuming modern_template is the one we are focusing on

app = Flask(__name__)
app.secret_key = os.urandom(24) # For session management

AVAILABLE_TEMPLATES = {
    "template_1_classic": {
        "name": "Template 1 (Classic)",
        "generator": classic_template.generate_pdf,
        "preview_image": "images/classic_preview.png" # Ensure this image exists
    },
    "template_2_modern": {
        "name": "Template 2 (Modern Design)",
        "generator": modern_template.generate_pdf,
        "preview_image": "images/modern_preview.png" # Ensure this image exists
    }
}

# Updated SAMPLE_RESUME_DATA as per the previous response for dynamic forms
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
}

@app.route('/', methods=['GET', 'POST'])
def resume_form():
    if request.method == 'POST':
        resume_data = {
            'full_name': request.form.get('full_name'),
            'title_subtitle': request.form.get('title_subtitle'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'linkedin': request.form.get('linkedin', ''),
            'location': request.form.get('location', ''),
            'profile_image_path': session.get('resume_data', {}).get('profile_image_path', SAMPLE_RESUME_DATA.get('profile_image_path')),
            'summary': request.form.get('summary'),
            'key_achievements': [],
            'courses': [],
            'experiences': [],
            'education_entries': []
        }

        for i in range(1, 4):
            ach_title = request.form.get(f'ach_title_{i}')
            if ach_title:
                resume_data['key_achievements'].append({
                    'title': ach_title,
                    'description': request.form.get(f'ach_description_{i}', '')
                })
        
        for i in range(1, 3):
            course_title = request.form.get(f'course_title_{i}')
            if course_title:
                resume_data['courses'].append({
                    'title': course_title,
                    'description': request.form.get(f'course_description_{i}', '')
                })

        i = 0
        while True:
            title_key = f'exp_title[{i}]'
            if title_key not in request.form or not request.form[title_key]:
                break
            is_present_val = request.form.get(f'exp_present[{i}]') == 'on'
            resume_data['experiences'].append({
                'title': request.form[title_key],
                'company': request.form.get(f'exp_company[{i}]', ''),
                'location': request.form.get(f'exp_location[{i}]', ''),
                'start_date': request.form.get(f'exp_start_date[{i}]', ''),
                'end_date': request.form.get(f'exp_end_date[{i}]', '') if not is_present_val else '',
                'is_present': is_present_val,
                'description': request.form.get(f'exp_description[{i}]', '')
            })
            i += 1

        i = 0
        while True:
            degree_key = f'edu_degree[{i}]'
            if degree_key not in request.form or not request.form[degree_key]:
                break
            is_present_val_edu = request.form.get(f'edu_present[{i}]') == 'on'
            resume_data['education_entries'].append({
                'degree': request.form[degree_key],
                'institution': request.form.get(f'edu_institution[{i}]', ''),
                'edu_location': request.form.get(f'edu_location[{i}]', ''),
                'start_date': request.form.get(f'edu_start_date[{i}]', ''),
                'end_date': request.form.get(f'edu_end_date[{i}]', '') if not is_present_val_edu else '',
                'is_present': is_present_val_edu,
                'edu_details': request.form.get(f'edu_details[{i}]', '')
            })
            i += 1
        
        session['resume_data'] = resume_data
        return redirect(url_for('select_pdf_template'))

    form_data = session.get('resume_data', SAMPLE_RESUME_DATA.copy())
    return render_template('form.html', title="Create Your Resume", data=form_data)

@app.route('/select-template', methods=['GET'])
def select_pdf_template():
    if 'resume_data' not in session:
        return redirect(url_for('resume_form'))
    return render_template('select_template.html',
                           title="Select a Template",
                           templates=AVAILABLE_TEMPLATES)

@app.route('/download-resume/<template_id>', methods=['GET'])
def download_resume(template_id):
    if 'resume_data' not in session:
        return redirect(url_for('resume_form'))
    if template_id not in AVAILABLE_TEMPLATES:
        return "Invalid template selected", 404

    resume_data = session['resume_data']
    template_info = AVAILABLE_TEMPLATES[template_id]
    try:
        pdf_buffer = template_info['generator'](resume_data)
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = \
            f'attachment; filename={resume_data.get("full_name", "resume").replace(" ", "_")}_{template_id}.pdf'
        return response
    except Exception as e:
        import traceback
        app.logger.error(f"Error generating PDF for template {template_id}: {e}\n{traceback.format_exc()}")
        return f"An error occurred while generating PDF: <pre>{traceback.format_exc()}</pre>", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')