-- Active: 1738051755016@@127.0.0.1@3306@jobportal

USE JobPortal;
-- ROLES AND USERS FOR SECURITY

-- Creating roles
CREATE ROLE 'admin_role';
CREATE ROLE 'school_role';
CREATE ROLE 'teacher_role';

-- Granting privileges to each role

-- Admin: full control
GRANT ALL PRIVILEGES ON JobPortal.* TO 'admin_role';

-- School: can manage jobs and see applications/notifications
GRANT SELECT, INSERT, UPDATE ON JobPortal.Job TO 'school_role';
GRANT SELECT, INSERT ON JobPortal.Notification TO 'school_role';
GRANT SELECT ON JobPortal.Application TO 'school_role';

-- Teacher: can view jobs, apply, and view their applications/notifications
GRANT SELECT ON JobPortal.Job TO 'teacher_role';
GRANT SELECT, INSERT, UPDATE ON JobPortal.Application TO 'teacher_role';
GRANT SELECT ON JobPortal.Notification TO 'teacher_role';

-- Start here
-- user accounts
CREATE USER 'admin_user'@'localhost' IDENTIFIED BY 'admin456';
CREATE USER 'school_user'@'localhost' IDENTIFIED BY 'school456';
CREATE USER 'teacher_user'@'localhost' IDENTIFIED BY 'teacher456';


-- Assign roles to users
GRANT 'admin_role' TO 'admin_user'@'localhost';
GRANT 'school_role' TO 'school_user'@'localhost';
GRANT 'teacher_role' TO 'teacher_user'@'localhost';

--- Set default role
SET DEFAULT ROLE admin_role TO 'admin_user'@'localhost';
SET DEFAULT ROLE school_role TO 'school_user'@'localhost';
SET DEFAULT ROLE teacher_role TO 'teacher_user'@'localhost';


-- Checking the roles assigned to users
SHOW GRANTS FOR 'admin_user'@'localhost';
SHOW GRANTS FOR 'school_user'@'localhost';
SHOW GRANTS FOR 'teacher_user'@'localhost';

-- Checking the privileges of each role
SHOW GRANTS FOR 'admin_role';
SHOW GRANTS FOR 'school_role';
SHOW GRANTS FOR 'teacher_role';