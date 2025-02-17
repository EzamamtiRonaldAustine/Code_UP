-- Active: 1738051755016@@127.0.0.1@3306@bscs
-- CREATE DATABASE bscs2;

CREATE TABLE doctor(did VARCHAR(20) PRIMARY key, dname VARCHAR(20), speciality VARCHAR(20));

DESC doctor;
ALTER TABLE doctor drop PRIMARY KEY;

DESC doctor;

ALTER TABLE doctor add PRIMARY KEY(did);

DESC doctor;

ALTER TABLE doctor add COLUMN address VARCHAR(20) AFTER dname;

DESC doctor;

ALTER TABLE doctor ADD COLUMN telno INT;

DESC doc;

ALTER TABLE doc DROP telno;

ALTER TABLE doctor RENAME COLUMN did TO doc_id;

DESC doctor;

ALTER TABLE doctor MODIFY dname VARCHAR(40);

RENAME TABLE doctor TO doc;

DESC doctor;

DESC doc;

INSERT INTO doc(doc_id, dname) VALUES ("d001", 'peter');

SELECT * FROM doc;

INSERT INTO doc VALUES ('d002', 'mary', 'kla', 'ENT');

INSERT INTO doc VALUES ('d003', 'John', 'mukono', 'optician'), 
('d004', 'mathew', 'ebbs', 'urologist');


SELECT * FROM doc;

CREATE TABLE patient(pid VARCHAR(20) PRIMARY KEY, pname VARCHAR(20), gender CHAR(1), DOB DATE, doc_id VARCHAR(20), 
FOREIGN KEY(doc_id) REFERENCES doc(doc_id));

DESC patient;

INSERT INTO patient VALUES ('P001', 'JAMES', 'M', '1990-10-10', 'D002');

SELECT * FROM patient;



