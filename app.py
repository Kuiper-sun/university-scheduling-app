from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import os
import tempfile
import csv
import traceback
from branch_and_bound import run_branch_and_bound_algorithm
import logging
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/import-data', methods=['POST'])
def import_data():
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, newline='', suffix='.csv') as temp_file:
            writer = csv.writer(temp_file, delimiter='\t')
            writer.writerow([
                "Timestamp", "Professor's Name", 
                'Please rate your preference for teaching "Design and Analysis of Algorithms"  from 1 (least preferred) to 5 (most preferred).',
                'Please select timeslots based on your availability to teach this course. [9:00 am - 12:00 pm]',
                'Please select timeslots based on your availability to teach this course. [12:00 pm - 3:00 pm]',
                'Please select timeslots based on your availability to teach this course. [3:00 pm - 6:00 pm]',
                'Please select timeslots based on your availability to teach this course. [5:00 pm - 9:00 pm]',
                'Please select timeslots based on your availability to teach this course. [10:00 am - 1:00 pm]',
                'Please rate your preference for teaching "Information Management"  from 1 (least preferred) to 5 (most preferred).',
                'Please rate your preference for teaching "Operating Systems"  from 1 (least preferred) to 5 (most preferred).',
                'Please rate your preference for teaching "Data Communications and Networking"  from 1 (least preferred) to 5 (most preferred).',
                'Please rate your preference for teaching "Technical Documentations"  from 1 (least preferred) to 5 (most preferred).'
            ])
            writer.writerow([
                "07/07/2024 10:48:25", "Kevin G. Fulgencio", "5", "9:00 am - 12:00 pm", "12:00 pm - 3:00 pm", "", "", "", "5", "1", "2", "3"
            ])
            temp_file_path = temp_file.name

        logger.info(f"Processing default data file: {temp_file_path}")
        schedule, steps = run_branch_and_bound_algorithm(temp_file_path)
        os.unlink(temp_file_path)
        
        if not schedule or not steps:
            return jsonify({'error': 'Algorithm did not produce a valid schedule'}), 400
        
        # Store the schedule and steps in session
        session['schedule'] = schedule
        session['steps'] = steps

        return render_template('results.html', schedule=schedule, steps=steps)

    except Exception as e:
        logger.error(f"Error in import_data: {str(e)}")
        return jsonify({'error': 'Error processing default data'}), 500

@app.route('/process-data', methods=['POST'])
def process_data():
    if 'data_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['data_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            schedule, steps = run_branch_and_bound_algorithm(filepath)
            os.unlink(filepath)
            
            if not schedule or not steps:
                return jsonify({'error': 'Algorithm did not produce a valid schedule'}), 400
            
            
            session['schedule'] = schedule
            session['steps'] = steps

            return render_template('results.html', schedule=schedule, steps=steps)

        except Exception as e:
            logger.error(f"Error in process_data: {str(e)}")
            return jsonify({'error': 'Error processing uploaded file'}), 500

    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/download-csv', methods=['GET'])
def download_csv():
    logger.info("Download CSV route accessed")
    try:
        schedule = session.get('schedule', [])
        logger.info(f"Schedule from session: {schedule}")
        if not schedule:
            logger.warning("No schedule data available")
            return jsonify({'error': 'No schedule data available'}), 400

        output = io.StringIO()
        writer = csv.writer(output)

        # Write CSV header
        writer.writerow(['Professor', 'Course', 'Timeslot'])

        # Write schedule data
        for entry in schedule:
            writer.writerow([entry['professor'], entry['course'], entry['timeslot']])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='schedule.csv'
        )
    except Exception as e:
        logger.exception(f"Error in download_csv: {str(e)}")
        return jsonify({'error': f'Error generating CSV: {str(e)}'}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xls', 'xlsx'}

if __name__ == '__main__':
    app.run(debug=True)
