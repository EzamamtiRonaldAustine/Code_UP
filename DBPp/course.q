-- Active: 1738051755016@@127.0.0.1@3306@bscs2
USE bscs2;

CREATE TABLE programme(PID VARCHAR(20) PRIMARY KEY, PNAME VARCHAR(20));
DESC programme;

INSERT INTO programme VALUES ('P001','CS'), ('P002','IT'), ('P003','DS');

SELECT * FROM programme;

CREATE TABLE student(S_ID VARCHAR(20) PRIMARY KEY, S_NAME VARCHAR(20), gender CHAR(1), PID VARCHAR(20),
FOREIGN KEY (PID) REFERENCES programme(PID));

DESC student;


INSERT INTO student VALUES ('S001', 'SIMON', 'M', 'P003'), ('S002', 'MARY', 'F', 'P001'),
('S003', 'JOHN', 'M', 'P002');

SELECT * FROM student;

ALTER TABLE student ADD COLUMN DOB DATE;

DESC student;   

ALTER TABLE student RENAME COLUMN S_ID TO student_ID;

DESC student;

ALTER TABLE student RENAME COLUMN S_NAME TO SNAME;

DESC student;

SELECT * FROM student WHERE gender = 'M';

ALTER TABLE patient MODIFY PID VARCHAR(20);

SELECT * FROM student LIMIT 2;