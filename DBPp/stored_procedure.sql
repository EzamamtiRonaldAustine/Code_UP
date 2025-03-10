-- Active: 1738051755016@@127.0.0.1@3306@bscs
-- Stored procedure: is a prepared SQL code that can be saved/stored  within the DBMS
-- and reused when needed
-- syntax
-- Create procedure name(_,_,_)
-- Begin
-- select * from employee where job = ID
-- end/ or end;

-- / @ delimiter /


DELIMITER /

CREATE PROCEDURE teachers()

BEGIN
SELECT * FROM employee WHERE job = 'teacher';

end/

DROP PROCEDURE teachers;

CALL teachers()/

CREATE PROCEDURE jobtype(in id1 VARCHAR(20))
BEGIN
SELECT * FROM employee WHERE job = id1;

end/

CALL jobtype('manager')/

CALL jobtype('clerk')/

CALL jobtype('teacher')/

SELECT * FROM employee;

UPDATE employee SET job = "Teacher" WHERE EmpNo = 'E003';

CREATE PROCEDURE jobsum(in id2 VARCHAR(20))
BEGIN
SELECT SUM(salary) AS Total_amount FROM employee WHERE job = id2;

end/

DROP PROCEDURE jobsum;

CALL jobsum('manager')/


