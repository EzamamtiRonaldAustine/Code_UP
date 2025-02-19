-- Active: 1738051755016@@127.0.0.1@3306@cs
CREATE DATABASE CS;

CREATE TABLE department(DeptNo INT PRIMARY KEY, DName VARCHAR(30), Loc VARCHAR(30));


CREATE TABLE employee(EmpNo VARCHAR(20) PRIMARY KEY, Ename VARCHAR(30), Job VARCHAR(30), Salary INT, DeptNo INT, 
FOREIGN KEY(DeptNo) REFERENCES department(DeptNo));

SHOW TABLES;


INSERT INTO department VALUES (10,'SALES','KAMPALA');

INSERT INTO department VALUES (40,'MARKETING',	'ENTEBBE'),
(30,	'ACCOUNTING', 'MUKONO');

SELECT * FROM department;

DESCRIBE department;

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

-- DROP VIEW view_d; 

SELECT * FROM employee;

CREATE VIEW view_d AS SELECT * FROM employee WHERE DeptNo=30;


CREATE VIEW view_e AS SELECT Job, COUNT(*) AS NumEmployees FROM Employee GROUP BY Job;


SELECT * FROM view_e;

CREATE VIEW view_f AS SELECT * FROM employee WHERE Ename LIKE 'T%';

CREATE VIEW view_g AS SELECT DISTINCT job FROM employee ORDER BY job DESC;

SELECT * FROM view_g;

SELECT DISTINCT job FROM employee ORDER BY job;

CREATE VIEW view_h AS SELECT Job, SUM(Salary) AS TotalSalary FROM Employee GROUP BY Job;

SELECT * FROM  view_h;

SELECT Job, SUM(Salary) AS TotalSalary FROM Employee GROUP BY Job

-- i/

-- j
CREATE VIEW view_j AS SELECT Job, AVG(Salary) AS AvgSalary FROM Employee 
GROUP BY Job HAVING AVG(Salary) > 50000;

SELECT Job, AVG(Salary) AS AvgSalary FROM Employee 
GROUP BY Job; 
SELECT * FROM view_j;

ALTER TABLE DEPARTMENT ADD COLUMN Location VARCHAR(100);

DESC department;

ALTER TABLE DEPARTMENT MODIFY DName VARCHAR(50);

SHOW FULL TABLES WHERE Table_Type = 'BASE TABLE';
SHOW FULL TABLES WHERE Table_Type = 'VIEW';



CREATE VIEW view_n AS 
SELECT EmpNo, EName, DeptNo, CASE WHEN DeptNo = 10 THEN 'Computing' 
WHEN DeptNo = 30 THEN 'Business' WHEN DeptNo = 40 THEN 'Marketing' ELSE 'N/A' 
END AS DepartmentName FROM Employee;



CREATE VIEW view_o AS 
SELECT EmpNo, EName, Salary, CASE WHEN DeptNo = 10 THEN Salary * 1.08 
WHEN DeptNo = 30 THEN Salary * 0.88 WHEN DeptNo = 40 THEN Salary * 1.10 
ELSE Salary END AS AdjustedSalary FROM Employee;

SELECT * FROM view_o;

START TRANSACTION;
UPDATE Employee SET Salary = 80000, Job = 'Cleaner' WHERE EmpNo = 'E004';

DELETE FROM Employee WHERE EmpNo = 'E002';

DESC Employee;

SELECT * FROM employee

ROLLBACK;

DESC Employee;

SELECT * FROM employee

SELECT * FROM employee WHERE job='manager' OR deptno=30;

SELECT ename FROM employee ORDER BY ename DESC;

SELECT job, salary FROM employee ORDER BY job , salary DESC;

SELECT job, salary FROM employee ORDER BY salary , job DESC;

SELECT salary, job FROM employee ORDER BY salary , job DESC;

SELECT salary, job FROM employee ORDER BY salary , job;


CREATE TABLE Project (
    ProjID INT PRIMARY KEY AUTO_INCREMENT,
    ProjName VARCHAR(100) NOT NULL,
    DeptNo INT, 
    FOREIGN KEY (DeptNo) REFERENCES department(DeptNo)
);

-- ALTER TABLE Project ADD COLUMN AssignedDate DATE, ADD COLUMN role ENUM

ALTER TABLE project ADD COLUMN EmpNo VARCHAR(20), ADD FOREIGN KEY (EmpNo) REFERENCES employee(EmpNo);

INSERT INTO project(ProjName, DeptNo, EmpNo) VALUES
    ("Sales Boost", 10, "E003"),
    ("Marketing Expansion", 40, "E005"),
    ("Accounting Automation", 30, "E007"),
    ("Sales Strategy", 10, "E006");

SELECT * FROM project;

SELECT * FROM department;

SELECT e.*, d.DName, d.Loc FROM employee e JOIN department d ON e.DeptNo = d.DeptNo;

SELECT p.ProjID, p.ProjName, d.DName, d.Loc FROM project p JOIN department d ON p.DeptNo = d.DeptNo;

SELECT e.EmpNo, e.Ename, e.Job, e.Salary, d.DName AS Department, p.ProjName AS Project
FROM employee e JOIN department d ON e.DeptNo = d.DeptNo JOIN project p ON d.DeptNo = p.DeptNo ;

SELECT p.ProjName AS Project, d.DName AS Department, e.Ename AS Employee, e.Job 
FROM project p JOIN department d ON p.DeptNo = d.DeptNo JOIN employee e ON d.DeptNo = e.DeptNo 
ORDER BY p.ProjName;







