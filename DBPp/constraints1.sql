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

