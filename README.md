# CCE Quiz Portal
**College Quiz Management System**
CSE 2212 – Database Systems Lab Mini Project
Team: Ankitha (240953194), Arnav Varshney (240953382), Shreeniketh E R (240953148)
CCE B — MIT Manipal

---

## Tech Stack
- **Backend:** Python 3.10+ with Flask
- **Database:** MySQL
- **Frontend:** Jinja2 templates + HTML/CSS + vanilla JS
- **Package manager:** uv

---

## Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher
- MySQL Server running on localhost
- MySQL Workbench (recommended)
- uv installed (`pip install uv`)

### 2. Clone / Download the project
```bash
cd "DBS project"
```

### 3. Install dependencies
```bash
uv sync
```

### 4. Set up the database
- Open MySQL Workbench
- Connect to localhost
- Open `schema.sql` → File → Open SQL Script
- Click ⚡ Execute
- Verify row counts match expected values (see below)

### 5. Configure environment
Edit `.env` and fill in your MySQL root password:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=quiz_db
SECRET_KEY=quizapp_secret_change_this_later
```

### 6. Run the app
```bash
uv run app.py
```

Open your browser at: `http://127.0.0.1:5000`

### 7. LAN access (hotspot/same network)
Share your hotspot and tell teammates to open:
```
http://<your-ip>:5000
```
Your IP is shown in the terminal when Flask starts.

---

## Expected DB Row Counts (after schema.sql)

| Table         | Rows |
|---------------|------|
| Department    | 2    |
| Teacher       | 2    |
| Student       | 4    |
| Subject       | 1    |
| Quiz          | 1    |
| Question      | 5    |
| Option        | 16   |
| QuizAttempt   | 0    |
| StudentAnswer | 0    |
| Enrollment    | 4    |

---

## Pre-seeded Accounts

### Teachers
| Name             | Staff ID | Password    |
|------------------|----------|-------------|
| Dr. Ramesh Kumar | CCE101   | teacher123  |
| Prof. Sunita Rao | CSE101   | teacher456  |

### Students
| Name            | Login ID    | Password   | Roll Number |
|-----------------|-------------|------------|-------------|
| Ankitha         | 240953194   | student123 | 240953194   |
| Arnav Varshney  | 240953382   | student456 | 240953382   |
| Shreeniketh E R | 240953148   | student789 | 240953148   |
| Test Student    | 240953001   | test123    | 240953001   |

All seed students are enrolled in **Database Systems (CCE2212)**.

---

## Features

### Teacher
- Register / Login
- Create quizzes with title, subject, duration, marks, date
- Add MCQ and True/False questions
- Delete questions
- View all student attempts with scores
- Publish / unpublish results

### Student
- Register / Login (self-enroll in subjects at registration)
- View quizzes for enrolled subjects only
- Take time-bound quizzes (auto-submit on timeout)
- Questions shuffled randomly per attempt
- View results (score + answer breakdown shown after teacher publishes)

---

## Project Structure
```
DBS project/
├── app.py               # Flask app factory + entry point
├── config.py            # Loads .env variables
├── db.py                # MySQL connection + query helpers
├── schema.sql           # Full DB schema + seed data
├── .env                 # DB credentials (never commit)
├── .gitignore
├── pyproject.toml       # uv dependencies
├── Procfile             # For cloud deployment (Render/Railway)
├── README.md
├── blueprints/
│   ├── auth/routes.py      # /login, /logout, /register
│   ├── teacher/routes.py   # Teacher dashboard + quiz management
│   └── student/routes.py   # Student dashboard + quiz taking
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── teacher/
│   │   ├── dashboard.html
│   │   ├── create_quiz.html
│   │   ├── add_question.html
│   │   └── results.html
│   └── student/
│       ├── dashboard.html
│       ├── take_quiz.html
│       └── result.html
└── static/
    └── css/
        └── style.css
```

---

## Cloud Deployment (Optional — Render/Railway)
1. Push code to GitHub (make sure `.env` is in `.gitignore`)
2. Create a new Web Service on Render, connect your repo
3. Set environment variables (same as `.env`) in Render dashboard
4. Deploy — `Procfile` handles the rest

---

## Notes
- Passwords are stored as plain text (lab project scope)
- A student can only attempt each quiz once (enforced at DB level)
- Results are hidden from students until teacher publishes them
- Timer runs in the browser (JS) and auto-submits on expiry