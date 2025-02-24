
CREATE Table empx (EID VARCHAR(10),
constraint empx_pk PRIMARY KEY(EID),
designation VARCHAR(20)
constraint empx_des check (designation in ('manager','clerk','teacher')),
age int constraint empx_age check (age >18),
Date_of_Join DATETIME DEFAULT CURRENT_TIMESTAMP,
gender VARCHAR(1),
email VARCHAR (20),
telno int
);

--Modifying the table structure
ALTER table empx add constraint empx_gender check (gender in ('M','F'));

ALTER table empx drop constraint empx_gender;

ALTER table empx add constraint empx_gender check (gender='M' OR gender='F');


ALTER table empx add constraint empx_email UNIQUE (email);

--modifying the empx to accept exactly 10 digits of telno
ALTER table empx add constraint empx_telno check (length(telno)=10);

desc empx;

INSERT INTO empx VALUES(
    'E001','MANAGER', 34, 'M','one@gmail.com', 0782267543);

SELECT CONSTRAINT_NAME, constraint_Type 
from information_schema.TABLE_CONSTRAINTS where TABLE_NAME='empx';



CREATE Table empy (EID VARCHAR(10) PRIMARY key,
AGE int,
GENDER VARCHAR(1),
LNAME VARCHAR(20),
DNAME VARCHAR(20),
SALARY INT,
PHONENO int,
Email VARCHAR (20),
DOJ DATE
);

--eid to accept 4 varchar
ALTER Table empy add constraint empy_eid check (length(eid)=4)


--age to be in range of 18-60
ALTER Table empy add constraint empy_age check (age>=18 and age<=60);

--lname to be uppercase
ALTER Table empy add constraint empy_lname check (lname=upper(lname));

--salary in the range 40000 t0 100000
ALTER Table empy add constraint empy_salary check (salary>=40000 and salary <=100000);

--unique phoneNo
ALTER Table empy add constraint empy_phone UNIQUE(phoneno);

--email must contain @ symbol
ALTER Table empy add constraint empy_email check (email like '%@%');

--gender not null
ALTER Table empy add constraint empy_gender check((gender)!=''); 


ALTER Table empy add constraint empy_eid_e check(EID like 'E%');

ALTER Table empy drop constraint empy_salary;


--Running TESTS
insert into empy values (
    'E001', '20', 'M', 'ODONGKARA','OSCAR', '20000','0771301999','oscar@gmail.com', '2025-02-24'
);


insert into empy values (
    'E01', '20', 'M', 'ODONGKARA','OSCAR', '20000','0771301999','oscar@gmail.com', '2025-02-24'
);

insert into empy values (
    'E002', '20', '', 'ODONGKARA','OSCAR', '20000','0771301999','oscar@gmail.com', '2025-02-24'
);

insert into empy values (
    'E005', '20', 'M', 'odongkara','OSCAR', '20000','0771301998','oscar@gmail.com', '2025-02-24'
);

insert into empy values (
    'E007', '20', 'M', 'ODONGKARA','OSCAR', '20000','0771301999','oscargmail.com', '2025-02-24'
);

ALTER Table empy drop constraint empy_phone;

insert into empy values (
    'E003', '20', 'F', 'Precious','OSCAR', '1000000','0771301999','oscar@gmail.com', '2025-02-24'
);

SELECT * FROM empy;




