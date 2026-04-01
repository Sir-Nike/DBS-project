-- =============================================================
-- College Quiz Management System
-- schema.sql
-- Run this entire file in MySQL Workbench once to set up the DB
-- =============================================================

DROP DATABASE IF EXISTS quiz_db;
CREATE DATABASE quiz_db;
USE quiz_db;

-- Department
CREATE TABLE Department (
    department_id   INT          AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE
);

-- Teacher (login ID = staff_id)
CREATE TABLE Teacher (
    teacher_id    INT         AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    staff_id      VARCHAR(20)  NOT NULL UNIQUE,
    password      VARCHAR(50)  NOT NULL,
    department_id INT          NOT NULL,
    FOREIGN KEY (department_id) REFERENCES Department(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Student (login ID = roll_number)
CREATE TABLE Student (
    student_id    INT          AUTO_INCREMENT PRIMARY KEY,
    roll_number   VARCHAR(20)  NOT NULL UNIQUE,
    name          VARCHAR(100) NOT NULL,
    password      VARCHAR(50)  NOT NULL,
    department_id INT          NOT NULL,
    FOREIGN KEY (department_id) REFERENCES Department(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Subject
CREATE TABLE Subject (
    subject_id    INT         AUTO_INCREMENT PRIMARY KEY,
    subject_name  VARCHAR(100) NOT NULL,
    subject_code  VARCHAR(20)  NOT NULL UNIQUE,
    semester      INT          NOT NULL,
    department_id INT          NOT NULL,
    FOREIGN KEY (department_id) REFERENCES Department(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Quiz
CREATE TABLE Quiz (
    quiz_id           INT          AUTO_INCREMENT PRIMARY KEY,
    quiz_title        VARCHAR(150) NOT NULL,
    duration_minutes  INT          NOT NULL,
    total_marks       INT          NOT NULL,
    quiz_date         DATE         NOT NULL,
    results_published BOOLEAN      NOT NULL DEFAULT FALSE,
    subject_id        INT          NOT NULL,
    created_by        INT          NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (created_by) REFERENCES Teacher(teacher_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Question
CREATE TABLE Question (
    question_id   INT  AUTO_INCREMENT PRIMARY KEY,
    question_text TEXT NOT NULL,
    question_type ENUM('MCQ','TrueFalse') NOT NULL,
    marks         INT  NOT NULL,
    quiz_id       INT  NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES Quiz(quiz_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Option
CREATE TABLE `Option` (
    option_id   INT          AUTO_INCREMENT PRIMARY KEY,
    option_text VARCHAR(255) NOT NULL,
    is_correct  BOOLEAN      NOT NULL DEFAULT FALSE,
    question_id INT          NOT NULL,
    FOREIGN KEY (question_id) REFERENCES Question(question_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- QuizAttempt
CREATE TABLE QuizAttempt (
    attempt_id      INT      AUTO_INCREMENT PRIMARY KEY,
    submission_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_score     INT      NOT NULL DEFAULT 0,
    quiz_id         INT      NOT NULL,
    student_id      INT      NOT NULL,
    FOREIGN KEY (quiz_id)    REFERENCES Quiz(quiz_id)    ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE KEY unique_attempt (quiz_id, student_id)
);

-- StudentAnswer
CREATE TABLE StudentAnswer (
    answer_id          INT     AUTO_INCREMENT PRIMARY KEY,
    is_correct         BOOLEAN NOT NULL DEFAULT FALSE,
    attempt_id         INT     NOT NULL,
    question_id        INT     NOT NULL,
    selected_option_id INT     NOT NULL,
    FOREIGN KEY (attempt_id)         REFERENCES QuizAttempt(attempt_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (question_id)        REFERENCES Question(question_id)   ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (selected_option_id) REFERENCES `Option`(option_id)    ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Enrollment
CREATE TABLE Enrollment (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id    INT NOT NULL,
    subject_id    INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY unique_enrollment (student_id, subject_id)
);

-- =============================================================
-- SEED DATA
-- =============================================================

-- 8 Departments
INSERT INTO Department (department_name) VALUES
    ('Computer and Communication Engineering'),
    ('Computer Science Engineering'),
    ('Computer Science Engineering with AIML'),
    ('Mechanical Engineering'),
    ('Electrical and Electronics Engineering'),
    ('Chemical Engineering'),
    ('Industrial Engineering'),
    ('Mechatronics Engineering');

-- Teachers
INSERT INTO Teacher (name, staff_id, password, department_id) VALUES
    ('Dr. Ramesh Kumar', 'CCE101', 'teacher123', 1),
    ('Prof. Sunita Rao', 'CSE101', 'teacher456', 2);

-- Students
INSERT INTO Student (roll_number, name, password, department_id) VALUES
    ('240953194', 'Ankitha',         'student123', 1),
    ('240953382', 'Arnav Varshney',  'student456', 1),
    ('240953148', 'Shreeniketh E R', 'student789', 1),
    ('240953001', 'Test Student',    'test123',    1);

-- Subject
INSERT INTO Subject (subject_name, subject_code, semester, department_id) VALUES
    ('Database Systems', 'CCE2212', 4, 1);

-- Quiz
INSERT INTO Quiz (quiz_title, duration_minutes, total_marks, quiz_date, results_published, subject_id, created_by) VALUES
    ('DBS Unit 1 Quiz', 15, 10, CURDATE(), FALSE, 1, 1);

-- Q1 MCQ
INSERT INTO Question (question_text, question_type, marks, quiz_id) VALUES ('Which of the following is a DDL command?', 'MCQ', 2, 1);
INSERT INTO `Option` (option_text, is_correct, question_id) VALUES ('SELECT',FALSE,1),('INSERT',FALSE,1),('CREATE',TRUE,1),('UPDATE',FALSE,1);

-- Q2 MCQ
INSERT INTO Question (question_text, question_type, marks, quiz_id) VALUES ('Which normal form eliminates transitive dependencies?', 'MCQ', 2, 1);
INSERT INTO `Option` (option_text, is_correct, question_id) VALUES ('1NF',FALSE,2),('2NF',FALSE,2),('3NF',TRUE,2),('BCNF',FALSE,2);

-- Q3 MCQ
INSERT INTO Question (question_text, question_type, marks, quiz_id) VALUES ('A foreign key is used to:', 'MCQ', 2, 1);
INSERT INTO `Option` (option_text, is_correct, question_id) VALUES
    ('Uniquely identify a record in its own table',FALSE,3),
    ('Link two tables together',TRUE,3),
    ('Encrypt sensitive data',FALSE,3),
    ('Speed up queries',FALSE,3);

-- Q4 TrueFalse
INSERT INTO Question (question_text, question_type, marks, quiz_id) VALUES ('SQL stands for Structured Query Language.', 'TrueFalse', 2, 1);
INSERT INTO `Option` (option_text, is_correct, question_id) VALUES ('True',TRUE,4),('False',FALSE,4);

-- Q5 TrueFalse
INSERT INTO Question (question_text, question_type, marks, quiz_id) VALUES ('A primary key can contain NULL values.', 'TrueFalse', 2, 1);
INSERT INTO `Option` (option_text, is_correct, question_id) VALUES ('True',FALSE,5),('False',TRUE,5);

-- Enrollments
INSERT INTO Enrollment (student_id, subject_id) VALUES (1,1),(2,1),(3,1),(4,1);

-- =============================================================
-- VERIFY
-- =============================================================
SELECT 'Department'    AS `Table`, COUNT(*) AS `Rows` FROM Department
UNION ALL SELECT 'Teacher',      COUNT(*) FROM Teacher
UNION ALL SELECT 'Student',      COUNT(*) FROM Student
UNION ALL SELECT 'Subject',      COUNT(*) FROM Subject
UNION ALL SELECT 'Quiz',         COUNT(*) FROM Quiz
UNION ALL SELECT 'Question',     COUNT(*) FROM Question
UNION ALL SELECT 'Option',       COUNT(*) FROM `Option`
UNION ALL SELECT 'QuizAttempt',  COUNT(*) FROM QuizAttempt
UNION ALL SELECT 'StudentAnswer',COUNT(*) FROM StudentAnswer
UNION ALL SELECT 'Enrollment',   COUNT(*) FROM Enrollment;
