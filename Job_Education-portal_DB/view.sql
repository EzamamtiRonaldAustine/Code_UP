
USE JobPortal;
-- VIEWS
-- View to see currently open jobs with school name
CREATE VIEW OpenJobs AS
SELECT 
    j.job_id, j.title, j.subject, j.deadline, s.name AS school_name
FROM 
    Job j
JOIN School s ON j.school_id = s.school_id
WHERE 
    j.status = 'open';


-- View to manage users
CREATE VIEW ManageUsers AS
SELECT teacher_id AS id, full_name AS name, email, role AS user_type FROM Teacher
UNION
SELECT school_id, name, email, role FROM School
UNION
SELECT admin_id, username, email, role FROM Admin;

-- View for Active Users
CREATE VIEW ActiveUsersView AS
SELECT school_id AS id, name, email, role AS user_type FROM School WHERE status = 'active';

SELECT * FROM OpenJobs;

SELECT * FROM ManageUsers;

SELECT * FROM ActiveUsersView;