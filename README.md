<<<<<<< HEAD
# AI-Powered Interview Experience and Preparation Portal

A production-grade, full-stack web application where students and job seekers can share real interview experiences, explore company-specific interview rounds, prepare for technical & HR interviews using AI, analyze resumes for role compatibility, practice interactive mock interviews with live rubric evaluations, and track interview performance trends.

Built exclusively with a **Python Flask** backend, **MySQL** database (with seamless **SQLite** local development/test fallback), **Bootstrap 5** frontend with modern responsive dashboard architecture, and dual **Google Gemini** & **OpenAI** AI provider integration.

---

## 🌟 Key Features & Modules

### 1. Student / User Portal
- **User Authentication**: Secure registration, email validation, scrypt password hashing, session management, and role-based route protection.
- **Interactive Dashboard**: Real-time stats (available experiences, companies, completed mocks, latest AI scores), recent interview experiences, and AI preparation shortcuts.
- **User Profile Management**: Update full name, change passwords securely, and inspect personal preparation summary counts.

### 2. Interview Experience Management
- **Community Submissions**: Share detailed interview experiences including company name, job role, interview date, format (Online/Offline), difficulty (Easy/Medium/Hard), candidate level (Fresher to Senior), number of rounds, technical coding questions, HR/behavioral questions, overall process review, preparation tips, and outcome (`Selected`, `Rejected`, `Waiting`, `Not Disclosed`).
- **Moderation Workflow**: Submitted experiences enter `pending` approval status. Only approved experiences appear in public exploration and vector search retrieval.
- **My Experiences**: Manage, edit, and delete your own submissions. Edits automatically enter the moderation queue for re-approval.
- **Explore & Filter**: Filter approved experiences by company, job role, difficulty, experience level, and keyword search.

### 3. AI Module 1: AI Mock Interview
- **Dynamic Session Configuration**: Select target company, job role, category (`Technical`, `HR`, `Mixed`), difficulty (`Beginner`, `Intermediate`, `Advanced`), and question count (3 to 10 questions).
- **Interactive Runner**: Questions delivered one at a time with real-time candidate answer submission.
- **Multi-Criteria Rubric Grading**: Evaluates relevance (0-100), technical correctness (0-100), completeness (0-100), and clarity (0-100).
- **Actionable Feedback**: Instant feedback highlighting key strengths, improvement areas, and a model exemplary answer.
- **Comprehensive Final Report**: Performance score meter, executive summary, recurring strengths, growth opportunities, and question-by-question review.
- **Disclaimer**: Clearly communicates AI evaluation as practice feedback rather than an objective guarantee of hiring outcomes.

### 4. AI Module 2: AI Question Generator
- **Role-Tailored Generation**: Generates customized practice questions across Technical, Programming, Scenario-based, Conceptual, and HR categories.
- **Approved Experience Context**: Automatically leverages approved company interview experiences as real-world background context.
- **Model Solutions**: Every question includes a difficulty rating, subtopic, suggested model answer, architectural explanation, and core concepts to study.
- **Notebook & Bookmarks**: Save/bookmark questions to your personal study notebook or jump straight into a simulated mock interview.

### 5. AI Module 3: AI Resume Analyzer
- **PyMuPDF Document Extraction**: Secure text extraction from uploaded PDF resumes (and DOCX via python-docx).
- **Target Role Compatibility**: Matches candidate resume against target job role and optional job descriptions.
- **Diagnostic Breakdown**: Extracted technical skills cloud, education, projects, experience summary, strengths, weaknesses, and missing/underrepresented skills.
- **Actionable Suggestions**: Concrete, high-impact resume enhancement recommendations and recommended study topics.
- **Privacy Controls**: Users can review past analyses and permanently delete stored analyses and documents at any time.

### 6. AI Module 4: AI Smart Search
- **Natural Language Semantic Search**: Understands queries like *"Show me Python developer interviews for freshers with difficult technical rounds"* or *"Find companies that asked SQL and DBMS questions"*.
- **Vector Embeddings**: Dense semantic vector matching using `SentenceTransformers` (`all-MiniLM-L6-v2`) and FAISS inner product cosine similarity with relational MySQL metadata filters.
- **Match Explanations**: Surfaces relevance match percentages and extracted snippet explanations highlighting *why* a particular experience matched.
- **Suggested Queries & History**: One-click suggested query pills and user search history tracking.

### 7. AI Module 5: AI Performance Analysis
- **Real Saved Data**: Analyzes actual completed mock interview sessions without generating synthetic metrics.
- **Chart.js Visualizations**: Score progression line chart over time, and Technical vs HR/Behavioral round comparison bar chart.
- **Diagnostic Insights**: Highlights demonstrated strengths, priority improvement areas, and recurring gaps.
- **Personalized AI Mentor Diagnostic**: Generates tailored multi-paragraph study recommendations.
- **Zero-Data Handling**: Displays an informative empty state for users who haven't completed mock sessions yet.

### 8. Administrator Control Center
- **Dedicated Admin Authentication**: Separate secure admin login (`/admin/login`) with no public self-registration.
- **Moderation Queue**: Review pending experiences, approve for public display, reject with custom explanatory notes, or delete inappropriate content.
- **User Directory**: Search registered users, toggle active/deactivate status, or delete accounts.
- **Company Management**: Create, update, and delete company directories and view associated experience counts.
- **AI Token & Cost Governance**: Monitor AI request counts, success/failure telemetry, token consumption, and estimated API spend in USD.
- **Security Audit Logs**: Comprehensive compliance logging of all administrative actions with IP addresses and timestamps.
- **System Reports**: Popular companies, trending student search queries, and candidate selection ratios.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.11+, Flask 3.1+, Flask Blueprints |
| **Database** | MySQL 8.0+ via `mysql-connector-python` (with automatic SQLite fallback) |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5.3, Jinja2, Chart.js, Bootstrap Icons |
| **AI Providers** | Google Gemini API (`google-genai` / `google-generativeai`), OpenAI API (`openai`) |
| **Resume Processing** | PyMuPDF (`pymupdf`), python-docx |
| **Vector Search** | SentenceTransformers (`all-MiniLM-L6-v2`), FAISS (`faiss-cpu`) |
| **Security** | Werkzeug scrypt hashing, Flask-WTF CSRF protection, secure HTTP-only cookies |
| **Testing** | pytest 9.2+, Flask test client, Mocked AI provider |

---

## 📂 Project Structure

```
Interview_Experience_Portal/
├── app.py                      # Flask Application entry point & factory
├── config.py                   # Centralized configuration & environment loader
├── database.py                 # MySQL connection pooling & SQLite fallback engine
├── requirements.txt            # Python dependencies
├── schema.sql                  # MySQL database schema (13 normalized relational tables)
├── .env.example                # Environment variables template
├── README.md                   # Complete documentation
├── seed_admin.py               # Administrator account seeder script
├── seed_data.py                # Initial companies & sample approved experiences seeder
│
├── models/                     # Data domain models
│   ├── __init__.py
│   ├── user.py                 # User & Admin models
│   ├── company.py              # Company model
│   ├── experience.py           # InterviewExperience model
│   ├── mock_interview.py       # MockInterviewSession & MockInterviewQuestion models
│   └── resume_analysis.py      # ResumeAnalysis & GeneratedQuestion models
│
├── dao/                        # Data Access Object (DAO) layer
│   ├── __init__.py
│   ├── user_dao.py             # User & Admin database operations
│   ├── company_dao.py          # Company directory operations
│   ├── experience_dao.py       # Interview experience queries & moderation
│   └── ai_dao.py               # Mocks, generated questions, resumes, usage & audit logs
│
├── routes/                     # Modular Flask Blueprint routes
│   ├── __init__.py
│   ├── auth_routes.py          # Register, Login, Logout, Decorators
│   ├── user_routes.py          # User Dashboard & Profile management
│   ├── experience_routes.py    # Experience submission, explore, edit, delete
│   ├── admin_routes.py         # Admin control panel, moderation, users, AI governance
│   ├── mock_interview_routes.py # AI Mock interview setup, runner, evaluation, report
│   ├── question_generator_routes.py # AI Question generator & bookmarking
│   ├── resume_analyzer_routes.py    # Resume file upload, PyMuPDF extraction, matching
│   ├── smart_search_routes.py  # Natural language semantic vector search
│   └── performance_routes.py   # Performance tracking & Chart.js dashboards
│
├── services/ai/                # AI Provider abstraction & domain services
│   ├── __init__.py
│   ├── base_provider.py        # Abstract base provider class
│   ├── gemini_provider.py      # Google Gemini integration
│   ├── openai_provider.py      # OpenAI integration
│   ├── ai_factory.py           # Factory pattern with MockAIProvider & cost calculation
│   ├── mock_interview_service.py     # Question synthesis & rubric evaluations
│   ├── question_generation_service.py # Role question generation with context
│   ├── resume_analysis_service.py    # Text parsing & compatibility scoring
│   ├── smart_search_service.py       # SentenceTransformers & FAISS embeddings
│   └── performance_analysis_service.py # Performance analytics & mentor diagnostic
│
├── templates/                  # Modern Jinja2 HTML5 templates
│   ├── base.html               # Master layout with navbar, alerts, footer
│   ├── user_layout.html        # Modern user layout with sidebar navigation
│   ├── admin_layout.html       # Dark professional admin layout with sidebar
│   ├── index.html              # Public landing page with hero banner & features
│   ├── login.html              # Student / User sign-in
│   ├── register.html           # Student registration
│   ├── dashboard.html          # User overview dashboard
│   ├── profile.html            # Profile & password management
│   ├── experiences.html        # Public approved experience exploration with filters
│   ├── add_experience.html     # Experience submission form
│   ├── edit_experience.html    # Edit own experience form
│   ├── experience_detail.html  # Full experience view with round details
│   ├── my_experiences.html     # User's submitted experiences with status badges
│   ├── mock_interview.html     # Mock interview setup wizard
│   ├── mock_interview_session.html # Interactive live interview runner with rubric
│   ├── mock_interview_report.html  # Final evaluation report & score meter
│   ├── mock_interview_history.html # Previous mock interview sessions table
│   ├── question_generator.html # AI question generator & practice cards
│   ├── saved_questions.html    # Bookmarked practice questions notebook
│   ├── resume_analyzer.html    # Resume PDF upload form
│   ├── resume_detail.html      # Resume compatibility diagnostics & skill cloud
│   ├── my_resumes.html         # Table of analyzed resumes with privacy clean
│   ├── smart_search.html       # Semantic search interface with snippets
│   ├── performance_analysis.html # Chart.js performance graphs & AI mentor
│   ├── admin_login.html        # Dedicated administrator login
│   ├── admin_dashboard.html    # Admin control center
│   ├── admin_users.html        # User account management & toggles
│   ├── admin_experiences.html  # Experience moderation queue
│   ├── admin_companies.html    # Company CRUD management modal
│   ├── admin_ai_usage.html     # AI token usage, error monitoring & costs
│   └── admin_reports.html      # Platform activity reports & popular searches
│
├── static/                     # Static assets
│   ├── css/style.css           # Custom styling, color palette & cards
│   └── js/main.js              # CSRF handlers, AJAX evaluation, bookmarking
│
├── uploads/resumes/            # Secure upload storage directory
└── tests/                      # Automated test suite (pytest)
    ├── __init__.py
    ├── conftest.py             # Test fixtures & Mock AI provider configuration
    ├── test_auth.py            # Authentication & authorization tests
    ├── test_experiences.py     # Experience CRUD & moderation workflow tests
    ├── test_admin.py           # Admin portal & user control tests
    ├── test_ai_features.py     # Mock interview, questions, resume, search tests
    └── test_edge_cases.py      # Error handling, empty inputs, unconfigured API tests
```

---

## 🚀 Setup & Installation Guide

### Prerequisites
- Python 3.11 or higher
- MySQL Server 8.0+ (optional: SQLite fallback operates automatically if MySQL is not running)

### Step 1: Clone or Navigate to Directory
```bash
cd Interview_Experience_Portal
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
Open `.env` and set your configuration:
```env
# Flask Configuration
FLASK_SECRET_KEY=your-secure-random-secret-key-here
PORT=5000

# Database Configuration (MySQL)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=interview_experience_portal
USE_SQLITE_FALLBACK=false

# AI Provider Configuration ('gemini' or 'openai')
AI_PROVIDER=gemini

# Google Gemini API Credentials
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# OpenAI API Credentials (Optional Alternative)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

> **Note on Database Connectivity:**
> If you have a local or remote MySQL server running, set `USE_SQLITE_FALLBACK=false` and provide your credentials. The application connects via connection pooling and uses `mysql-connector-python`. If MySQL is unavailable on your system, set `USE_SQLITE_FALLBACK=true` (or leave the automatic fallback active) to run the application immediately out of the box using SQLite!

### Step 4: Initialize MySQL Database (When using MySQL)
In your MySQL command line or Workbench:
```sql
SOURCE schema.sql;
```
*(Or let `database.py` initialize the schema automatically on first run).*

### Step 5: Seed Administrator Account
Admin accounts cannot be registered publicly. Run the secure seed script:
```bash
python seed_admin.py --username admin --email admin@interviewportal.com --password AdminPassword123!
```

### Step 6: Seed Initial Sample Data (Companies & Experiences)
Populate verified sample companies (Google, Amazon, Microsoft, TCS, Infosys) and approved experiences:
```bash
python seed_data.py
```

### Step 7: Run the Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🔑 Default Credentials (After Seeding)

| Role | Portal URL | Username / Email | Password |
|---|---|---|---|
| **Administrator** | `http://localhost:5000/admin/login` | `admin` / `admin@interviewportal.com` | `AdminPassword123!` |
| **Test Student** | `http://localhost:5000/login` | `student@example.com` | `Student123!` |

*(You can also register new student/user accounts at `/register`).*

---

## 🤖 Live AI Configuration Guide

### 1. Google Gemini API (Primary Provider)
1. Visit [Google AI Studio](https://aistudio.google.com/) and obtain a free API key.
2. In your `.env` file:
   ```env
   AI_PROVIDER=gemini
   GEMINI_API_KEY=AIzaSyYourActualGeminiKeyHere
   GEMINI_MODEL=gemini-2.5-flash
   ```
3. Restart `app.py`. Live AI mock interviews, question generation, and resume analysis will now call the official Google GenAI SDK.

### 2. OpenAI API (Alternative Provider)
1. Obtain an API key from [OpenAI Platform](https://platform.openai.com/api-keys).
2. In your `.env` file:
   ```env
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-YourActualOpenAIKeyHere
   OPENAI_MODEL=gpt-4o-mini
   ```
3. Restart `app.py`. The provider abstraction factory seamlessly routes all AI requests to OpenAI.

### 3. Graceful Offline Fallback & Mock Mode
If an API key is not configured or network quota is exceeded:
- The backend gracefully logs the issue without crashing.
- Fallback mock data and domain algorithms engage automatically so candidates can test the end-to-end user experience without interruption.

---

## 🧪 Running Automated Tests

The application includes an extensive **pytest** test suite with **100% pass rate** across 34 automated unit and integration tests.

The test suite runs with a mocked AI provider (`AIFactory.set_force_mock(True)`), so tests run instantaneously **without requiring paid API keys or network access**.

Run all tests:
```bash
python -m pytest tests -v
```

### Test Coverage Highlights:
- **Authentication (`test_auth.py`)**: Registration, password hashing (scrypt), duplicate email prevention, login validation, session handling, route protection.
- **Experience Management (`test_experiences.py`)**: Pending submission workflow, admin approval, public view gating, search filtering, editing re-approval, deletion.
- **Admin Management (`test_admin.py`)**: Admin credentials authentication, audit trail logging, user activation toggling, company CRUD, telemetry pages.
- **AI Modules (`test_ai_features.py`)**: Mock interview question generation, answer evaluation across 4 rubric dimensions, full session lifecycle, question generator with bookmarking, PyMuPDF resume parsing, semantic search retrieval, performance dashboard.
- **Edge Cases (`test_edge_cases.py`)**: Unconfigured API credentials, empty/invalid answer inputs, malicious/unsupported file uploads, empty analytics states.

---

## 🔒 Security & Privacy Architecture

- **Password Hashing**: Implements Werkzeug's modern `scrypt` key derivation function with unique salts.
- **CSRF Protection**: All forms and AJAX state-changing requests are protected via `Flask-WTF` CSRF tokens and HTTP headers.
- **SQL Injection Prevention**: 100% parameterized queries across all MySQL and SQLite database calls.
- **Role-Based Access Control**: Strict separation between Student (`@login_required`) and Administrator (`@admin_required`) routes.
- **Prompt Injection Defense**: All user inputs (interview answers, uploaded resume text) are strictly isolated as untrusted data strings within structured boundaries, preventing system prompt overriding.
- **Resume Document Privacy**: Uploaded resumes are never exposed publicly. Users can permanently delete their analyses and stored files at any time.
- **Administrative Audit Logging**: All sensitive administrative actions (approving, rejecting, editing, deleting, user status changes) are logged with admin ID, action type, IP address, and timestamp.

---

## 📄 License
Educational & Commercial preparation project. Developed with standard open-source Python libraries.
=======
# Interview_Experience_Portal
Developed an AI-powered web platform enabling students to share, explore, and prepare using real interview experiences.
>>>>>>> 8443a58b22a0f666cdf90cc02b34437eecc142f1
