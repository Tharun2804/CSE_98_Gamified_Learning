from flask import Flask, render_template, request, redirect, session, send_from_directory, jsonify
import mysql.connector
import os
from datetime import date, timedelta
from dotenv import load_dotenv
load_dotenv()
from werkzeug.utils import secure_filename
from email_service import (send_registration_email, send_approval_email, 
                           send_streak_milestone_email, send_quiz_created_email,
                           send_video_posted_email, send_certificate_email)
from certificate_service import check_course_completion, create_certificate_for_student

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

if not os.path.exists('uploads'):
    os.makedirs('uploads')

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="gamified_learning"
    )

def update_streak(student_id, activity_type):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    today = date.today()
    
    # Update or insert daily activity
    if activity_type == 'lesson':
        cursor.execute("""
            INSERT INTO daily_activity (student_id, activity_date, lessons_completed, quizzes_attempted)
            VALUES (%s, %s, 1, 0)
            ON DUPLICATE KEY UPDATE lessons_completed = lessons_completed + 1
        """, (student_id, today))
    elif activity_type == 'quiz':
        cursor.execute("""
            INSERT INTO daily_activity (student_id, activity_date, lessons_completed, quizzes_attempted)
            VALUES (%s, %s, 0, 1)
            ON DUPLICATE KEY UPDATE quizzes_attempted = quizzes_attempted + 1
        """, (student_id, today))
    
    # Get user's last activity date
    cursor.execute("SELECT last_activity_date, current_streak, email, username FROM users WHERE id = %s", (student_id,))
    user = cursor.fetchone()
    
    last_date = user['last_activity_date']
    current_streak = user['current_streak'] or 0
    
    # Calculate new streak
    if last_date is None:
        new_streak = 1
    elif last_date == today:
        new_streak = current_streak
    elif last_date == today - timedelta(days=1):
        new_streak = current_streak + 1
    else:
        new_streak = 1
    
    # Update user streak
    cursor.execute("""
        UPDATE users 
        SET current_streak = %s, 
            longest_streak = GREATEST(longest_streak, %s),
            last_activity_date = %s
        WHERE id = %s
    """, (new_streak, new_streak, today, student_id))
    
    db.commit()
    
    # Send milestone emails for streaks
    if new_streak in [7, 14, 30, 50, 100] and user['email']:
        send_streak_milestone_email(user['email'], user['username'], new_streak)
    
    cursor.close()
    db.close()

@app.route('/')
def index():
    if 'user_id' in session:
        role = session['role']
        if role == 'student':
            return redirect('/student')
        elif role == 'teacher':
            return redirect('/teacher')
        elif role == 'parent':
            return redirect('/parent')
        elif role == 'admin':
            return redirect('/admin')
    return render_template('home.html', logged_in='user_id' in session)

@app.route('/student')
def student_dashboard():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    student = cursor.fetchone()
    cursor.execute("SELECT * FROM lessons ORDER BY id")
    lessons = cursor.fetchall()
    
    # Get quizzes with attempt status
    cursor.execute("""
        SELECT q.*, 
        (SELECT COUNT(*) FROM quiz_attempts qa WHERE qa.quiz_id = q.id AND qa.student_id = %s AND qa.is_correct = 1) as correct_count,
        (SELECT COUNT(*) FROM quiz_attempts qa WHERE qa.quiz_id = q.id AND qa.student_id = %s) as total_attempts
        FROM quizzes q ORDER BY q.created_at DESC
    """, (session['user_id'], session['user_id']))
    quizzes = cursor.fetchall()
    
    # Calculate score percentage for each quiz
    for quiz in quizzes:
        if quiz['total_attempts'] > 0:
            quiz['score'] = (quiz['correct_count'] / quiz['total_attempts']) * 100
            quiz['can_attempt'] = quiz['score'] < 40
        else:
            quiz['score'] = 0
            quiz['can_attempt'] = True
    
    cursor.execute("SELECT * FROM videos ORDER BY created_at DESC")
    videos = cursor.fetchall()
    cursor.execute("SELECT * FROM presentations ORDER BY created_at DESC")
    presentations = cursor.fetchall()
    
    # Get today's activity
    cursor.execute("""
        SELECT lessons_completed, quizzes_attempted 
        FROM daily_activity 
        WHERE student_id = %s AND activity_date = %s
    """, (session['user_id'], date.today()))
    today_activity = cursor.fetchone()
    
    # Check for certificate
    cursor.execute("SELECT * FROM certificates WHERE student_id = %s", (session['user_id'],))
    certificate = cursor.fetchone()
    
    # Check if eligible for certificate
    course_completed = check_course_completion(session['user_id'], db)
    
    cursor.close()
    db.close()
    return render_template('student.html', student=student, lessons=lessons, quizzes=quizzes, 
                         videos=videos, presentations=presentations, today_activity=today_activity,
                         certificate=certificate, course_completed=course_completed)

@app.route('/teacher')
def teacher_dashboard():
    if 'user_id' not in session or session['role'] != 'teacher':
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    teacher = cursor.fetchone()
    cursor.execute("SELECT u.username, u.points, u.level, u.current_streak FROM users u WHERE u.role = 'student'")
    students = cursor.fetchall()
    cursor.execute("SELECT * FROM quizzes WHERE teacher_id = %s ORDER BY created_at DESC", (session['user_id'],))
    quizzes = cursor.fetchall()
    cursor.execute("SELECT * FROM videos WHERE teacher_id = %s ORDER BY created_at DESC", (session['user_id'],))
    videos = cursor.fetchall()
    cursor.execute("SELECT * FROM presentations WHERE teacher_id = %s ORDER BY created_at DESC", (session['user_id'],))
    presentations = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('teacher.html', teacher=teacher, students=students, quizzes=quizzes, videos=videos, presentations=presentations)

@app.route('/parent')
def parent_dashboard():
    if 'user_id' not in session or session['role'] != 'parent':
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    parent = cursor.fetchone()
    cursor.execute("SELECT u.username, u.points, u.level, u.current_streak FROM users u WHERE u.role = 'student'")
    students = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('parent.html', parent=parent, students=students)

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    admin = cursor.fetchone()
    cursor.execute("SELECT role, COUNT(*) as count FROM users GROUP BY role")
    stats = cursor.fetchall()
    cursor.execute("SELECT * FROM users ORDER BY id")
    users = cursor.fetchall()
    cursor.execute("SELECT * FROM users WHERE approved = FALSE AND role != 'admin' ORDER BY id")
    pending_users = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('admin.html', admin=admin, stats=stats, users=users, pending_users=pending_users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s AND role = %s", (username, password, role))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        
        if user:
            if user['approved'] or user['role'] == 'admin':
                session['user_id'] = user['id']
                session['role'] = user['role']
                return redirect('/')
            else:
                return render_template('login.html', error='Account pending admin approval')
        else:
            return render_template('login.html', error='Invalid credentials')
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role', 'student')
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        username = request.form['username']
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        db = get_db()
        cursor = db.cursor()
        try:
            if role == 'student':
                student_id = request.form['student_id']
                school_name = request.form['school_name']
                class_grade = request.form['class_grade']
                parent_contact = request.form['parent_contact']
                dob = request.form['dob']
                cursor.execute("INSERT INTO users (username, password, role, full_name, student_id, email, school_name, class_grade, parent_contact, dob, approved) VALUES (%s, %s, 'student', %s, %s, %s, %s, %s, %s, %s, FALSE)",
                               (username, password, full_name, student_id, email, school_name, class_grade, parent_contact, dob))
            elif role == 'teacher':
                employee_id = request.form['employee_id']
                school_name = request.form['school_name']
                department = request.form['department']
                cursor.execute("INSERT INTO users (username, password, role, full_name, employee_id, email, school_name, department, approved) VALUES (%s, %s, 'teacher', %s, %s, %s, %s, %s, FALSE)",
                               (username, password, full_name, employee_id, email, school_name, department))
            else:  # parent
                linked_student_id = request.form['linked_student_id']
                relationship = request.form['relationship']
                parent_contact = request.form['parent_contact']
                cursor.execute("INSERT INTO users (username, password, role, full_name, email, linked_student_id, relationship, parent_contact, approved) VALUES (%s, %s, 'parent', %s, %s, %s, %s, %s, FALSE)",
                               (username, password, full_name, email, linked_student_id, relationship, parent_contact))
            
            db.commit()
            cursor.close()
            db.close()
            
            # Send registration email
            if email:
                send_registration_email(email, username, role)
            
            return render_template('register.html', success='Registration submitted! Wait for admin approval.')
        except:
            cursor.close()
            db.close()
            return render_template('register.html', error='Username already exists')
    
    return render_template('register.html')

@app.route('/complete/<int:lesson_id>')
def complete_lesson(lesson_id):
    if 'user_id' not in session or session['role'] != 'student':
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO progress (student_id, lesson_id) VALUES (%s, %s)", 
                   (session['user_id'], lesson_id))
    cursor.execute("UPDATE users SET points = points + 10 WHERE id = %s", 
                   (session['user_id'],))
    db.commit()
    cursor.close()
    
    # Update streak
    update_streak(session['user_id'], 'lesson')
    
    # Check if course completed and generate certificate
    if check_course_completion(session['user_id'], db):
        create_certificate_for_student(session['user_id'], db)
    
    db.close()
    return redirect('/student')

@app.route('/create_quiz', methods=['POST'])
def create_quiz():
    if 'user_id' not in session or session['role'] != 'teacher':
        return redirect('/login')
    
    title = request.form['title']
    question = request.form['question']
    option_a = request.form['option_a']
    option_b = request.form['option_b']
    option_c = request.form['option_c']
    option_d = request.form['option_d']
    correct_answer = request.form['correct_answer']
    points = request.form['points']
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("INSERT INTO quizzes (teacher_id, title, question, option_a, option_b, option_c, option_d, correct_answer, points) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   (session['user_id'], title, question, option_a, option_b, option_c, option_d, correct_answer, points))
    db.commit()
    
    # Notify all students about new quiz
    cursor.execute("SELECT username, email FROM users WHERE role = 'student' AND approved = TRUE AND email IS NOT NULL")
    students = cursor.fetchall()
    
    for student in students:
        send_quiz_created_email(student['email'], student['username'], title)
    
    cursor.close()
    db.close()
    return redirect('/teacher')

@app.route('/post_video', methods=['POST'])
def post_video():
    if 'user_id' not in session or session['role'] != 'teacher':
        return redirect('/login')
    
    title = request.form['title']
    video_file = request.files['video']
    
    if video_file:
        filename = secure_filename(video_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video_file.save(filepath)
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("INSERT INTO videos (teacher_id, title, url) VALUES (%s, %s, %s)",
                       (session['user_id'], title, filename))
        db.commit()
        
        # Notify all students about new video
        cursor.execute("SELECT username, email FROM users WHERE role = 'student' AND approved = TRUE AND email IS NOT NULL")
        students = cursor.fetchall()
        
        for student in students:
            send_video_posted_email(student['email'], student['username'], title)
        
        cursor.close()
        db.close()
    
    return redirect('/teacher')

@app.route('/post_presentation', methods=['POST'])
def post_presentation():
    if 'user_id' not in session or session['role'] != 'teacher':
        return redirect('/login')
    
    title = request.form['title']
    ppt_file = request.files['presentation']
    
    if ppt_file:
        filename = secure_filename(ppt_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        ppt_file.save(filepath)
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO presentations (teacher_id, title, file_path) VALUES (%s, %s, %s)",
                       (session['user_id'], title, filename))
        db.commit()
        cursor.close()
        db.close()
    
    return redirect('/teacher')

@app.route('/attempt_quiz/<int:quiz_id>', methods=['POST'])
def attempt_quiz(quiz_id):
    if 'user_id' not in session or session['role'] != 'student':
        return redirect('/login')
    
    answer = request.form['answer']
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM quizzes WHERE id = %s", (quiz_id,))
    quiz = cursor.fetchone()
    
    is_correct = (answer == quiz['correct_answer'])
    
    cursor.execute("INSERT INTO quiz_attempts (student_id, quiz_id, answer, is_correct) VALUES (%s, %s, %s, %s)",
                   (session['user_id'], quiz_id, answer, is_correct))
    
    if is_correct:
        cursor.execute("UPDATE users SET points = points + %s WHERE id = %s",
                       (quiz['points'], session['user_id']))
    
    db.commit()
    cursor.close()
    db.close()
    
    # Update streak
    update_streak(session['user_id'], 'quiz')
    
    return redirect('/student')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT full_name, username, points, level, current_streak, longest_streak FROM users WHERE role = 'student' ORDER BY points DESC, level DESC")
    students = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('leaderboard.html', students=students)

@app.route('/watergame')
def water_game():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect('/login')
    return render_template('watergame.html')

@app.route('/games')
def games_page():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect('/login')
    return render_template('games.html')

@app.route('/game')
def game_page():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect('/login')
    return render_template('game.html')

@app.route('/approve_user/<int:user_id>')
def approve_user(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get user details before approval
    cursor.execute("SELECT username, email, role FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    
    cursor.execute("UPDATE users SET approved = TRUE WHERE id = %s", (user_id,))
    db.commit()
    
    # Send approval email
    if user and user['email']:
        send_approval_email(user['email'], user['username'], user['role'])
    
    cursor.close()
    db.close()
    return redirect('/admin')

@app.route('/admin/student/<int:student_id>')
def admin_view_student(student_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users WHERE id = %s AND role = 'student'", (student_id,))
    student = cursor.fetchone()
    
    # Lessons completed
    cursor.execute("""
        SELECT l.title, l.description, l.points, p.completed_at
        FROM progress p JOIN lessons l ON p.lesson_id = l.id
        WHERE p.student_id = %s ORDER BY p.completed_at DESC
    """, (student_id,))
    progress = cursor.fetchall()
    
    # Quiz attempts
    cursor.execute("""
        SELECT q.title, q.question, qa.answer, qa.is_correct, qa.attempted_at
        FROM quiz_attempts qa JOIN quizzes q ON qa.quiz_id = q.id
        WHERE qa.student_id = %s ORDER BY qa.attempted_at DESC
    """, (student_id,))
    attempts = cursor.fetchall()
    
    # Certificate
    cursor.execute("SELECT * FROM certificates WHERE student_id = %s", (student_id,))
    certificate = cursor.fetchone()
    
    lessons_completed = len(progress)
    
    cursor.close()
    db.close()
    
    return render_template('admin_student_view.html', student=student, progress=progress,
                           attempts=attempts, certificate=certificate, lessons_completed=lessons_completed)

@app.route('/admin/teacher/<int:teacher_id>')
def admin_view_teacher(teacher_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users WHERE id = %s AND role = 'teacher'", (teacher_id,))
    teacher = cursor.fetchone()
    
    cursor.execute("SELECT * FROM quizzes WHERE teacher_id = %s ORDER BY created_at DESC", (teacher_id,))
    quizzes = cursor.fetchall()
    
    cursor.execute("SELECT * FROM videos WHERE teacher_id = %s ORDER BY created_at DESC", (teacher_id,))
    videos = cursor.fetchall()
    
    cursor.execute("SELECT * FROM presentations WHERE teacher_id = %s ORDER BY created_at DESC", (teacher_id,))
    presentations = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template('admin_teacher_view.html', teacher=teacher, quizzes=quizzes, videos=videos, presentations=presentations)
def delete_user(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM quiz_attempts WHERE student_id = %s", (user_id,))
    cursor.execute("DELETE FROM progress WHERE student_id = %s", (user_id,))
    cursor.execute("DELETE FROM daily_activity WHERE student_id = %s", (user_id,))
    cursor.execute("DELETE FROM certificates WHERE student_id = %s", (user_id,))
    cursor.execute("DELETE FROM quizzes WHERE teacher_id = %s", (user_id,))
    cursor.execute("DELETE FROM videos WHERE teacher_id = %s", (user_id,))
    cursor.execute("DELETE FROM presentations WHERE teacher_id = %s", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/generate_certificate')
def generate_certificate():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect('/login')
    
    db = get_db()
    
    if not check_course_completion(session['user_id'], db):
        db.close()
        return redirect('/student')
    
    cert_filename = create_certificate_for_student(session['user_id'], db)
    db.close()
    return redirect('/student')

@app.route('/view_certificate')
def view_certificate():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT u.full_name, u.username, c.certificate_id, c.issued_date FROM users u JOIN certificates c ON c.student_id = u.id WHERE u.id = %s", (session['user_id'],))
    cert = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not cert:
        return redirect('/student')
    
    from datetime import datetime
    issued = cert['issued_date']
    completion_date = issued.strftime('%B %d, %Y') if issued else datetime.now().strftime('%B %d, %Y')
    
    return render_template('certificate.html',
        student_name=cert['full_name'] or cert['username'],
        course_name='Environmental Awareness & Sustainability',
        completion_date=completion_date,
        certificate_id=cert['certificate_id']
    )

@app.route('/download_certificate/<filename>')
def download_certificate(filename):
    if 'user_id' not in session or session['role'] != 'student':
        return redirect('/login')
    
    return send_from_directory('certificates', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
