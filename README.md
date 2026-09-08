# AI HR RECRUITMENT ASSISTANT

An enterprise-grade, production-style full-stack HR recruitment management web application built with **Flask**, **MySQL**, **Bootstrap 5**, **Chart.js**, and an intelligent **AI/NLP Service Layer**.

The system streamlines the entire hiring lifecycle: posting job descriptions, parsing PDF/DOCX resumes, comparing candidates against job criteria using a transparent 5-factor scoring model, ranking applicants on interactive leaderboards, identifying skill gaps, generating personalized interview questions, and recording structured competency evaluations.

---

## 🌟 Key Features

1. **Authentication & Session Security**:
   - Secure HR user registration and session-based login.
   - Industry-standard password hashing via `Werkzeug` (scrypt/pbkdf2).
   - Protected routes with `@login_required` decorator.

2. **Executive HR Dashboard**:
   - 6 Live Metric KPI Cards: Total Jobs, Active Openings, Total Candidates, Resumes Parsed, Shortlisted Candidates, Interviews Completed.
   - Interactive data visualizations with **Chart.js**:
     - *Applicants per Job* (Bar Chart)
     - *Match Score Distribution* (Doughnut Chart)
     - *Recruitment Status Pipeline* (Pie Chart)
   - Real-time feeds of recent requisitions, new talent, top matching candidates, and upcoming interviews.

3. **Job Requisition Management**:
   - Full CRUD: Create, View, Edit, and Delete requisitions.
   - Fields: Title, Department, Location, Type (Full Time, Part Time, Contract, Internship), Experience, Salary Range, Description, Education, Responsibilities.
   - Automatic **AI JD Skill Extractor**: extracts required & preferred skills directly from description text.

4. **Intelligent Resume Parser (PDF & DOCX)**:
   - Drag-and-drop file upload with live progress bar and validation (16 MB limit).
   - High-fidelity text extraction using `pypdf` and `python-docx`.
   - Structured entity extraction: Contact info, Technical Skills (Languages, Frameworks, Databases, Tools), Experience, Education, Projects, Certifications, and an AI Executive Summary.

5. **Transparent 5-Factor Candidate Matching (Core Engine)**:
   - **Skills Match (50%)**: Exact match, partial/synonym overlap, and missing skills.
   - **Experience Match (20%)**: Candidate years vs. required years.
   - **Education Match (10%)**: Degree level and domain alignment.
   - **Project Relevance (10%)**: Portfolio tech stack overlap.
   - **Preferred Skills (10%)**: Bonus criteria matching.
   - Visual radial conic meter and individual progress bars.
   - Clear categorized badges: Matched (`✓`), Missing (`✗`), and Partial (`⚠`).
   - Ethical AI compliance: protected personal attributes are never used in scoring.

6. **Candidate Leaderboard & Ranking**:
   - Filterable candidate rankings for each job.
   - Recommendation categories based on score thresholds:
     - **Strong Match** (85% - 100%)
     - **Potential Match** (70% - 84%)
     - **Needs Review** (< 70%)
   - Prominent decision-support AI disclaimer ensuring recruiters maintain hiring authority.

7. **Personalized Interview Question Generator**:
   - Generates questions tailored to candidate projects and specific skill gaps from the JD.
   - 6 Categories: *Technical*, *Project-Based*, *Behavioral*, *Situational*, *Role-Specific*, and *Skill Gap*.
   - Configurable question counts: 5, 10, 15, or 20 questions with difficulty indicators (Easy, Medium, Hard).
   - One-click export to formatted `.txt` or printable view.

8. **Interview Management & 6-Dimension Evaluation**:
   - Schedule interview rounds (Technical, HR, Managerial, Final) with date, time, and interviewer.
   - Interactive evaluation scorecard rating 6 competencies on a 1-5 scale:
     1. Technical Skills
     2. Communication
     3. Problem Solving
     4. Project Knowledge
     5. Role Fit
     6. Confidence
   - Real-time overall score calculation and hiring recommendations (*Strongly Recommend*, *Recommend*, *Consider*, *Not Recommended*).

9. **Reports & CSV Data Export**:
   - Recruitment funnel conversion analytics.
   - One-click CSV export of candidate scores, interview evaluations, and hiring recommendations.

10. **Zero-Crash DEMO_MODE**:
    - Runs completely offline with built-in intelligent NLP and heuristics when `DEMO_MODE=true` or when no external API key is provided.
    - Zero-friction MySQL setup: if MySQL credentials are not yet configured, automatically activates local database store so the app is instantly testable.

---

## 🛠 Technology Stack

- **Backend**: Python 3.13, Flask 3.1, Flask-CORS, Werkzeug, python-dotenv
- **Database**: MySQL 8.0 (`mysql-connector-python`) with resilient local fallback engine
- **Document Processing**: `pypdf` (PDF extraction), `python-docx` (Word extraction)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons 1.11, Chart.js 4.4
- **AI/NLP**: Service abstraction supporting Gemini, OpenAI, Ollama, and deterministic offline heuristics

---

## 📁 Project Structure

```
ai_hr_recruitment/
├── app.py                     # Flask application factory and entry point
├── config.py                  # Environment and app configuration
├── database.py                # Database connection pooling & query helper (MySQL + fallback)
├── init_db.py                 # DB initialization script (creates schema and seed data)
├── requirements.txt           # Python dependencies
├── .env.example               # Template environment configuration
├── .env                       # Active environment configuration
├── .gitignore                 # Git ignore rules
├── README.md                  # Complete documentation
│
├── database/
│   ├── schema.sql             # 15 normalized tables with indexes & foreign keys
│   └── seed.sql               # Seed data for 3 HR users, 5 jobs, 10 candidates, etc.
│
├── routes/
│   ├── auth_routes.py         # Login, register, logout, profile, /api/me
│   ├── dashboard_routes.py    # Command center metrics and recent feeds
│   ├── job_routes.py          # Job CRUD and JD auto-extraction
│   ├── candidate_routes.py    # Candidate directory and profiles
│   ├── resume_routes.py       # PDF/DOCX upload and AI parsing
│   ├── matching_routes.py     # 5-factor matching and candidate ranking
│   ├── interview_routes.py    # Question generation, scheduling, evaluation
│   └── report_routes.py       # Analytics dashboard and CSV export
│
├── services/
│   ├── ai_service.py          # Unified AI service (Gemini/OpenAI/Ollama/Demo)
│   ├── resume_parser.py       # PDF/DOCX text extraction & entity recognition
│   ├── job_analyzer.py        # Structured skill & requirement extraction from JD
│   ├── matching_service.py    # Transparent 5-factor scoring engine
│   └── interview_service.py   # Contextual interview question generator
│
├── utils/
│   ├── security.py            # Password hashing and @login_required guard
│   ├── validators.py          # Email, password, and file validators
│   └── helpers.py             # Formatters, badges, and JSON responses
│
├── templates/                 # Modern Bootstrap 5 SaaS templates
│   ├── base.html              # Layout with responsive sidebar and topbar
│   ├── login.html             # Login with demo autofill buttons
│   ├── register.html          # Registration form
│   ├── dashboard.html         # 6 KPI cards, 3 Chart.js charts, recent tables
│   ├── jobs.html              # Job requisitions list with filters
│   ├── create_job.html        # Job creation with AI skill extraction
│   ├── edit_job.html          # Job edit form
│   ├── job_details.html       # Job overview and applicants list
│   ├── candidates.html        # Talent pool directory with sorting
│   ├── candidate_details.html # Candidate profile (skills, exp, matches, evals)
│   ├── resume_analyzer.html   # Drag & drop upload and live parsed cards
│   ├── matching.html          # Side-by-side comparator and radial dial
│   ├── ranking.html           # Candidate leaderboard
│   ├── interview_questions.html # Dynamic question generator with export
│   ├── interviews.html        # Scheduling pipeline
│   ├── evaluation.html        # 6-competency rating scorecard
│   ├── reports.html           # Analytics funnel and CSV export
│   ├── profile.html           # HR user settings
│   ├── 404.html, 413.html, 500.html # User-friendly error pages
│
├── static/
│   ├── css/style.css          # Custom SaaS design system
│   ├── js/                    # Client scripts (app.js, dashboard.js, etc.)
│   └── uploads/resumes/       # Secure folder for uploaded resumes
│
└── tests/
    ├── test_auth.py           # Password hashing and session tests
    ├── test_matching.py       # 5-factor scoring tests
    ├── test_resume_parser.py  # Text and entity extraction tests
    └── test_routes.py         # Flask endpoints and API tests
```

---

## 🚀 Windows PowerShell Quick Start Guide

Open **Windows PowerShell** in this project directory (`c:\Users\manju\OneDrive\Desktop\Anusha`):

### 1. Activate Virtual Environment
The virtual environment is already prepared in the project. Activate it via PowerShell:
```powershell
.\env\Scripts\Activate.ps1
```
*(If you see an execution policy error, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Initialize Database
Initialize all 15 tables and seed sample data:
```powershell
python init_db.py
```
> **Tip for MySQL Users**: If your local MySQL `root` user has a password, pass it directly:
> ```powershell
> python init_db.py --password YOUR_MYSQL_PASSWORD
> ```
> Or set `DB_PASSWORD=YOUR_MYSQL_PASSWORD` in `.env`.
> If MySQL is not running or no password is provided, `init_db.py` automatically initializes the local database store so you can immediately test the application!

### 4. Run the Application
```powershell
python app.py
```
Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Default Demo Login Credentials

The seed script automatically creates 3 HR users with preset accounts:

| Role | Email | Password |
| :--- | :--- | :--- |
| **HR Director (Admin)** | `admin@recruitment.ai` | `Admin@123` |
| **Senior Tech Recruiter** | `sarah.recruiter@recruitment.ai` | `Recruiter@123` |
| **Talent Acquisition Partner** | `michael.hr@recruitment.ai` | `Recruiter@123` |

*(The login page also has convenient one-click demo autofill buttons)*

---

## ⚙️ Environment Configuration (`.env`)

```ini
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=ai-hr-recruitment-secret-key-change-in-prod-2025

# Database Configuration (MySQL)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=ai_hr_recruitment

# AI / LLM Configuration
# Options: demo, gemini, openai, ollama
AI_PROVIDER=demo
AI_API_KEY=
AI_MODEL=gemini-1.5-flash

# Demo Mode: true runs all parsing & matching offline with zero API keys required
DEMO_MODE=true

# Upload Configuration
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=static/uploads/resumes
```

### Enabling Real AI (Gemini or OpenAI)
To connect to an external LLM API:
1. In `.env`, set:
   ```ini
   DEMO_MODE=false
   AI_PROVIDER=gemini       # or openai
   AI_API_KEY=your_actual_api_key_here
   AI_MODEL=gemini-1.5-flash # or gpt-4o-mini
   ```
2. Restart the application (`python app.py`). The topbar badge will display `AI: GEMINI` or `AI: OPENAI`.

---

## 🧪 Running Automated Tests

Run the complete test suite:
```powershell
python -m unittest discover tests
```
All tests verify:
- Registration and login authentication security
- 5-factor weighted candidate matching algorithm
- Resume entity extraction and skill ontology
- Protected web routes and REST API endpoints

---

## 📡 REST API Documentation

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/api/login` | HR User login | No |
| `POST` | `/api/register` | HR User registration | No |
| `POST` | `/api/logout` | End session | Yes |
| `GET` | `/api/me` | Current authenticated user profile | Yes |
| `GET` | `/api/jobs` | List all job requisitions | No |
| `POST` | `/api/jobs` | Create requisition with AI skills | Yes |
| `GET` | `/api/jobs/<id>` | Requisition details and skills | No |
| `DELETE` | `/api/jobs/<id>` | Delete requisition | Yes |
| `POST` | `/api/ai/analyze-job` | AI skill extraction from JD | Yes |
| `GET` | `/api/candidates` | List talent directory | No |
| `GET` | `/api/candidates/<id>` | Candidate detailed profile | No |
| `PUT` | `/api/candidates/<id>/status` | Update candidate recruitment status | Yes |
| `POST` | `/api/resumes/upload` | Upload & parse PDF/DOCX resume | Yes |
| `GET` | `/api/jobs/<id>/matches` | Ranked candidate matches for a job | No |
| `POST` | `/api/jobs/<job_id>/match/<candidate_id>` | Recompute candidate match | Yes |
| `POST` | `/api/ai/generate-interview-questions` | Generate interview questions | Yes |
| `GET` | `/api/interviews` | List all scheduled interviews | No |
| `POST` | `/api/interviews` | Schedule an interview round | Yes |
| `GET` | `/api/reports/dashboard` | Aggregated analytics & chart data | Yes |
| `GET` | `/api/reports/export` | Download full CSV data report | Yes |

---

## 🛡️ Security & Privacy Architecture

- **Strict Non-Bias Matching**: The scoring algorithm evaluates only explicit skills, documented experience years, degrees, and project technical relevance. Demographics (age, gender, ethnicity, location, etc.) are excluded from scoring.
- **SQL Parameterization**: Every database query uses parameterized statements (`%s`), preventing SQL injection.
- **Safe Uploads**: Filenames are sanitized with UUIDs and directory traversal attacks are blocked.
- **Session Protection**: HTTPOnly session cookies protect against XSS attacks.

#   A I - H R - R e c r u i t m e n t - A s s i s t a n t  
 