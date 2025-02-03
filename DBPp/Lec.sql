-- -- Active: 1738051755016@@127.0.0.1@3306@cs
-- CREATE DATABASE cs;

-- CREATE TABLE emp()

-- -- SHOW TABLES;

-- -- SELECT * FROM emp;

-- -- SELECT empno, ename, salary FROM emp;

-- -- SELECT empno, salary, job FROM emp WHERE job='clerk';

-- -- SELECT job FROM emp;

-- -- SELECT DISTINCT job FROM emp;

-- -- SELECT * FROM emp;

-- -- SELECT empno, ename, salary, salary/12 FROM emp;

-- -- SELECT empno, ename, salary, ROUND(salary/12,2) AS monthly_sal FROM emp;

-- -- SELECT empno, ename, salary, ROUND(salary/12) AS monthly_sal FROM emp;

-- -- SELECT * FROM emp;

-- -- SELECT empno, job, salary, salary*1.1 AS Sal_incr FROM emp WHERE job='clerk';

-- -- SELECT * FROM emp WHERE salary>40000;

-- -- SELECT * FROM emp WHERE ename>'mark';

-- -- SELECT * FROM emp WHERE ename<'mark';

-- -- SELECT * FROM emp WHERE salary BETWEEN 30000 AND 50000;

-- -- SELECT * FROM emp WHERE salary > 30000 AND salary < 50000;

-- -- SELECT * FROM emp WHERE job IN ('manager', 'teacher');

-- -- SELECT * FROM emp WHERE job NOT IN ('manager', 'teacher');

-- -- -- Pattern matching 
-- --     ename like 'b%';
-- --     ename like '%n';

-- --     ename like '_,_,_,_,_';

-- --     ename like '%b%';

-- -- SELECT * FROM emp WHERE ename LIKE 's%';

-- -- SELECT * FROM emp WHERE ename LIKE '%k';

-- -- SELECT * FROM emp WHERE ename LIKE '____';

-- -- SELECT * FROM emp WHERE ename LIKE '_____';

-- -- SELECT * FROM emp WHERE ename IS NULL;

-- -- SELECT * FROM emp WHERE ename IS NOT NULL;

-- -- SELECT * FROM emp WHERE job='manager' AND deptno=30;

-- SELECT * FROM emp WHERE job='manager' OR deptno=30;

-- SELECT ename FROM emp ORDER BY ename DESC;

-- SELECT job, salary FROM emp ORDER BY job , salary DESC;

-- SELECT job, salary FROM emp ORDER BY salary , job DESC;

-- SELECT salary, job FROM emp ORDER BY salary , job DESC;

-- SELECT salary, job FROM emp ORDER BY salary , job;

-- AGGREGATE FUNCTIONS=[SUM, COUNT, MAX, MIN, AVERAGE]

-- SELECT COUNT(*) FROM emp WHERE job='teacher';

-- SELECT COUNT(*) FROM emp WHERE job='manager';

-- SELECT COUNT(*), SUM(salary) FROM emp WHERE job='manager';








