-- AI HR RECRUITMENT ASSISTANT - Seed Data
USE ai_hr_recruitment;

-- 1. Seed HR Users
-- Default Passwords:
-- admin@recruitment.ai -> Admin@123
-- sarah.recruiter@recruitment.ai -> Recruiter@123
-- michael.hr@recruitment.ai -> Recruiter@123
INSERT INTO users (id, name, email, password_hash, role, company) VALUES
(1, 'Admin User', 'admin@recruitment.ai', 'scrypt:32768:8:1$RgcUvUZTjI77NAdA$251f33efc2bce0e61ad3e02036c99d3f383c7861b2f5d66c14f6a5b85ac86adc4fd3a3ee6f91c6634ca8611e0a3b0612db56a61906904044ed6601b0cc213a0c', 'HR Director', 'TalentFlow Global'),
(2, 'Sarah Jenkins', 'sarah.recruiter@recruitment.ai', 'scrypt:32768:8:1$OABEiWVRmTPtTSP9$4a422e0fda76fb70539fb77df8c51d0bf8f3beea05041844fc215a944bb9077a601257c3990eefee609f0681d0f4911ce39df3145b25f52d335441a2a52f9499', 'Senior Tech Recruiter', 'TalentFlow Global'),
(3, 'Michael Chang', 'michael.hr@recruitment.ai', 'scrypt:32768:8:1$OABEiWVRmTPtTSP9$4a422e0fda76fb70539fb77df8c51d0bf8f3beea05041844fc215a944bb9077a601257c3990eefee609f0681d0f4911ce39df3145b25f52d335441a2a52f9499', 'Talent Acquisition Partner', 'TalentFlow Global')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 2. Seed Jobs
INSERT INTO jobs (id, user_id, title, department, location, employment_type, experience_required, min_salary, max_salary, description, education_requirements, responsibilities, status) VALUES
(1, 1, 'Senior Python / Flask Backend Engineer', 'Engineering', 'Remote / New York, NY', 'Full Time', '5+ Years', 120000.00, 150000.00, 
'We are looking for a Senior Python / Flask Backend Engineer to architect, build, and scale high-throughput RESTful microservices. You will lead database design in MySQL, optimize caching layers with Redis, and collaborate closely with frontend developers.',
'Bachelor''s or Master''s in Computer Science, Software Engineering, or equivalent experience.',
'1. Design and maintain resilient REST APIs with Python and Flask.\n2. Model and optimize complex relational schemas in MySQL.\n3. Containerize applications using Docker and orchestrate CI/CD deployments.\n4. Mentor junior engineers and enforce best coding practices.', 'Active'),

(2, 2, 'Full-Stack Software Engineer', 'Product Engineering', 'San Francisco, CA (Hybrid)', 'Full Time', '3+ Years', 95000.00, 125000.00,
'Join our core product team building modern SaaS recruitment tools. You will work across both client-facing React interfaces and robust backend APIs built with Flask and Python.',
'Bachelor''s degree in Computer Science, Information Technology, or relevant discipline.',
'1. Develop responsive UI components with React and modern CSS.\n2. Implement backend business logic and database queries in Python.\n3. Participate in sprint planning, code reviews, and architectural spikes.\n4. Write comprehensive automated unit and integration tests.', 'Active'),

(3, 1, 'AI / Machine Learning Specialist', 'Data & AI', 'Remote / Austin, TX', 'Full Time', '4+ Years', 135000.00, 170000.00,
'Seeking an experienced AI/ML Engineer to train, fine-tune, and deploy state-of-the-art NLP models, embedding pipelines, and LLM integrations. Deep expertise in Python, PyTorch/TensorFlow, and vector databases required.',
'Master''s or Ph.D. in Computer Science, Artificial Intelligence, or Mathematics.',
'1. Build production LLM pipelines and embedding retrieval mechanisms.\n2. Fine-tune open-weight models for document parsing and entity extraction.\n3. Collaborate with software engineers to productionize AI microservices.\n4. Monitor model drift and inference latency.', 'Active'),

(4, 2, 'Frontend React Developer', 'Design & Engineering', 'Austin, TX (Hybrid)', 'Full Time', '3+ Years', 85000.00, 115000.00,
'We need a talented Frontend Developer proficient in React, modern JavaScript/TypeScript, HTML5, and CSS3. You will craft fluid, accessible, and fast web dashboards.',
'Bachelor''s degree in CS, Web Development, or equivalent practical portfolio.',
'1. Build dynamic, modular web views using React, Bootstrap 5, and Chart.js.\n2. Ensure cross-browser compatibility, web accessibility (WCAG), and responsive UX.\n3. Integrate client-side interfaces with RESTful backend services.\n4. Optimize web bundle sizes and Core Web Vitals.', 'Active'),

(5, 3, 'Cloud DevOps & SRE Engineer', 'Infrastructure', 'Remote / Chicago, IL', 'Contract', '4+ Years', 110000.00, 140000.00,
'Looking for a DevOps Engineer to manage AWS infrastructure as code, Kubernetes clusters, Docker image pipelines, and monitoring systems.',
'Bachelor''s in Computer Science, Systems Engineering, or equivalent experience.',
'1. Maintain Kubernetes clusters and Terraform infrastructure on AWS.\n2. Streamline CI/CD pipelines using GitHub Actions.\n3. Configure Prometheus, Grafana, and ELK log aggregation.\n4. Implement robust security practices and automated vulnerability scanning.', 'Active')
ON DUPLICATE KEY UPDATE title=VALUES(title);

-- 3. Job Skills
INSERT INTO job_skills (job_id, skill_name, is_required, category) VALUES
-- Job 1 Skills (Python Backend)
(1, 'Python', TRUE, 'Programming Language'),
(1, 'Flask', TRUE, 'Framework'),
(1, 'MySQL', TRUE, 'Database'),
(1, 'REST API', TRUE, 'Architecture'),
(1, 'Docker', TRUE, 'DevOps'),
(1, 'Redis', FALSE, 'Database'),
(1, 'Git', TRUE, 'Tools'),
(1, 'AWS', FALSE, 'Cloud'),

-- Job 2 Skills (Full-Stack)
(2, 'JavaScript', TRUE, 'Programming Language'),
(2, 'React', TRUE, 'Framework'),
(2, 'Python', TRUE, 'Programming Language'),
(2, 'Flask', TRUE, 'Framework'),
(2, 'HTML5', TRUE, 'Frontend'),
(2, 'CSS3', TRUE, 'Frontend'),
(2, 'MySQL', TRUE, 'Database'),
(2, 'TypeScript', FALSE, 'Programming Language'),
(2, 'Docker', FALSE, 'DevOps'),

-- Job 3 Skills (AI/ML)
(3, 'Python', TRUE, 'Programming Language'),
(3, 'PyTorch', TRUE, 'Framework'),
(3, 'TensorFlow', FALSE, 'Framework'),
(3, 'NLP', TRUE, 'Domain'),
(3, 'Scikit-Learn', TRUE, 'Library'),
(3, 'LLM Integration', TRUE, 'AI/ML'),
(3, 'Vector Databases', FALSE, 'Database'),
(3, 'Docker', TRUE, 'DevOps'),

-- Job 4 Skills (Frontend)
(4, 'React', TRUE, 'Framework'),
(4, 'JavaScript', TRUE, 'Programming Language'),
(4, 'HTML5', TRUE, 'Frontend'),
(4, 'CSS3', TRUE, 'Frontend'),
(4, 'Bootstrap', TRUE, 'Framework'),
(4, 'Chart.js', FALSE, 'Library'),
(4, 'TypeScript', FALSE, 'Programming Language'),
(4, 'Git', TRUE, 'Tools'),

-- Job 5 Skills (DevOps)
(5, 'Docker', TRUE, 'DevOps'),
(5, 'Kubernetes', TRUE, 'DevOps'),
(5, 'AWS', TRUE, 'Cloud'),
(5, 'Terraform', TRUE, 'DevOps'),
(5, 'CI/CD', TRUE, 'DevOps'),
(5, 'Linux', TRUE, 'Operating System'),
(5, 'Python', FALSE, 'Programming Language'),
(5, 'Prometheus', FALSE, 'Monitoring');

-- 4. Candidates
INSERT INTO candidates (id, name, email, phone, location, current_title, years_experience, recruitment_status, ai_summary) VALUES
(1, 'Rahul Sharma', 'rahul.sharma@example.com', '+1 (555) 234-5678', 'New York, NY', 'Senior Backend Engineer', 5.5, 'Shortlisted',
'Versatile Senior Backend Engineer with 5.5 years of hands-on experience building scalable Python and Flask microservices, optimizing complex MySQL databases, and deploying containerized applications with Docker. Demonstrates deep architectural knowledge and strong problem-solving skills.'),

(2, 'Priya Patel', 'priya.patel@example.com', '+1 (555) 345-6789', 'San Jose, CA', 'Senior Frontend Engineer', 4.0, 'Shortlisted',
'Passionate Frontend Engineer with 4 years specializing in React, TypeScript, responsive Bootstrap designs, and high-performance data visualizations with Chart.js. Strong eye for UX and cross-browser accessibility.'),

(3, 'Alex Mercer', 'alex.mercer@example.com', '+1 (555) 456-7890', 'Boston, MA', 'Machine Learning Researcher', 4.5, 'Interview Scheduled',
'AI/ML specialist with 4.5 years of industry and research experience in Natural Language Processing, transformer fine-tuning, PyTorch, and deploying production LLM inference pipelines with Docker.'),

(4, 'David Miller', 'david.miller@example.com', '+1 (555) 567-8901', 'San Francisco, CA', 'Full-Stack Developer', 3.5, 'Interview Scheduled',
'Balanced full-stack developer with 3.5 years of experience delivering end-to-end web applications using Python, Flask, React, and MySQL. Proven track record in rapid prototyping and RESTful API engineering.'),

(5, 'Ananya Iyer', 'ananya.iyer@example.com', '+1 (555) 678-9012', 'Seattle, WA', 'Backend Systems Developer', 5.0, 'Selected',
'Accomplished software engineer with 5 years in backend Python development, distributed microservices, MySQL query optimization, Redis caching, and CI/CD pipelines. Strong leader with mentoring experience.'),

(6, 'James Wilson', 'james.wilson@example.com', '+1 (555) 789-0123', 'Chicago, IL', 'Senior DevOps / Cloud Engineer', 4.5, 'Under Review',
'Cloud and infrastructure engineer with 4.5 years implementing Kubernetes clusters, AWS cloud architecture, automated Terraform deployments, and zero-downtime CI/CD release pipelines.'),

(7, 'Sneha Reddy', 'sneha.reddy@example.com', '+1 (555) 890-1234', 'Dallas, TX', 'Software Developer', 3.0, 'New',
'Motivated backend software developer with 3 years focusing on Python, relational database design with MySQL, REST APIs, and basic Docker containerization. Eager to expand into large-scale microservice architectures.'),

(8, 'Carlos Rodriguez', 'carlos.rodriguez@example.com', '+1 (555) 901-2345', 'Miami, FL', 'Frontend UI/UX Developer', 3.5, 'New',
'Creative frontend engineer with 3.5 years experience crafting clean interfaces using React, JavaScript, HTML5, CSS3, and Bootstrap. Experienced with state management and API integration.'),

(9, 'Emily Chen', 'emily.chen@example.com', '+1 (555) 012-3456', 'Austin, TX', 'Data & ML Engineer', 3.0, 'Under Review',
'Data scientist with 3 years applying machine learning algorithms in Python, PyTorch, Scikit-Learn, and SQL. Experience building recommendation engines and predictive models in cloud environments.'),

(10, 'Liam Murphy', 'liam.murphy@example.com', '+1 (555) 123-4567', 'Denver, CO', 'Junior Software Engineer', 1.5, 'Rejected',
'Enthusiastic junior developer with 1.5 years experience in foundational Python, JavaScript, and HTML/CSS. Strong academic background and active contributor to open-source personal projects.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 5. Resumes
INSERT INTO resumes (id, candidate_id, filename, original_filename, file_path, file_size, file_type, extracted_text) VALUES
(1, 1, 'resume_rahul_sharma.pdf', 'Rahul_Sharma_Resume.pdf', 'static/uploads/resumes/resume_rahul_sharma.pdf', 104230, 'application/pdf',
'RAHUL SHARMA - Senior Backend Engineer\nEmail: rahul.sharma@example.com | Phone: +1 (555) 234-5678 | New York, NY\n\nSUMMARY: 5.5 years experience building scalable web backend services with Python, Flask, MySQL, Redis, Docker, and REST APIs.\n\nEXPERIENCE:\n- Senior Backend Developer at FinTech Global (2022 - Present): Designed and deployed Flask microservices handling 5M daily requests. Optimized MySQL queries reducing p99 latency by 35%.\n- Software Engineer at Nexa Tech (2019 - 2022): Built RESTful APIs using Python, MySQL, and Docker.\n\nEDUCATION: B.S. in Computer Science, New York University (2019).\nSKILLS: Python, Flask, MySQL, REST API, Docker, Redis, Git, Linux, AWS.\nPROJECTS: High-throughput payment gateway service, Distributed task worker queue.\nCERTIFICATIONS: AWS Certified Developer Associate.'),

(2, 2, 'resume_priya_patel.pdf', 'Priya_Patel_CV.pdf', 'static/uploads/resumes/resume_priya_patel.pdf', 98520, 'application/pdf',
'PRIYA PATEL - Senior Frontend Engineer\nEmail: priya.patel@example.com | San Jose, CA\n\nEXPERIENCE:\n- Frontend Engineer at CloudScale Apps (2021 - Present): Developed React dashboards, integrated REST APIs, styled using modern Bootstrap and CSS3.\n- UI Developer at SoftCraft (2020 - 2021): Implemented modular component libraries.\n\nEDUCATION: B.S. in Software Engineering, San Jose State University (2020).\nSKILLS: React, JavaScript, TypeScript, HTML5, CSS3, Bootstrap, Chart.js, Git.'),

(3, 3, 'resume_alex_mercer.pdf', 'Alex_Mercer_Resume.pdf', 'static/uploads/resumes/resume_alex_mercer.pdf', 115200, 'application/pdf',
'ALEX MERCER - AI / ML Specialist\nEmail: alex.mercer@example.com | Boston, MA\n\nSUMMARY: 4.5 years developing NLP systems, fine-tuning LLMs, and deploying transformer models.\n\nEXPERIENCE:\n- Machine Learning Engineer at AI Nexus (2021 - Present): Trained document classification pipelines with PyTorch and HuggingFace. Deployed containerized endpoints with Docker.\n- Data Scientist at Cognita (2020 - 2021): Built predictive NLP models using Python, Scikit-Learn, and PyTorch.\n\nEDUCATION: M.S. in Artificial Intelligence, Northeastern University (2020).\nSKILLS: Python, PyTorch, TensorFlow, NLP, Scikit-Learn, LLM Integration, Vector Databases, Docker, Git.'),

(4, 4, 'resume_david_miller.pdf', 'David_Miller_Resume.pdf', 'static/uploads/resumes/resume_david_miller.pdf', 92100, 'application/pdf',
'DAVID MILLER - Full-Stack Developer\nEmail: david.miller@example.com | San Francisco, CA\n\nEXPERIENCE:\n- Full-Stack Engineer at OmniWeb (2022 - Present): Developed frontend in React and backend in Flask/Python with MySQL database.\n- Junior Developer at TechSpark (2021 - 2022): Built responsive UI and REST endpoints.\n\nEDUCATION: B.S. in Computer Science, UC Davis (2021).\nSKILLS: Python, Flask, React, JavaScript, MySQL, HTML5, CSS3, Git, REST API.'),

(5, 5, 'resume_ananya_iyer.pdf', 'Ananya_Iyer_Resume.pdf', 'static/uploads/resumes/resume_ananya_iyer.pdf', 108400, 'application/pdf',
'ANANYA IYER - Senior Backend Engineer\nEmail: ananya.iyer@example.com | Seattle, WA\n\nEXPERIENCE:\n- Senior Backend Engineer at PrimeCloud (2021 - Present): Lead engineer for Python Flask backend, MySQL replication, Redis caching, and Docker pipelines.\n- Software Engineer at DataStream (2019 - 2021): Built REST APIs and automated ETL pipelines.\n\nEDUCATION: M.S. in Computer Science, University of Washington (2019).\nSKILLS: Python, Flask, MySQL, Redis, REST API, Docker, Git, AWS, Microservices.');

-- 6. Candidate Skills
INSERT INTO candidate_skills (candidate_id, skill_name, category, proficiency) VALUES
(1, 'Python', 'Programming Language', 'Expert'),
(1, 'Flask', 'Framework', 'Expert'),
(1, 'MySQL', 'Database', 'Advanced'),
(1, 'REST API', 'Architecture', 'Advanced'),
(1, 'Docker', 'DevOps', 'Advanced'),
(1, 'Redis', 'Database', 'Intermediate'),
(1, 'Git', 'Tools', 'Advanced'),
(1, 'AWS', 'Cloud', 'Intermediate'),

(2, 'React', 'Framework', 'Expert'),
(2, 'JavaScript', 'Programming Language', 'Expert'),
(2, 'TypeScript', 'Programming Language', 'Advanced'),
(2, 'HTML5', 'Frontend', 'Expert'),
(2, 'CSS3', 'Frontend', 'Expert'),
(2, 'Bootstrap', 'Framework', 'Advanced'),
(2, 'Chart.js', 'Library', 'Advanced'),
(2, 'Git', 'Tools', 'Advanced'),

(3, 'Python', 'Programming Language', 'Expert'),
(3, 'PyTorch', 'Framework', 'Expert'),
(3, 'TensorFlow', 'Framework', 'Intermediate'),
(3, 'NLP', 'Domain', 'Expert'),
(3, 'Scikit-Learn', 'Library', 'Advanced'),
(3, 'LLM Integration', 'AI/ML', 'Advanced'),
(3, 'Docker', 'DevOps', 'Intermediate'),

(4, 'Python', 'Programming Language', 'Advanced'),
(4, 'Flask', 'Framework', 'Advanced'),
(4, 'React', 'Framework', 'Intermediate'),
(4, 'JavaScript', 'Programming Language', 'Advanced'),
(4, 'MySQL', 'Database', 'Intermediate'),
(4, 'HTML5', 'Frontend', 'Advanced'),
(4, 'CSS3', 'Frontend', 'Advanced'),
(4, 'Git', 'Tools', 'Advanced'),

(5, 'Python', 'Programming Language', 'Expert'),
(5, 'Flask', 'Framework', 'Expert'),
(5, 'MySQL', 'Database', 'Expert'),
(5, 'REST API', 'Architecture', 'Expert'),
(5, 'Docker', 'DevOps', 'Advanced'),
(5, 'Redis', 'Database', 'Advanced'),
(5, 'AWS', 'Cloud', 'Advanced'),
(5, 'Git', 'Tools', 'Expert');

-- 7. Candidate Experience
INSERT INTO candidate_experience (candidate_id, company, title, start_date, end_date, is_current, description) VALUES
(1, 'FinTech Global', 'Senior Backend Developer', '2022-03', 'Present', TRUE, 'Architected and developed Python/Flask RESTful microservices handling 5M daily requests. Optimized MySQL indexing and Redis caching.'),
(1, 'Nexa Tech', 'Software Engineer', '2019-07', '2022-02', FALSE, 'Developed REST APIs in Python with MySQL backend. Implemented automated Docker test suites.'),
(2, 'CloudScale Apps', 'Frontend Engineer', '2021-08', 'Present', TRUE, 'Built modular dashboard interfaces using React and Bootstrap. Integrated Chart.js for analytics views.'),
(3, 'AI Nexus', 'Machine Learning Engineer', '2021-06', 'Present', TRUE, 'Fine-tuned LLM architectures and deployed real-time transformer models on AWS with Docker.'),
(4, 'OmniWeb', 'Full-Stack Engineer', '2022-04', 'Present', TRUE, 'Implemented React frontend components and Flask backend services with MySQL storage.'),
(5, 'PrimeCloud', 'Senior Backend Engineer', '2021-05', 'Present', TRUE, 'Engineered high-concurrency microservices in Flask and MySQL. Automated CI/CD deployments.');

-- 8. Candidate Education
INSERT INTO candidate_education (candidate_id, degree, institution, field_of_study, graduation_year, grade) VALUES
(1, 'Bachelor of Science', 'New York University', 'Computer Science', '2019', '3.8 GPA'),
(2, 'Bachelor of Science', 'San Jose State University', 'Software Engineering', '2020', '3.7 GPA'),
(3, 'Master of Science', 'Northeastern University', 'Artificial Intelligence', '2020', '3.9 GPA'),
(4, 'Bachelor of Science', 'University of California, Davis', 'Computer Science', '2021', '3.6 GPA'),
(5, 'Master of Science', 'University of Washington', 'Computer Science', '2019', '3.9 GPA');

-- 9. Candidate Projects
INSERT INTO candidate_projects (candidate_id, project_title, description, technologies_used) VALUES
(1, 'Enterprise Payment Microservice', 'Built a scalable payment processing gateway with Flask, MySQL transactions, and Redis distributed locks.', 'Python, Flask, MySQL, Redis, Docker'),
(1, 'Asynchronous Event Dispatcher', 'High-throughput event queue worker system processing over 10,000 tasks/second.', 'Python, RabbitMQ, MySQL'),
(2, 'SaaS Analytics Dashboard', 'Interactive analytics dashboard with dynamic filtering, dark mode, and real-time Chart.js visual graphs.', 'React, TypeScript, Bootstrap 5, Chart.js'),
(3, 'Multi-Document AI Summarizer', 'NLP summarization engine utilizing PyTorch, transformer fine-tuning, and semantic chunking.', 'Python, PyTorch, HuggingFace, Docker'),
(4, 'E-Commerce Marketplace', 'Full-stack retail application with React single-page app and Flask REST API backend.', 'React, Python, Flask, MySQL'),
(5, 'Cloud Monitoring Orchestrator', 'Microservices health check and auto-recovery service with alerting.', 'Python, Flask, Docker, AWS');

-- 10. Candidate Certifications
INSERT INTO candidate_certifications (candidate_id, name, issuing_organization, issue_date) VALUES
(1, 'AWS Certified Developer - Associate', 'Amazon Web Services', '2023-04'),
(1, 'Docker Certified Associate (DCA)', 'Docker Inc.', '2022-11'),
(2, 'Meta Certified Frontend Developer', 'Meta', '2022-06'),
(3, 'Deep Learning Specialization', 'DeepLearning.AI', '2021-09'),
(5, 'AWS Certified Solutions Architect', 'Amazon Web Services', '2023-01');

-- 11. Job Applications
INSERT INTO job_applications (job_id, candidate_id, applied_at, status, notes) VALUES
(1, 1, '2025-01-10 10:30:00', 'Shortlisted', 'Strong match for senior backend requirements.'),
(1, 4, '2025-01-12 14:15:00', 'Screening', 'Good fullstack experience, evaluate Python depth.'),
(1, 5, '2025-01-08 09:00:00', 'Interviewing', 'Exceptional backend qualifications and MySQL expertise.'),
(2, 2, '2025-01-11 11:20:00', 'Shortlisted', 'Excellent React frontend portfolio.'),
(2, 4, '2025-01-14 16:45:00', 'Interviewing', 'Full-stack experience matches both React and Flask stack.'),
(3, 3, '2025-01-09 13:00:00', 'Interviewing', 'Top candidate for NLP and PyTorch model development.'),
(4, 2, '2025-01-15 15:30:00', 'Shortlisted', 'Direct match for React developer role.'),
(5, 6, '2025-01-13 10:00:00', 'Screening', 'Strong Kubernetes and Terraform skills.');

-- 12. Candidate Matches (5-Factor Weighted Score)
INSERT INTO candidate_matches (job_id, candidate_id, overall_score, skills_score, experience_score, education_score, project_score, preferred_skills_score, matched_skills, missing_skills, partial_skills, strengths, weaknesses, ai_explanation, recommendation) VALUES
(1, 1, 94.00, 96.00, 95.00, 90.00, 95.00, 90.00, 
'["Python", "Flask", "MySQL", "REST API", "Docker", "Git", "Redis", "AWS"]',
'[]',
'[]',
'Outstanding mastery of Python, Flask, and relational MySQL database optimization. 5.5 years of directly relevant experience exceeds the 5-year requirement. Has published projects involving high-throughput payment architectures.',
'Minimal exposure to Kubernetes container orchestration; however, Docker mastery is proven.',
'Candidate Rahul Sharma is an exemplary match for the Senior Python/Flask Backend Engineer role. Qualifications align strongly with core system architecture and database design needs.',
'Strong Match'),

(1, 4, 76.00, 75.00, 70.00, 85.00, 80.00, 70.00,
'["Python", "Flask", "MySQL", "REST API", "Git"]',
'["Docker"]',
'["Redis", "AWS"]',
'Solid grasp of Python web development and relational databases. Experience with both frontend and backend makes for good versatility.',
'Missing production Docker containerization experience. Has 3.5 years experience compared to the 5+ years preferred for the senior level.',
'Candidate David Miller displays promising full-stack foundations with Python and Flask, but has a skill gap in Docker containerization and slightly less total senior experience.',
'Potential Match'),

(1, 5, 96.50, 98.00, 95.00, 95.00, 95.00, 95.00,
'["Python", "Flask", "MySQL", "REST API", "Docker", "Redis", "AWS", "Git"]',
'[]',
'[]',
'Extensive 5-year track record in enterprise Python/Flask microservices, master-slave MySQL database architecture, and cloud deployments on AWS.',
'None identified in core job competencies.',
'Candidate Ananya Iyer meets or exceeds every required and preferred qualification for the Senior Python/Flask Backend Engineer role.',
'Strong Match'),

(2, 4, 88.00, 90.00, 85.00, 85.00, 90.00, 85.00,
'["Python", "Flask", "React", "JavaScript", "HTML5", "CSS3", "MySQL", "Git"]',
'["Docker"]',
'["TypeScript"]',
'Proven end-to-end full-stack capabilities across both React on the frontend and Flask on the backend.',
'TypeScript and Docker skills could be strengthened through onboarding.',
'Candidate David Miller is a high-potential fit for the Full-Stack Software Engineer role.',
'Strong Match'),

(3, 3, 93.50, 95.00, 90.00, 98.00, 95.00, 90.00,
'["Python", "PyTorch", "NLP", "Scikit-Learn", "LLM Integration", "Docker", "Git"]',
'[]',
'["Vector Databases", "TensorFlow"]',
'Strong research and practical background in NLP and transformer fine-tuning. Holds an M.S. in Artificial Intelligence.',
'Slightly lower experience in dedicated vector database optimization.',
'Candidate Alex Mercer is exceptionally qualified for the AI/ML Specialist position.',
'Strong Match');

-- 13. Interview Questions
INSERT INTO interview_questions (job_id, candidate_id, category, difficulty, question_text, expected_skills) VALUES
(1, 1, 'Technical', 'Medium', 'How does Flask manage the application and request context under concurrent gunicorn worker threads?', 'Flask, Concurrency, WSGI'),
(1, 1, 'Technical', 'Hard', 'Explain how you would diagnose and eliminate slow queries in MySQL using EXPLAIN ANALYZE and composite indexing.', 'MySQL, Indexing, Performance'),
(1, 1, 'Project-Based', 'Medium', 'In your Enterprise Payment Microservice project, how did you prevent race conditions and duplicate debits using Redis distributed locks?', 'Redis, Distributed Systems, Python'),
(1, 1, 'Behavioral', 'Medium', 'Describe a situation where you had to push back on an unrealistic product deadline due to technical debt concerns. How did you negotiate?', 'Communication, Leadership'),
(1, 1, 'Situational', 'Hard', 'If our production Flask API experiences a sudden 10x traffic spike causing database connection exhaustion, what immediate and architectural steps would you take?', 'System Design, Connection Pooling, Caching'),
(1, 1, 'Skill Gap', 'Medium', 'Your profile shows strong Docker container experience. What is your approach to multi-stage Docker builds to reduce image attack surfaces and sizes?', 'Docker, Security, Optimization'),

(1, 4, 'Technical', 'Medium', 'What are the main architectural differences between Flask Blueprints and Django Apps, and when would you choose Flask for an enterprise service?', 'Python, Flask, Architecture'),
(1, 4, 'Skill Gap', 'Medium', 'The job requires Docker containerization for CI/CD deployments. How would you containerize a Flask app with MySQL and run it locally with docker-compose?', 'Docker, DevOps, MySQL'),
(1, 4, 'Project-Based', 'Medium', 'Tell us about the architecture of your E-Commerce Marketplace project. How did you structure your REST API endpoints for inventory updates?', 'React, Flask, REST API');

-- 14. Interviews
INSERT INTO interviews (id, candidate_id, job_id, scheduled_date, scheduled_time, interview_type, interviewer_name, status, notes) VALUES
(1, 1, 1, '2025-01-20', '14:00:00', 'Technical', 'Sarah Jenkins & Principal Architect', 'Completed', 'Deep-dive technical assessment into Python internals and MySQL optimization.'),
(2, 4, 1, '2025-01-22', '10:30:00', 'Technical', 'Michael Chang', 'Scheduled', 'First round technical and project review.'),
(3, 5, 1, '2025-01-21', '15:00:00', 'Managerial', 'Admin User (HR Director)', 'Completed', 'Final leadership and architectural alignment interview.'),
(4, 3, 3, '2025-01-23', '11:00:00', 'Technical', 'Sarah Jenkins', 'Scheduled', 'Assessment of NLP algorithms and LLM pipeline engineering.');

-- 15. Interview Evaluations
INSERT INTO interview_evaluations (interview_id, candidate_id, job_id, technical_score, communication_score, problem_solving_score, project_knowledge_score, role_fit_score, confidence_score, overall_score, strengths, weaknesses, notes, final_recommendation) VALUES
(1, 1, 1, 5, 4, 5, 5, 5, 4, 93.33,
'Exceptional command of Python, Flask WSGI lifecycle, and MySQL indexing mechanisms. Answered database concurrency questions with clarity and precision. Clearly understood real-world scalability trade-offs.',
'Could improve on articulating high-level DevOps orchestration (Kubernetes), though easily trainable.',
'Strongly recommended for the Senior Backend Engineer role. Candidate demonstrated immediate ability to elevate our backend engineering standards.',
'Strongly Recommend'),

(3, 5, 1, 5, 5, 5, 5, 5, 5, 96.67,
'Outstanding communication, comprehensive technical knowledge of Python and distributed microservices, and excellent cultural leadership fit.',
'None of note.',
'Ananya gave one of the best technical and leadership interviews this quarter. Candidate was extended an offer.',
'Strongly Recommend');
