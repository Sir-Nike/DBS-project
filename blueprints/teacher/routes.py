from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import query, execute

teacher_bp = Blueprint('teacher', __name__)


# --- Auth guard ---
def teacher_required():
    if 'user_id' not in session or session.get('role') != 'teacher':
        flash('Please login as a teacher.', 'error')
        return redirect(url_for('auth.login'))
    return None


# =============================================================
# DASHBOARD
# =============================================================
@teacher_bp.route('/dashboard')
def dashboard():
    guard = teacher_required()
    if guard: return guard

    teacher_id = session['user_id']

    quizzes = query("""
        SELECT q.quiz_id, q.quiz_title, q.duration_minutes, q.total_marks,
               q.quiz_date, q.results_published,
               s.subject_name, s.subject_code,
               COUNT(qa.attempt_id) AS attempt_count
        FROM Quiz q
        JOIN Subject s ON q.subject_id = s.subject_id
        LEFT JOIN QuizAttempt qa ON q.quiz_id = qa.quiz_id
        WHERE q.created_by = %s
        GROUP BY q.quiz_id
        ORDER BY q.quiz_date DESC
    """, (teacher_id,))

    return render_template('teacher/dashboard.html', quizzes=quizzes)


# =============================================================
# CREATE QUIZ
# =============================================================
@teacher_bp.route('/quiz/create', methods=['GET', 'POST'])
def create_quiz():
    guard = teacher_required()
    if guard: return guard

    subjects = query("SELECT subject_id, subject_name, subject_code FROM Subject")

    if request.method == 'POST':
        title    = request.form.get('quiz_title', '').strip()
        duration = request.form.get('duration_minutes', '').strip()
        marks    = request.form.get('total_marks', '').strip()
        date     = request.form.get('quiz_date', '').strip()
        subj_id  = request.form.get('subject_id', '').strip()

        if not all([title, duration, marks, date, subj_id]):
            flash('All fields are required.', 'error')
            return render_template('teacher/create_quiz.html', subjects=subjects)

        quiz_id = execute("""
            INSERT INTO Quiz (quiz_title, duration_minutes, total_marks, quiz_date, subject_id, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, int(duration), int(marks), date, int(subj_id), session['user_id']))

        flash(f'Quiz "{title}" created! Now add questions.', 'success')
        return redirect(url_for('teacher.add_question', quiz_id=quiz_id))

    return render_template('teacher/create_quiz.html', subjects=subjects)


# =============================================================
# ADD QUESTIONS
# =============================================================
@teacher_bp.route('/quiz/<int:quiz_id>/add-question', methods=['GET', 'POST'])
def add_question(quiz_id):
    guard = teacher_required()
    if guard: return guard

    quiz = query("""
        SELECT quiz_id, quiz_title, total_marks FROM Quiz
        WHERE quiz_id = %s AND created_by = %s
    """, (quiz_id, session['user_id']), one=True)

    if not quiz:
        flash('Quiz not found.', 'error')
        return redirect(url_for('teacher.dashboard'))

    questions = query("""
        SELECT q.question_id, q.question_text, q.question_type, q.marks,
               COUNT(o.option_id) AS option_count
        FROM Question q
        LEFT JOIN `Option` o ON q.question_id = o.question_id
        WHERE q.quiz_id = %s
        GROUP BY q.question_id
        ORDER BY q.question_id
    """, (quiz_id,))

    if request.method == 'POST':
        q_text  = request.form.get('question_text', '').strip()
        q_type  = request.form.get('question_type', '').strip()
        q_marks = request.form.get('marks', '').strip()
        
        print(f"DEBUG: text={q_text}, type={q_type}, marks={q_marks}, tf={request.form.get('correct_tf')}")


        if not all([q_text, q_type, q_marks]):
            flash('All question fields are required.', 'error')
            return render_template('teacher/add_question.html', quiz=quiz, questions=questions)

        q_id = execute("""
            INSERT INTO Question (question_text, question_type, marks, quiz_id)
            VALUES (%s, %s, %s, %s)
        """, (q_text, q_type, int(q_marks), quiz_id))

        if q_type == 'TrueFalse':
            correct = request.form.get('correct_tf')
            execute("INSERT INTO `Option` (option_text, is_correct, question_id) VALUES ('True', %s, %s)",
                    (correct == 'True', q_id))
            execute("INSERT INTO `Option` (option_text, is_correct, question_id) VALUES ('False', %s, %s)",
                    (correct == 'False', q_id))
        else:
            correct = request.form.get('correct_mcq')
            for i in range(1, 5):
                opt_text = request.form.get(f'option_{i}', '').strip()
                if opt_text:
                    execute("""
                        INSERT INTO `Option` (option_text, is_correct, question_id)
                        VALUES (%s, %s, %s)
                    """, (opt_text, str(i) == correct, q_id))

        flash('Question added!', 'success')
        return redirect(url_for('teacher.add_question', quiz_id=quiz_id))

    return render_template('teacher/add_question.html', quiz=quiz, questions=questions)


# =============================================================
# DELETE QUESTION
# =============================================================
@teacher_bp.route('/question/<int:question_id>/delete', methods=['POST'])
def delete_question(question_id):
    guard = teacher_required()
    if guard: return guard

    q = query("SELECT quiz_id FROM Question WHERE question_id = %s", (question_id,), one=True)
    if q:
        execute("DELETE FROM Question WHERE question_id = %s", (question_id,))
        flash('Question deleted.', 'success')
        return redirect(url_for('teacher.add_question', quiz_id=q['quiz_id']))

    flash('Question not found.', 'error')
    return redirect(url_for('teacher.dashboard'))


# =============================================================
# PUBLISH / UNPUBLISH RESULTS
# =============================================================
@teacher_bp.route('/quiz/<int:quiz_id>/publish', methods=['POST'])
def publish_results(quiz_id):
    guard = teacher_required()
    if guard: return guard

    quiz = query("SELECT results_published FROM Quiz WHERE quiz_id = %s AND created_by = %s",
                 (quiz_id, session['user_id']), one=True)

    if not quiz:
        flash('Quiz not found.', 'error')
        return redirect(url_for('teacher.dashboard'))

    new_state = not quiz['results_published']
    execute("UPDATE Quiz SET results_published = %s WHERE quiz_id = %s", (new_state, quiz_id))

    msg = 'Results published!' if new_state else 'Results unpublished.'
    flash(msg, 'success')
    return redirect(url_for('teacher.view_results', quiz_id=quiz_id))


# =============================================================
# VIEW RESULTS
# =============================================================
@teacher_bp.route('/quiz/<int:quiz_id>/results')
def view_results(quiz_id):
    guard = teacher_required()
    if guard: return guard

    quiz = query("""
        SELECT q.quiz_id, q.quiz_title, q.total_marks, q.results_published,
               s.subject_name
        FROM Quiz q
        JOIN Subject s ON q.subject_id = s.subject_id
        WHERE q.quiz_id = %s AND q.created_by = %s
    """, (quiz_id, session['user_id']), one=True)

    if not quiz:
        flash('Quiz not found.', 'error')
        return redirect(url_for('teacher.dashboard'))

    attempts = query("""
        SELECT st.name AS student_name, st.roll_number,
               qa.total_score, qa.submission_time, qa.attempt_id
        FROM QuizAttempt qa
        JOIN Student st ON qa.student_id = st.student_id
        WHERE qa.quiz_id = %s
        ORDER BY qa.total_score DESC
    """, (quiz_id,))

    return render_template('teacher/results.html', quiz=quiz, attempts=attempts)


# =============================================================
# CREATE SUBJECT
# =============================================================
@teacher_bp.route('/subject/create', methods=['GET', 'POST'])
def create_subject():
    guard = teacher_required()
    if guard: return guard

    teacher = query("""
        SELECT t.department_id, d.department_name
        FROM Teacher t
        JOIN Department d ON t.department_id = d.department_id
        WHERE t.teacher_id = %s
    """, (session['user_id'],), one=True)

    if request.method == 'POST':
        subject_name = request.form.get('subject_name', '').strip()
        subject_code = request.form.get('subject_code', '').strip()
        semester     = request.form.get('semester', '').strip()

        if not all([subject_name, subject_code, semester]):
            flash('All fields are required.', 'error')
            return render_template('teacher/create_subject.html', teacher=teacher)

        existing = query(
            "SELECT subject_id FROM Subject WHERE subject_code = %s", (subject_code,), one=True
        )
        if existing:
            flash('Subject code already exists.', 'error')
            return render_template('teacher/create_subject.html', teacher=teacher)

        execute("""
            INSERT INTO Subject (subject_name, subject_code, semester, department_id)
            VALUES (%s, %s, %s, %s)
        """, (subject_name, subject_code, int(semester), teacher['department_id']))

        flash(f'Subject "{subject_name}" created!', 'success')
        return redirect(url_for('teacher.dashboard'))

    return render_template('teacher/create_subject.html', teacher=teacher)