from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import query, execute

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session['role'] == 'teacher':
        return redirect(url_for('teacher.dashboard'))
    return redirect(url_for('student.dashboard'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        login_id = request.form.get('login_id', '').strip()
        password = request.form.get('password', '').strip()

        if not login_id or not password:
            flash('Please enter your ID and password.', 'error')
            return render_template('login.html')

        # Check Student (roll_number)
        student = query(
            "SELECT student_id, name, password FROM Student WHERE roll_number = %s",
            (login_id,), one=True
        )
        if student and student['password'] == password:
            session['user_id'] = student['student_id']
            session['name']    = student['name']
            session['role']    = 'student'
            flash(f"Welcome, {student['name']}!", 'success')
            return redirect(url_for('student.dashboard'))

        # Check Teacher (staff_id)
        teacher = query(
            "SELECT teacher_id, name, password FROM Teacher WHERE staff_id = %s",
            (login_id,), one=True
        )
        if teacher and teacher['password'] == password:
            session['user_id'] = teacher['teacher_id']
            session['name']    = teacher['name']
            session['role']    = 'teacher'
            flash(f"Welcome, {teacher['name']}!", 'success')
            return redirect(url_for('teacher.dashboard'))

        flash('Invalid ID or password.', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('auth.index'))

    departments = query("SELECT department_id, department_name FROM Department")
    subjects    = query("SELECT subject_id, subject_name, subject_code FROM Subject")

    if request.method == 'POST':
        role     = request.form.get('role', '').strip()
        name     = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()
        dept_id  = request.form.get('department_id', '').strip()

        if not all([role, name, password, dept_id]):
            flash('All fields are required.', 'error')
            return render_template('register.html', departments=departments, subjects=subjects)

        if role == 'student':
            roll = request.form.get('roll_number', '').strip()
            if not roll:
                flash('Roll number is required.', 'error')
                return render_template('register.html', departments=departments, subjects=subjects)

            existing = query(
                "SELECT student_id FROM Student WHERE roll_number = %s", (roll,), one=True
            )
            if existing:
                flash('Roll number already registered.', 'error')
                return render_template('register.html', departments=departments, subjects=subjects)

            student_id = execute("""
                INSERT INTO Student (roll_number, name, password, department_id)
                VALUES (%s, %s, %s, %s)
            """, (roll, name, password, int(dept_id)))

            selected_subjects = request.form.getlist('subjects')
            for subj_id in selected_subjects:
                execute("INSERT IGNORE INTO Enrollment (student_id, subject_id) VALUES (%s, %s)",
                        (student_id, int(subj_id)))

            flash('Account created! Login with your roll number.', 'success')
            return redirect(url_for('auth.login'))

        elif role == 'teacher':
            staff_id = request.form.get('staff_id', '').strip()
            if not staff_id:
                flash('Staff ID is required.', 'error')
                return render_template('register.html', departments=departments, subjects=subjects)

            existing = query(
                "SELECT teacher_id FROM Teacher WHERE staff_id = %s", (staff_id,), one=True
            )
            if existing:
                flash('Staff ID already registered.', 'error')
                return render_template('register.html', departments=departments, subjects=subjects)

            execute("""
                INSERT INTO Teacher (name, staff_id, password, department_id)
                VALUES (%s, %s, %s, %s)
            """, (name, staff_id, password, int(dept_id)))

            flash('Teacher account created! Login with your staff ID.', 'success')
            return redirect(url_for('auth.login'))

        else:
            flash('Invalid role.', 'error')

    return render_template('register.html', departments=departments, subjects=subjects)