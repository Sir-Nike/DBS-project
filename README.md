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

## Local Setup

### 1. Prerequisites
- Python 3.10 or higher
- MySQL Server running on localhost
- MySQL Workbench (recommended)
- uv installed (`pip install uv`)

### 2. Install dependencies
```bash
cd "DBS project"
uv sync
```

### 3. Set up the database
- Open MySQL Workbench → connect to localhost
- File → Open SQL Script → select `schema.sql`
- Click ⚡ Execute
- Verify row counts match expected values (see below)

### 4. Configure environment
Edit `.env`:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=quiz_db
SECRET_KEY=quizapp_secret_change_this_later
```

### 5. Run the app
```bash
uv run app.py
```

Open: `http://127.0.0.1:5000`

### 6. LAN access (hotspot/same network)
Share your hotspot → teammates open:
```
http://<your-ip>:5000
```
Your IP is shown in the terminal when Flask starts.

---

## Cloud Deployment (Railway)

### 1. Push code to GitHub
```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/yourusername/repo-name.git
git push -u origin main
```
Make sure `.env` is NOT committed — it's covered by `.gitignore`.

### 2. Create Railway account
Go to [railway.app](https://railway.app) → login with GitHub.

### 3. Add MySQL service
New Project → Add MySQL → click MySQL service → Variables tab → note down all credentials.

### 4. Enable public networking on MySQL
MySQL service → Settings → Public Networking → Generate Domain.
You'll get a hostname like `hopper.proxy.rlwy.net` and a port like `55255`.

### 5. Run schema on Railway MySQL
Open MySQL Workbench → New Connection:
- **Hostname:** `hopper.proxy.rlwy.net` (your public hostname)
- **Port:** your public port (e.g. `55255`)
- **Username:** `MYSQLUSER` value from Railway Variables
- **Password:** `MYSQLPASSWORD` value from Railway Variables

Connect → run this first:
```sql
USE railway;
```
Then select everything in `schema.sql` **from `CREATE TABLE Department` onwards**
(skip the DROP/CREATE DATABASE lines at the top) and execute.

### 6. Deploy Flask app
Railway dashboard → + New → GitHub Repo → select your repo.

### 7. Set environment variables on Flask service
Railway → Flask service → Variables tab → add:
```
DB_HOST=mysql.railway.internal
DB_PORT=3306
DB_USER=<MYSQLUSER from Railway>
DB_PASSWORD=<MYSQLPASSWORD from Railway>
DB_NAME=railway
SECRET_KEY=quizapp_secret_change_this_later
```
Note: use `mysql.railway.internal` (internal hostname) for Flask→MySQL
communication within Railway. The public hostname is only for Workbench access.

### 8. Get your public URL
Flask service → Settings → Networking → Generate Domain.
Share this URL — accessible from anywhere without any hotspot.

### 9. Making updates
```bash
git add .
git commit -m "describe change"
git push
```
Railway auto-redeploys on every push.

---

## Expected DB Row Counts (after schema.sql)

| Table         | Rows |
|---------------|------|
| Department    | 8    |
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

### Teachers (login with Staff ID)
| Name             | Staff ID | Password   |
|------------------|----------|------------|
| Dr. Ramesh Kumar | CCE101   | teacher123 |
| Prof. Sunita Rao | CSE101   | teacher456 |

### Students (login with Roll Number)
| Name            | Roll Number | Password   |
|-----------------|-------------|------------|
| Ankitha         | 240953194   | student123 |
| Arnav Varshney  | 240953382   | student456 |
| Shreeniketh E R | 240953148   | student789 |
| Test Student    | 240953001   | test123    |

All seed students are enrolled in **Database Systems (CCE2212)**.

---

## Features

### Teacher
- Register / Login with Staff ID
- Create subjects (restricted to own department)
- Create quizzes with title, subject, duration, marks, date
- Add MCQ and True/False questions
- Delete questions
- View all student attempts with scores
- Publish / unpublish results

### Student
- Register / Login with Roll Number
- Self-enroll in subjects at registration
- View quizzes for enrolled subjects only
- Take time-bound quizzes (JS timer, auto-submit on timeout)
- Questions shuffled randomly per attempt
- View results (score + answer breakdown after teacher publishes)

---

## Project Structure
```
DBS project/
├── app.py                      # Flask app factory + entry point
├── config.py                   # Loads .env variables
├── db.py                       # MySQL connection + query helpers
├── schema.sql                  # Full DB schema + seed data
├── .env                        # DB credentials (never commit)
├── .gitignore
├── pyproject.toml              # uv dependencies
├── Procfile                    # For cloud deployment
├── README.md
├── blueprints/
│   ├── auth/routes.py          # /login, /logout, /register
│   ├── teacher/routes.py       # Teacher dashboard + quiz + subject management
│   └── student/routes.py       # Student dashboard + quiz taking
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── teacher/
│   │   ├── dashboard.html
│   │   ├── create_quiz.html
│   │   ├── create_subject.html
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

## Notes
- Passwords stored as plain text (lab project scope)
- Students can only attempt each quiz once (enforced at DB + app level)
- Results hidden from students until teacher publishes them
- Timer runs in browser JS, auto-submits on expiry
- Internal Railway hostname (`mysql.railway.internal`) used for Flask→MySQL
- Public hostname (`hopper.proxy.rlwy.net`) used only for Workbench access
