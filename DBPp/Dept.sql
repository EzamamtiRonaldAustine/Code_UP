-- Active: 1738051755016@@127.0.0.1@3306@bscs

CREATE DATABASE BSCS;

CREATE TABLE department(DeptNo INT PRIMARY KEY, DName VARCHAR(30), Loc VARCHAR(30));


CREATE TABLE employee(EmpNo VARCHAR(20) PRIMARY KEY, Ename VARCHAR(30), Job VARCHAR(30), Salary INT, DeptNo INT, 
FOREIGN KEY(DeptNo) REFERENCES department(DeptNo));

SHOW TABLES;


INSERT INTO department VALUES (10,'SALES','KAMPALA');

INSERT INTO department VALUES (40,'MARKETING',	'ENTEBBE'),
(30,	'ACCOUNTING', 'MUKONO');

SELECT * FROM department;

INSERT INTO employee VALUES 
('E001', NULL, 'Clerk', 40000, 30),
('E002', 'Agaba', 'Manager', 16000, 30),
('E003', 'Mary', 'SalesLady', 20000, 10),
('E004', 'Timo', 'Clerk', 40000, 30),
('E005', 'Simon', 'Manager', 60000, 40),
('E006', 'Mark', 'Manager', 45000, 10),
('E007', 'Solomon', 'Teacher', 30000, 30);

-- DELETE FROM employee;
-- DROP TABLE employee;

SELECT * FROM employee