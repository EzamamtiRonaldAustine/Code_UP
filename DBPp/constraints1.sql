CREATE DATABASE cs2;

USE CS2;
CREATE TABLE Employee(
    EmployeeID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(50) NOT NULL, 
    LastName VARCHAR(50) NOT NULL, 
    Age INT CHECK(Age >= 18), 
    Email VARCHAR(120) UNIQUE
);


INSERT INTO Employee(FirstName, LastName, Age, Email)VALUES
("John",'Doe', 30, 'john.doe@yahoo.com'),
("James",'Pete', 40, 'jamesn.pete@yahoo.com'),
("John",'Carter', 30, 'john.cat@yahoo.com'),
("Jim",'Don', 32, 'jim.D@yahoo.com'),
("keith",'Lee', 30, 'lee.K@yahoo.com');

ALTER TABLE Employee DROP COLUMN Age;

ALTER TABLE Employee ADD COLUMN Age INT CHECK (Age >= 17);

UPDATE employee
SET Age = 32
WHERE EmployeeID = 5;

ALTER TABLE Employee ADD COLUMN DateOfJoining DATE DEFAULT '2025-02-26';

-- ALTER TABLE Employee ADD COLUMN DateOfJoining DATE DEFAULT 'CURRENT_DATE';

ALTER TABLE Employee ALTER COLUMN DateOfJoining DROP DEFAULT;

ALTER TABLE Employee MODIFY COLUMN DateOfJoining DATETIME;
ALTER TABLE Employee MODIFY COLUMN DateOfJoining DATETIME DEFAULT CURRENT_TIMESTAMP;

-- ALTER TABLE Employee ALTER COLUMN DateOfJoining SET DEFAULT '2025-02-26';

-- ALTER TABLE Employee ADD COLUMN DateOfJoining DATETIME DEFAULT 'CURRENTIMESTAMP';

-- ALTER TABLE Employee ADD COLUMN DateOfJoining DROP DEFAULT;

ALTER TABLE Employee ADD COLUMN Telno INT UNIQUE;

DESC employee;

CREATE TABLE Project(
    ProjectID INT PRIMARY KEY AUTO_INCREMENT,
    ProjectName VARCHAR(100) NOT NULL,
    EmployeeID INT,
    FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE CASCADE ON UPDATE CASCADE
);

SELECT CONSTRAINT_NAME, constraint_Type, TABLE_NAME
from information_schema.TABLE_CONSTRAINTS where TABLE_NAME='Employee';