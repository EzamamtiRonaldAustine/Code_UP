-- Active: 1738051755016@@127.0.0.1@3306@bscs
USE BSCS;;
SHOW TABLES;

SELECT * FROM employee;

SELECT empno, ename, job, salary, CASE WHEN salary > 50000 THEN 'corporate' 
WHEN salary >= 40000 AND salary <= 50000  THEN 'intermediate'
WHEN salary >= 30000 AND salary <= 40000  THEN 'junior entrant' ELSE 'interns' 
END AS  salary_comment FROM employee;

CREATE VIEW emp_sal_comment AS SELECT empno, ename, job, salary, 
CASE WHEN salary > 50000 THEN 'corporate' 
WHEN salary >= 40000 AND salary <= 50000  THEN 'intermediate'
WHEN salary >= 30000 AND salary <= 40000  THEN 'junior entrant' ELSE 'interns' 
END AS  salary_comment FROM employee;

SELECT * FROM emp_sal_comment;

SELECT * FROM employee;

SELECT empno, ename, job, salary, CASE WHEN job ='teacher' THEN salary*1.12
WHEN job ='manager' THEN salary*1.05 WHEN job ='clerk' THEN salary*1.10
ELSE salary*1.08 END AS salary_increment from employee;

SHOW TABLES;

-- UPDATE STUDENT SET ADDRESS='GULU', NAME 

-- START TRANSACTION;

-- SELECT * FROM employee;

-- UPDATE student set address = 'masindi' WHERE rengno='s004';

-- ROLLBACK;

-- START TRANSACTION;

-- DML LANG

-- COMMIT; YOU CANT ROLL BACK THE CHANGES AFTER THIS

START TRANSACTION;

SELECT * FROM employee;
UPDATE employee SET salary = salary*1.12 WHERE job ='teacher';

UPDATE employee SET salary = salary*1.05 WHERE job ='manager';
UPDATE employee SET salary = CASE WHEN job ='clerk' THEN salary*1.10
ELSE salary*1.08 END;

SELECT * FROM employee;

ROLLBACK;
SELECT * FROM employee;


START TRANSACTION;


UPDATE employee SET salary = CASE WHEN job ='teacher' THEN salary*1.12
WHEN job ='manager' THEN salary*1.05 WHEN job ='clerk' THEN salary*1.10
ELSE salary*1.08 END;

SELECT * FROM employee;

COMMIT;

SELECT * FROM employee;

CREATE TABLE doctor(did VARCHAR(20) PRIMARY key, dname VARCHAR(20), speciality VARCHAR(20));
INSERT INTO doctor VALUES ('d001', 'Peter', 'ENT'), ('d002', 'Mary',  'optician'), 
('d003', 'Henry', 'urologist') ;


CREATE TABLE patient(pid VARCHAR(20) PRIMARY KEY, address VARCHAR(20), 
gender CHAR(1), DID VARCHAR(20), CONSTRAINT FOREIGN KEY(DID) REFERENCES DOCTOR(DID) 
ON UPDATE CASCADE ON  DELETE CASCADE);

INSERT INTO patient VALUES ('P001', 'Kla', 'M', 'D001'), 
('P002', 'Entebbe', 'M', 'D002'), ('P003', 'Masindi', 'F', 'D003');

SELECT doctor.did, doctor.speciality, patient.pid, patient.gender FROM doctor
, patient WHERE doctor.did = patient.did;

CREATE VIEW doc_patient AS SELECT doctor.did, doctor.speciality, patient.pid, patient.gender FROM doctor
, patient WHERE doctor.did = patient.did;

SELECT d.*, p.* FROM doctor d, patient p WHERE d.did = p.did;


SELECT d.*, p.* FROM doctor d LEFT JOIN patient p ON d.did = p.did;

CREATE VIEW left_join AS SELECT d.*, p.* FROM doctor d LEFT JOIN patient p ON d.did = p.did;


