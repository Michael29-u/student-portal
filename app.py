from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['DATABASE'] = 'students.db'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'], timeout=30, isolation_level=None)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('PRAGMA journal_mode=DELETE')
        db.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                country TEXT NOT NULL,
                dob DATE NOT NULL,
                gender TEXT NOT NULL,
                program TEXT NOT NULL,
                student_id TEXT NOT NULL,
                gpa REAL NOT NULL,
                image TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()
        try:
            db.execute('ALTER TABLE students ADD COLUMN country TEXT NOT NULL DEFAULT "Unknown"')
            db.commit()
        except Exception:
            pass

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/api/countries')
def get_countries():
    countries = ['Nigeria', 'Ghana', 'Kenya', 'South Africa', 'United States', 'United Kingdom', 'Canada', 'Australia']
    return jsonify(countries)

@app.route('/api/programs')
def get_programs():
    programs = ['Computer Science', 'Engineering', 'Business Administration', 'Medicine', 'Law', 'Arts', 'Science', 'Education']
    return jsonify(programs)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        country = request.form.get('country', '').strip()
        dob = request.form.get('dob', '').strip()
        gender = request.form.get('gender', '').strip()
        program = request.form.get('program', '').strip()
        student_id = request.form.get('student_id', '').strip()
        gpa = request.form.get('gpa', '').strip()

        required_fields = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'address': address,
            'city': city,
            'country': country,
            'dob': dob,
            'gender': gender,
            'program': program,
            'student_id': student_id,
            'gpa': gpa
        }
        for field, value in required_fields.items():
            if not value:
                flash(f'{field.replace("_", " ").title()} is required.', 'error')
                return redirect(url_for('form'))

        try:
            gpa_float = float(gpa)
            if gpa_float < 0 or gpa_float > 4.0:
                flash('GPA must be between 0.0 and 4.0.', 'error')
                return redirect(url_for('form'))
        except ValueError:
            flash('GPA must be a valid number.', 'error')
            return redirect(url_for('form'))

        image = request.files.get('image')
        image_filename = None
        if image and image.filename:
            if allowed_file(image.filename):
                filename = f"{first_name}_{last_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{image.filename.rsplit('.', 1)[1].lower()}"
                upload_folder = app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                image.save(os.path.join(upload_folder, filename))
                image_filename = filename
            else:
                flash('Invalid image format. Allowed: png, jpg, jpeg, gif.', 'error')
                return redirect(url_for('form'))

        db = get_db()
        db.execute('''
            INSERT INTO students (first_name, last_name, email, phone, address, city, country, dob, gender, program, student_id, gpa, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, phone, address, city, country, dob, gender, program, student_id, gpa_float, image_filename))
        db.commit()
        flash('Student registered successfully!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error registering student: {str(e)}', 'error')
        return redirect(url_for('form'))

@app.route('/index')
def index():
    db = get_db()
    students = db.execute('SELECT * FROM students ORDER BY created_at DESC').fetchall()
    return render_template('index.html', students=students)

@app.route('/student/<int:student_id>')
def student_details(student_id):
    db = get_db()
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('index'))
    return render_template('details.html', student=student)

@app.route('/update_status/<int:student_id>', methods=['POST'])
def update_status(student_id):
    try:
        status = request.form.get('status')
        db = get_db()
        db.execute('UPDATE students SET status = ? WHERE id = ?', (status, student_id))
        db.commit()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
