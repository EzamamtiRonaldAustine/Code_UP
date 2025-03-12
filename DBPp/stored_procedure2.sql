CREATE DATABASE students;

use students;

CREATE TABLE student
(
    regno VARCHAR(20) PRIMARY KEY,
    fname VARCHAR(50),
    lname VARCHAR(50),
    fees INT
);

INSERT INTO student VALUES('e001', 'John', 'Cena', 20000),
('e002', 'Jon', 'Poe', 230000),
('e003', 'John', 'Don', 25000),
('e004', 'Jim', 'Bob', 270000),
('e005', 'Jane', 'Steve', 26000);

SELECT * FROM student;

delimiter /

CREATE PROCEDURE updatepro(in id1 VARCHAR(20), in id2 INT)
BEGIN
UPDATE student SET fees = id2 WHERE regno = id1;

end/

CALL updatepro('e004', 50000)/


SELECT * FROM student;


CREATE PROCEDURE delete_id(in id3 VARCHAR(20))
BEGIN
DELETE FROM student WHERE regno = id3;
end/

CALL delete_id('e005')/

SELECT * FROM student;

CREATE PROCEDURE insert_rows(in id4 VARCHAR(20),
    id5 VARCHAR(50),
    id6 VARCHAR(50),
    id7 INT)
BEGIN
INSERT INTO student VALUES(id4, id5, id6, id7);

end/

CALL insert_rows('e006', 'John', 'Doe', 30000)/

SELECT * FROM student;

SHOW PROCEDURE STATUS WHERE Db = 'students';