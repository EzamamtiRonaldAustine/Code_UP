
USE JobPortal;

-- Admin table constraints
ALTER TABLE Admin ADD CONSTRAINT admin_email_format CHECK (email LIKE '%@%');
ALTER TABLE Admin ADD CONSTRAINT admin_username_length CHECK (LENGTH(username) BETWEEN 5 AND 50);
ALTER TABLE Admin ADD CONSTRAINT admin_role_check CHECK (role IN ('admin', 'super_admin'));

-- School table constraints
ALTER TABLE School ADD CONSTRAINT school_email_format CHECK (email LIKE '%@%');

ALTER TABLE School ADD CONSTRAINT school_status_check CHECK (status IN ('active', 'inactive'));

-- Teacher table constraints
ALTER TABLE Teacher ADD CONSTRAINT teacher_email_format CHECK (email LIKE '%@%');
ALTER TABLE Teacher ADD CONSTRAINT teacher_phone_format CHECK (phone REGEXP '^[0-9]{10}$');
ALTER TABLE Teacher ADD CONSTRAINT teacher_role_check CHECK (role = 'teacher');

-- Job table constraints
ALTER TABLE Job ADD CONSTRAINT job_deadline_check CHECK (deadline > posted_on);
ALTER TABLE Job ADD CONSTRAINT job_status_check CHECK (status IN ('open', 'closed'));

-- Application table constraints
ALTER TABLE Application ADD CONSTRAINT app_status_check CHECK (status IN ('submitted', 'rejected', 'accepted'));

-- Notification table constraints
ALTER TABLE Notification ADD CONSTRAINT notif_recipient_check CHECK (recipient_type IN ('teacher', 'school', 'admin'));

-- View all constraints
SELECT 
    TABLE_NAME, 
    CONSTRAINT_NAME, 
    CONSTRAINT_TYPE 
FROM 
    information_schema.TABLE_CONSTRAINTS 
WHERE 
    TABLE_SCHEMA = 'JobPortal';

