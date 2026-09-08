-- AI HR RECRUITMENT ASSISTANT
-- Complete Database Schema (15 Tables)
-- Database: ai_hr_recruitment

CREATE DATABASE IF NOT EXISTS ai_hr_recruitment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ai_hr_recruitment;

-- 1. Users (HR Managers & Recruiters)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'HR Manager',
    company VARCHAR(150) DEFAULT 'Acme Corporation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Jobs
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    title VARCHAR(150) NOT NULL,
    department VARCHAR(100) NOT NULL,
    location VARCHAR(120) NOT NULL,
    employment_type ENUM('Full Time', 'Part Time', 'Internship', 'Contract') DEFAULT 'Full Time',
    experience_required VARCHAR(50) NOT NULL,
    min_salary DECIMAL(12,2) NULL,
    max_salary DECIMAL(12,2) NULL,
    description TEXT NOT NULL,
    education_requirements VARCHAR(255) NULL,
    responsibilities TEXT NULL,
    status ENUM('Active', 'Closed', 'Draft') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_job_status (status),
    INDEX idx_job_department (department),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Job Skills
CREATE TABLE IF NOT EXISTS job_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    is_required BOOLEAN DEFAULT TRUE,
    category VARCHAR(50) DEFAULT 'General',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_job_skills_job (job_id),
    INDEX idx_job_skills_name (skill_name),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Candidates
CREATE TABLE IF NOT EXISTS candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(50) NULL,
    location VARCHAR(120) NULL,
    current_title VARCHAR(150) NULL,
    years_experience DECIMAL(4,1) DEFAULT 0.0,
    recruitment_status ENUM('New', 'Under Review', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected') DEFAULT 'New',
    ai_summary TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_candidate_status (recruitment_status),
    INDEX idx_candidate_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Resumes
CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT DEFAULT 0,
    file_type VARCHAR(50) NOT NULL,
    extracted_text LONGTEXT NULL,
    raw_json LONGTEXT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_resume_candidate (candidate_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Candidate Skills
CREATE TABLE IF NOT EXISTS candidate_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) DEFAULT 'General',
    proficiency VARCHAR(50) DEFAULT 'Intermediate',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cand_skill_candidate (candidate_id),
    INDEX idx_cand_skill_name (skill_name),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Candidate Experience
CREATE TABLE IF NOT EXISTS candidate_experience (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    company VARCHAR(150) NOT NULL,
    title VARCHAR(150) NOT NULL,
    start_date VARCHAR(50) NULL,
    end_date VARCHAR(50) NULL,
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cand_exp_candidate (candidate_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Candidate Education
CREATE TABLE IF NOT EXISTS candidate_education (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    degree VARCHAR(150) NOT NULL,
    institution VARCHAR(200) NOT NULL,
    field_of_study VARCHAR(150) NULL,
    graduation_year VARCHAR(20) NULL,
    grade VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cand_edu_candidate (candidate_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Candidate Projects
CREATE TABLE IF NOT EXISTS candidate_projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    project_title VARCHAR(200) NOT NULL,
    description TEXT NULL,
    technologies_used VARCHAR(500) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cand_proj_candidate (candidate_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Candidate Certifications
CREATE TABLE IF NOT EXISTS candidate_certifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    issuing_organization VARCHAR(200) NULL,
    issue_date VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cand_cert_candidate (candidate_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. Job Applications
CREATE TABLE IF NOT EXISTS job_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    candidate_id INT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Applied', 'Screening', 'Shortlisted', 'Interviewing', 'Offered', 'Hired', 'Rejected') DEFAULT 'Applied',
    notes TEXT NULL,
    UNIQUE KEY unique_job_candidate (job_id, candidate_id),
    INDEX idx_app_job (job_id),
    INDEX idx_app_candidate (candidate_id),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. Candidate Matches
CREATE TABLE IF NOT EXISTS candidate_matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    candidate_id INT NOT NULL,
    overall_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    skills_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    experience_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    education_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    project_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    preferred_skills_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    matched_skills JSON NULL,
    missing_skills JSON NULL,
    partial_skills JSON NULL,
    strengths TEXT NULL,
    weaknesses TEXT NULL,
    ai_explanation TEXT NULL,
    recommendation ENUM('Strong Match', 'Potential Match', 'Needs Review') DEFAULT 'Needs Review',
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_job_candidate_match (job_id, candidate_id),
    INDEX idx_match_job_score (job_id, overall_score DESC),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 13. Interview Questions
CREATE TABLE IF NOT EXISTS interview_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    candidate_id INT NOT NULL,
    category ENUM('Technical', 'Project-Based', 'Behavioral', 'Situational', 'Role-Specific', 'Skill Gap') NOT NULL,
    difficulty ENUM('Easy', 'Medium', 'Hard') DEFAULT 'Medium',
    question_text TEXT NOT NULL,
    expected_skills VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_quest_job_cand (job_id, candidate_id),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 14. Interviews
CREATE TABLE IF NOT EXISTS interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    job_id INT NOT NULL,
    scheduled_date DATE NOT NULL,
    scheduled_time TIME NOT NULL,
    interview_type ENUM('Technical', 'HR', 'Managerial', 'Final') DEFAULT 'Technical',
    interviewer_name VARCHAR(150) NOT NULL,
    status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_interview_status (status),
    INDEX idx_interview_date (scheduled_date),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 15. Interview Evaluations
CREATE TABLE IF NOT EXISTS interview_evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    candidate_id INT NOT NULL,
    job_id INT NOT NULL,
    technical_score INT NOT NULL DEFAULT 3,
    communication_score INT NOT NULL DEFAULT 3,
    problem_solving_score INT NOT NULL DEFAULT 3,
    project_knowledge_score INT NOT NULL DEFAULT 3,
    role_fit_score INT NOT NULL DEFAULT 3,
    confidence_score INT NOT NULL DEFAULT 3,
    overall_score DECIMAL(5,2) NOT NULL DEFAULT 60.0,
    strengths TEXT NULL,
    weaknesses TEXT NULL,
    notes TEXT NULL,
    final_recommendation ENUM('Strongly Recommend', 'Recommend', 'Consider', 'Not Recommended') DEFAULT 'Consider',
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_interview_eval (interview_id),
    INDEX idx_eval_job (job_id),
    INDEX idx_eval_candidate (candidate_id),
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

