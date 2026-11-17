-- ============================================================
-- Database Schema for AI-Powered Interview Experience and Preparation Portal
-- Target RDBMS: MySQL 8.0+ / MariaDB 10.5+
-- Database Name: interview_experience_portal
-- ============================================================

CREATE DATABASE IF NOT EXISTS interview_experience_portal 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE interview_experience_portal;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(180) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'user', 'admin') DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Admins Table
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(180) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_admins_username (username),
    INDEX idx_admins_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Companies Table
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_companies_name (company_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Interview Experiences Table
CREATE TABLE IF NOT EXISTS interview_experiences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    company_id INT NOT NULL,
    job_role VARCHAR(150) NOT NULL,
    interview_date DATE,
    interview_type ENUM('Online', 'Offline') DEFAULT 'Online',
    difficulty ENUM('Easy', 'Medium', 'Hard') DEFAULT 'Medium',
    experience_level ENUM('Fresher', 'Entry Level', 'Mid Level', 'Senior') DEFAULT 'Fresher',
    interview_rounds INT DEFAULT 1,
    technical_questions MEDIUMTEXT,
    hr_questions MEDIUMTEXT,
    overall_experience MEDIUMTEXT NOT NULL,
    preparation_tips MEDIUMTEXT,
    result ENUM('Selected', 'Rejected', 'Waiting', 'Not Disclosed') DEFAULT 'Not Disclosed',
    approval_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    rejection_reason VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_experience_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_experience_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_exp_approval (approval_status),
    INDEX idx_exp_company (company_id),
    INDEX idx_exp_role (job_role),
    INDEX idx_exp_difficulty (difficulty),
    INDEX idx_exp_result (result)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Mock Interview Sessions Table
CREATE TABLE IF NOT EXISTS mock_interview_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    job_role VARCHAR(150) NOT NULL,
    interview_category ENUM('Technical', 'HR', 'Mixed') DEFAULT 'Technical',
    difficulty ENUM('Beginner', 'Intermediate', 'Advanced') DEFAULT 'Intermediate',
    total_questions INT NOT NULL DEFAULT 5,
    current_question_index INT DEFAULT 0,
    overall_score DECIMAL(5,2) NULL,
    final_feedback MEDIUMTEXT NULL,
    strengths_summary MEDIUMTEXT NULL,
    weaknesses_summary MEDIUMTEXT NULL,
    recommendations MEDIUMTEXT NULL,
    status ENUM('in_progress', 'completed', 'abandoned') DEFAULT 'in_progress',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME NULL,
    CONSTRAINT fk_mock_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_mock_user (user_id),
    INDEX idx_mock_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Mock Interview Questions Table
CREATE TABLE IF NOT EXISTS mock_interview_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    question_order INT NOT NULL DEFAULT 1,
    question_category ENUM('Technical', 'HR') DEFAULT 'Technical',
    question TEXT NOT NULL,
    suggested_answer MEDIUMTEXT NULL,
    user_answer MEDIUMTEXT NULL,
    evaluation_feedback MEDIUMTEXT NULL,
    strengths TEXT NULL,
    weaknesses TEXT NULL,
    relevance_score DECIMAL(5,2) NULL,
    correctness_score DECIMAL(5,2) NULL,
    completeness_score DECIMAL(5,2) NULL,
    clarity_score DECIMAL(5,2) NULL,
    overall_question_score DECIMAL(5,2) NULL,
    evaluated_at DATETIME NULL,
    CONSTRAINT fk_mock_q_session FOREIGN KEY (session_id) REFERENCES mock_interview_sessions(id) ON DELETE CASCADE,
    INDEX idx_mock_q_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Generated Questions Table
CREATE TABLE IF NOT EXISTS generated_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    company_name VARCHAR(150) NOT NULL,
    job_role VARCHAR(150) NOT NULL,
    technical_domain VARCHAR(150) NULL,
    category VARCHAR(100) NOT NULL,
    difficulty ENUM('Beginner', 'Intermediate', 'Advanced') DEFAULT 'Intermediate',
    question TEXT NOT NULL,
    suggested_answer MEDIUMTEXT,
    explanation MEDIUMTEXT,
    key_concepts MEDIUMTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_gen_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_gen_company (company_name),
    INDEX idx_gen_role (job_role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Saved Questions Table
CREATE TABLE IF NOT EXISTS saved_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    generated_question_id INT NOT NULL,
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_saved_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_saved_question FOREIGN KEY (generated_question_id) REFERENCES generated_questions(id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_saved_question (user_id, generated_question_id),
    INDEX idx_saved_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Resume Analyses Table
CREATE TABLE IF NOT EXISTS resume_analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    target_job_role VARCHAR(150) NOT NULL,
    job_description MEDIUMTEXT NULL,
    extracted_text_reference MEDIUMTEXT NULL,
    skills MEDIUMTEXT,
    education_summary MEDIUMTEXT,
    projects_summary MEDIUMTEXT,
    experience_summary MEDIUMTEXT,
    strengths MEDIUMTEXT,
    weaknesses MEDIUMTEXT,
    missing_skills MEDIUMTEXT,
    compatibility_score DECIMAL(5,2),
    improvement_suggestions MEDIUMTEXT,
    suggested_topics MEDIUMTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_resume_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_resume_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Search History Table
CREATE TABLE IF NOT EXISTS search_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    search_query VARCHAR(255) NOT NULL,
    results_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_search_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_search_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. Experience Embeddings Table
CREATE TABLE IF NOT EXISTS experience_embeddings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    experience_id INT NOT NULL UNIQUE,
    embedding_reference VARCHAR(255) NOT NULL,
    content_hash VARCHAR(64) NULL,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_embedding_experience FOREIGN KEY (experience_id) REFERENCES interview_experiences(id) ON DELETE CASCADE,
    INDEX idx_embedding_exp (experience_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 12. AI Usage Logs Table
CREATE TABLE IF NOT EXISTS ai_usage_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    feature_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    status ENUM('success', 'error', 'rate_limited') DEFAULT 'success',
    prompt_tokens INT DEFAULT 0,
    completion_tokens INT DEFAULT 0,
    token_usage INT DEFAULT 0,
    estimated_cost DECIMAL(8,6) DEFAULT 0.0,
    error_message TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ai_log_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_ai_log_feature (feature_name),
    INDEX idx_ai_log_provider (provider),
    INDEX idx_ai_log_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 13. Admin Audit Logs Table
CREATE TABLE IF NOT EXISTS admin_audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NULL,
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(100) NOT NULL,
    target_id INT NULL,
    details TEXT NULL,
    ip_address VARCHAR(45) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_admin FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE SET NULL,
    INDEX idx_audit_admin (admin_id),
    INDEX idx_audit_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
