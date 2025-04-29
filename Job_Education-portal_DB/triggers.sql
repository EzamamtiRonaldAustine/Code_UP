-- Active: 1738051755016@@127.0.0.1@3306@jobportal
USE JobPortal;
-- TRIGGERS
-- Triggers are stored programs that are automatically executed
-- when a specified event (such as INSERT, UPDATE, DELETE) occurs on a particular table. 
-- They are used to enforce business rules, maintain referential integrity, and automate tasks.

-- CREATE TRIGGER trigger_name
-- {BEFORE | AFTER} {INSERT | UPDATE | DELETE} ON table_name
-- FOR EACH ROW
-- BEGIN
--     -- Trigger body (SQL statements)
-- END;


DELIMITER $$

-- Trigger: Prevent duplicate applications
CREATE TRIGGER prevent_duplicate_application
BEFORE INSERT ON Application
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM Application 
        WHERE teacher_id = NEW.teacher_id AND job_id = NEW.job_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'You have already applied for this job.';
    END IF;
END;$$

-- Trigger: Notify school after job application
CREATE TRIGGER AfterJobApplication
AFTER INSERT ON Application
FOR EACH ROW
BEGIN
    DECLARE schoolId INT;
    SELECT school_id INTO schoolId FROM Job WHERE job_id = NEW.job_id;

    INSERT INTO Notification (recipient_id, recipient_type, message)
    VALUES (schoolId, 'school', CONCAT('A new application was submitted by teacher ID: ', NEW.teacher_id));
END;$$

-- Trigger: Notify teacher when application is accepted or rejected
CREATE TRIGGER NotifyTeacherOnStatusChange
AFTER UPDATE ON Application
FOR EACH ROW
BEGIN
    IF NEW.status = 'accepted' AND OLD.status != 'accepted' THEN
        INSERT INTO Notification (recipient_id, recipient_type, message)
        VALUES (NEW.teacher_id, 'teacher', CONCAT('Your application for job ID ', NEW.job_id, ' has been accepted.'));
    ELSEIF NEW.status = 'rejected' AND OLD.status != 'rejected' THEN
        INSERT INTO Notification (recipient_id, recipient_type, message)
        VALUES (NEW.teacher_id, 'teacher', CONCAT('Your application for job ID ', NEW.job_id, ' has been rejected.'));
    END IF;
END;$$
DELIMITER ;

-- application status updates to trigger notifications to teacher
UPDATE Application SET status = 'accepted' WHERE teacher_id = 1 AND job_id = 1;
UPDATE Application SET status = 'rejected' WHERE teacher_id = 1 AND job_id = 2;

-- View Notifications
SELECT * FROM Notification;