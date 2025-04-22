USE JobPortal;


INSERT INTO Admin (username, admin_password, email, role)
VALUES ('admin1', SHA2('admin1', 256), 'admin1@gmail.com', 'admin'),
       ('admin2', SHA2('admin12', 256), 'admin2@gmail.com', 'admin'),
       ('admin3', SHA2('admin13', 256), 'admin3@gmail.com', 'admin');

-- Teachers
INSERT INTO Teacher (full_name, email, tr_password, phone, role) VALUES
('Mary Jane', 'jane@gmail.com', SHA2('jane123', 256), '0700987654', 'teacher'),
('Will Smith', 'will@gmail.com', SHA2('will123', 256), '0700876543', 'teacher'),
('Simon Peter', 'peter@gmail.com', SHA2('peter123', 256), '0701234567', 'teacher'),
('Bruce Lee', 'Lee@gmail.com', SHA2('lee123', 256), '0707654321', 'teacher');

-- Schools
INSERT INTO School (name, email, school_password, location, role) VALUES
('Green Hill High', 'greenhill@gmail.com', SHA2('school1', 256), 'Kampala', 'school'),
('Lakeview Academy', 'lakeview@gmail.com', SHA2('school2', 256), 'Entebbe', 'school');


SELECT * FROM Admin;
SELECT * FROM Teacher;
SELECT * FROM School;
SELECT * FROM Job;

SELECT * FROM Application;
