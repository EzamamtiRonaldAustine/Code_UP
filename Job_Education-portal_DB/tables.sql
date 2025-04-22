-- Drop and Recreate Database
-- DROP DATABASE IF EXISTS JobPortal;
CREATE DATABASE JobPortal;
USE JobPortal;

-- Table: Admin
CREATE TABLE Admin (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    admin_password VARCHAR(256) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    role VARCHAR(20) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: School
CREATE TABLE School (
    school_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    email VARCHAR(100) UNIQUE NOT NULL,
    school_password VARCHAR(256),
    contact_phone VARCHAR(20),
    location VARCHAR(100),
    status ENUM('active', 'inactive') DEFAULT 'active',
    role VARCHAR(20) DEFAULT 'school',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Teacher
CREATE TABLE Teacher (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    tr_password VARCHAR(256) NOT NULL,
    subject_area VARCHAR(100),
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'teacher',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Job
CREATE TABLE Job (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    school_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    description TEXT,
    job_type ENUM('full-time', 'part-time') DEFAULT 'full-time',
    posted_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    deadline DATE NOT NULL,
    status ENUM('open', 'closed') DEFAULT 'open',
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES School(school_id)
);

-- Table: Application
CREATE TABLE Application (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    job_id INT NOT NULL,
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cover_letter TEXT,
    status ENUM('submitted', 'rejected', 'accepted') DEFAULT 'submitted',
    FOREIGN KEY (teacher_id) REFERENCES Teacher(teacher_id),
    FOREIGN KEY (job_id) REFERENCES Job(job_id)
);

-- Table: Notification
CREATE TABLE Notification (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    recipient_id INT,
    recipient_type ENUM('teacher', 'school', 'admin'),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);


