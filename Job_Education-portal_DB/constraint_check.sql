
USE JobPortal;
-- Test Admin table constraints 
BEGIN;
    -- Valid admin data
    INSERT INTO Admin (username, admin_password, email, role) 
    VALUES ('admin2', 'admin2', 'admin2@gmail.com', 'admin');
    
    -- Testing username length
    INSERT INTO Admin (username, admin_password, email, role) 
    VALUES ('adm', 'admin3', 'admin3@gmail.com', 'admin'); 
    
    -- Testing email format
    INSERT INTO Admin (username, admin_password, email, role) 
    VALUES ('admin4', 'admin4', 'invalid-email', 'admin'); 
    
    -- Testing role validation
    INSERT INTO Admin (username, password_hash, email, role) 
    VALUES ('admin5', 'admin5', 'admin4@gmail.com', 'invalid_role'); 
ROLLBACK;

-- Testing School table constraints
BEGIN;
    -- Valid school data
    INSERT INTO School (name, address, email, contact_phone, status)
    VALUES ('School2', 'Address2', 'school2@gmail.com', '074344535', 'active');
    
    -- status validation
    INSERT INTO School (name, address, email, contact_phone, status)
    VALUES ('School4', 'Address4', 'school4@gmail.com', '074344585', 'invalid_status'); 
ROLLBACK;

-- Testing Teacher table constraints
BEGIN;
    -- Valid teacher data
    INSERT INTO Teacher (full_name, email, tr_password, phone, role)
    VALUES ('Teacher1', 'teacher@email.com', 'tr1', '1234567890', 'teacher');
    
    -- phone format
    INSERT INTO Teacher (full_name, email, tr_password, phone, role)
    VALUES ('Teacher2', 'teacher2@email.com', 'tr2', 'invalid-phone', 'teacher'); 
    
    -- email format
    INSERT INTO Teacher (full_name, email, tr_password, phone, role)
    VALUES ('Teacher3', 'invalid-email', 'tr3', '1234567890', 'teacher'); 
    
    -- role validation
    INSERT INTO Teacher (full_name, email, tr_password, phone, role)
    VALUES ('Teacher4', 'teacher4@email.com', 'tr4', '1234554890', 'invalid_role'); 
ROLLBACK;

-- Testing Job table constraints
BEGIN;
    -- Setup: Insert a school for foreign key reference
    INSERT INTO School (name, email, status) VALUES ('Test School', 'school@gmail.com', 'active');
    
    -- deadline validation
    INSERT INTO Job (school_id, title, subject, description, deadline, status)
    VALUES (1, 'English Teacher', 'English', 'Description', DATE_SUB(CURDATE(), INTERVAL 1 DAY), 'open'); 
    
    -- Testing status validation
    INSERT INTO Job (school_id, title, subject, description, deadline, status)
    VALUES (1, 'Science Teacher', 'Science', 'Description', DATE_ADD(CURDATE(), INTERVAL 7 DAY), 'invalid_status'); 
ROLLBACK;


-- Testing Notification table constraints
BEGIN;
    -- Valid notification data
    INSERT INTO Notification (recipient_id, recipient_type, message)
    VALUES (1, 'teacher', 'Test message');
    
    -- Testing recipient_type validation
    INSERT INTO Notification (recipient_id, recipient_type, message)
    VALUES (1, 'invalid_type', 'Test message'); 
ROLLBACK;

SELECT 'All constraint tests completed' AS Test_Result;