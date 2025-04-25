-- Active: 1738051755016@@127.0.0.1@3306@jobportal

USE JobPortal;

-- STORED PROCEDURES
-- Stored procedures are precompiled SQL code that can be saved and executed multiple times. 
-- They are used to encapsulate and group SQL statements for reuse, 
-- improve performance, and enhance security by limiting direct access to tables.

-- CREATE PROCEDURE procedure_name(parameters)
-- BEGIN
--     -- Procedure body (SQL statements)
-- END;

DELIMITER $$

-- Procedure: Teacher login with SHA2 hash
CREATE PROCEDURE LoginUser(IN user_email VARCHAR(100), IN user_password VARCHAR(100))
BEGIN
    SELECT teacher_id, full_name
    FROM Teacher
    WHERE email = user_email AND tr_password = SHA2(user_password, 256);
END;$$

-- DROP PROCEDURE LoginUser;

-- Procedure: Reset user password (teacher only)
CREATE PROCEDURE ResetUserPassword(IN user_email VARCHAR(100), IN new_password VARCHAR(100))
BEGIN
    UPDATE Teacher
    SET tr_password = SHA2(new_password, 256)
    WHERE email = user_email;
END;$$

-- Procedure: Close expired jobs
CREATE PROCEDURE CloseExpiredJobs()
BEGIN
    UPDATE Job
    SET status = 'closed'
    WHERE deadline < CURRENT_DATE AND status = 'open';
END;$$

-- Procedure: Deactivate school
CREATE PROCEDURE DeactivateSchool(IN sid INT)
BEGIN
    UPDATE School
    SET status = 'inactive'
    WHERE school_id = sid;
END;$$



-- Procedure: Apply for a Job (Max 3 Applications)
CREATE PROCEDURE ApplyForJob (
    IN t_id INT, 
    IN j_id INT, 
    IN letter TEXT
)
BEGIN
    DECLARE total_apps INT;
    SELECT COUNT(*) INTO total_apps FROM Application WHERE teacher_id = t_id;

    IF total_apps < 6 THEN
        INSERT INTO Application (teacher_id, job_id, cover_letter)
        VALUES (t_id, j_id, letter);
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Application limit reached. You can only apply to 3 jobs.';
    END IF;
END;$$

-- Procedure: Post Job (Max 8 Jobs per School)
CREATE PROCEDURE PostJob (
    IN s_id INT, 
    IN title VARCHAR(100),
    IN subj VARCHAR(100), 
    IN descr TEXT, 
    IN due DATE
)
BEGIN
    DECLARE job_count INT;
    SELECT COUNT(*) INTO job_count FROM Job WHERE school_id = s_id;

    IF job_count < 8 THEN
        INSERT INTO Job (school_id, title, subject, description, deadline)
        VALUES (s_id, title, subj, descr, due);
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Posting limit reached. A school can only post up to 8 jobs.';
    END IF;
END;$$

-- CALL LoginUser(user_email, user_password);
-- CALL ResetUserPassword(user_email, new_password);
-- CALL CloseExpiredJobs();
-- CALL DeactivateSchool(1);

-- Jobs
CALL PostJob(1, 'Math Teacher Needed', 'Mathematics', 'Teach math to O-Level students', '2025-04-30');
CALL PostJob(2, 'Biology Substitute', 'Biology', 'Temporary biology teacher for Term 2', '2025-04-20');

CALL PostJob(1, 'English Substitute', 'English', 'Temporary English teacher for Term 2', '2025-04-20');

CALL PostJob(2, 'French Substitute', 'French', 'Temporary French teacher for Term 2', '2025-04-20');

CALL PostJob(2, 'Bi Substitute', 'Bi', 'Temporary biology teacher for Term 2', '2025-04-20');

CALL PostJob(2, 'En Substitute', 'En', 'Temporary English teacher for Term 2', '2025-04-20');

CALL PostJob(2, 'Fr Substitute', 'Fr', 'Temporary French teacher for Term 2', '2025-04-20');

CALL PostJob(2, 'F Substitute', 'F', 'Temporary French teacher for Term 2', '2025-04-20');


-- Applications
CALL ApplyForJob(1, 1, 'Excited to teach Math.');

CALL ApplyForJob(1, 2, 'I have experience in Biology.');

CALL ApplyForJob(1, 2, 'Love Biology.');


CALL ApplyForJob(2, 1, 'I am a qualified teacher.');

CALL LoginUser('peter@gmail.com', 'peter123')

