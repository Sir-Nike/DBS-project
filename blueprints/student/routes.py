from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import query, execute
import random
import pymysql

student_bp = Blueprint('student', __name__)


# --- Auth guard ---
def student_required():
    if 'user_id' not in session or session.get('role') != 'student':
        flash('Please login as a student.', 'error')
        return redirect(url_for('auth.login'))
    return None


# =============================================================
# DASHBOARD
# =============================================================
@student_bp.route('/dashboard')
def dashboard():
    guard = student_required()
    if guard: return guard

    student_id = session['user_id']

    # Only quizzes for subjects this student is enrolled in
    quizzes = query("""
        SELECT q.quiz_id, q.quiz_title, q.duration_minutes, q.total_marks,
               q.quiz_date, q.results_published,
               s.subject_name, s.subject_code,
               qa.attempt_id, qa.total_score
        FROM Quiz q
        JOIN Subject s ON q.subject_id = s.subject_id
        JOIN Enrollment e ON e.subject_id = q.subject_id AND e.student_id = %s
        LEFT JOIN QuizAttempt qa ON q.quiz_id = qa.quiz_id AND qa.student_id = %s
        ORDER BY q.quiz_date DESC
    """, (student_id, student_id))

    return render_template('student/dashboard.html', quizzes=quizzes)


# =============================================================
# TAKE QUIZ
# =============================================================
@student_bp.route('/quiz/<int:quiz_id>/take')
def take_quiz(quiz_id):
    guard = student_required()
    if guard: return guard

    student_id = session['user_id']

    # Check already attempted
    existing = query("""
        SELECT attempt_id FROM QuizAttempt
        WHERE quiz_id = %s AND student_id = %s
    """, (quiz_id, student_id), one=True)

    if existing:
        flash('You have already attempted this quiz.', 'error')
        return redirect(url_for('student.dashboard'))

    # Get quiz details
    quiz = query("""
        SELECT q.quiz_id, q.quiz_title, q.duration_minutes, q.total_marks,
               s.subject_name
        FROM Quiz q
        JOIN Subject s ON q.subject_id = s.subject_id
        WHERE q.quiz_id = %s
    """, (quiz_id,), one=True)

    if not quiz:
        flash('Quiz not found.', 'error')
        return redirect(url_for('student.dashboard'))

    # Get questions with options
    questions = query("""
        SELECT question_id, question_text, question_type, marks
        FROM Question
        WHERE quiz_id = %s
        ORDER BY question_id
    """, (quiz_id,))

    for q in questions:
        q['options'] = query("""
            SELECT option_id, option_text
            FROM `Option`
            WHERE question_id = %s
        """, (q['question_id'],))

    # Shuffle question order per attempt
    random.shuffle(questions)

    return render_template('student/take_quiz.html', quiz=quiz, questions=questions)


# =============================================================
# SUBMIT QUIZ
# =============================================================
@student_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    guard = student_required()
    if guard: return guard

    student_id = session['user_id']

    # Check already attempted
    existing = query("""
        SELECT attempt_id FROM QuizAttempt
        WHERE quiz_id = %s AND student_id = %s
    """, (quiz_id, student_id), one=True)

    if existing:
        flash('You have already attempted this quiz.', 'error')
        return redirect(url_for('student.dashboard'))

    # Get all questions for this quiz
    questions = query("""
        SELECT question_id, marks FROM Question WHERE quiz_id = %s
    """, (quiz_id,))

    total_score = 0

    try:
        # Create attempt first (score=0, we'll calculate below)
        attempt_id = execute("""
            INSERT INTO QuizAttempt (total_score, quiz_id, student_id)
            VALUES (0, %s, %s)
        """, (quiz_id, student_id))

        # Process each answer
        for q in questions:
            q_id = q['question_id']
            selected_option_id = request.form.get(f'question_{q_id}')

            if not selected_option_id:
                continue  # skipped question

            selected_option_id = int(selected_option_id)

            # Check if correct
            option = query("""
                SELECT is_correct FROM `Option`
                WHERE option_id = %s AND question_id = %s
            """, (selected_option_id, q_id), one=True)

            is_correct = option and option['is_correct']
            if is_correct:
                total_score += q['marks']

            execute("""
                INSERT INTO StudentAnswer (is_correct, attempt_id, question_id, selected_option_id)
                VALUES (%s, %s, %s, %s)
            """, (is_correct, attempt_id, q_id, selected_option_id))

        # Update total score
        execute("""
            UPDATE QuizAttempt SET total_score = %s WHERE attempt_id = %s
        """, (total_score, attempt_id))

        flash(f'Quiz submitted! You scored {total_score} marks.', 'success')
        return redirect(url_for('student.view_result', attempt_id=attempt_id))

    except pymysql.IntegrityError:
        flash('You have already attempted this quiz.', 'error')
        return redirect(url_for('student.dashboard'))


# =============================================================
# VIEW RESULT
# =============================================================
@student_bp.route('/result/<int:attempt_id>')
def view_result(attempt_id):
    guard = student_required()
    if guard: return guard

    student_id = session['user_id']

    # Get attempt — must belong to this student
    attempt = query("""
        SELECT qa.attempt_id, qa.total_score, qa.submission_time,
               q.quiz_title, q.total_marks, q.results_published,
               s.subject_name
        FROM QuizAttempt qa
        JOIN Quiz q ON qa.quiz_id = q.quiz_id
        JOIN Subject s ON q.subject_id = s.subject_id
        WHERE qa.attempt_id = %s AND qa.student_id = %s
    """, (attempt_id, student_id), one=True)

    if not attempt:
        flash('Result not found.', 'error')
        return redirect(url_for('student.dashboard'))

    # Only show detailed breakdown if results published
    answers = []
    if attempt['results_published']:
        answers = query("""
            SELECT sa.is_correct,
                   q.question_text, q.question_type, q.marks,
                   sel.option_text AS selected_text,
                   correct_opt.option_text AS correct_text
            FROM StudentAnswer sa
            JOIN Question q ON sa.question_id = q.question_id
            JOIN `Option` sel ON sa.selected_option_id = sel.option_id
            JOIN `Option` correct_opt ON correct_opt.question_id = q.question_id
                                     AND correct_opt.is_correct = TRUE
            WHERE sa.attempt_id = %s
            ORDER BY q.question_id
        """, (attempt_id,))

    return render_template('student/result.html', attempt=attempt, answers=answers)