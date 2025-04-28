USE JobPortal;

-- ROLES AND PERMISSIONS


-- Scenario: Teacher trying to post a job
-- Login in as 'teacher_user'@'localhost' and attempting:
INSERT INTO Job (school_id, title, subject, description, deadline) VALUES (1, 'Physics Teacher', 'Physics', 'Physics classes for A-Level', '2025-06-01');

-- Scenario: School posts a job 
-- Login in as 'school_user'@'localhost' and run:
CALL PostJob(1, 'English Teacher Needed', 'English', 'Teach English to O-Level', '2025-05-15');

-- Scenario: Admin views all data (should succeed)
-- Login in as 'admin_user'@'localhost' and run:
 SELECT * FROM Application;
 SELECT * FROM Job;
 DELETE FROM Teacher WHERE teacher_id = 4;
  

-- Scenario: Teacher views open jobs 
-- Login  in as 'teacher_user'@'localhost' and run:
 SELECT * FROM OpenJobs;