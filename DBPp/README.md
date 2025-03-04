# Group1CPMS
CREATE DATABASE ParkingSystem;
USE ParkingSystem;

-- Admin Table
CREATE TABLE Admin (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    FName VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    Role ENUM('Manager', 'Staff') NOT NULL
);

-- User Table
CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    FName VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Phone VARCHAR(20) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    UserType ENUM('Regular', 'VIP') NOT NULL
);

-- Parking Slot Table
CREATE TABLE ParkingSlot (
    slot_id INT PRIMARY KEY AUTO_INCREMENT,
    location VARCHAR(255) NOT NULL,
    admin_id INT,
    status ENUM('Available', 'Occupied', 'Reserved') NOT NULL,
    FOREIGN KEY (admin_id) REFERENCES Admin(admin_id) ON DELETE SET NULL
);

-- Reservation Table
CREATE TABLE Reservation (
    reservation_id INT PRIMARY KEY AUTO_INCREMENT,
    reservationDate DATETIME NOT NULL,
    booking_date DATETIME NOT NULL,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

-- Ticket Table
CREATE TABLE Ticket (
    ticket_id INT PRIMARY KEY AUTO_INCREMENT,
    entryTime DATETIME NOT NULL,
    duration INT NOT NULL,
    baseRate DECIMAL(10,2) NOT NULL,
    penaltyRate DECIMAL(10,2) NOT NULL,
    status ENUM('Active', 'Expired', 'Paid') NOT NULL,
    reservation_id INT,
    slot_id INT,
    FOREIGN KEY (reservation_id) REFERENCES Reservation(reservation_id) ON DELETE SET NULL,
    FOREIGN KEY (slot_id) REFERENCES ParkingSlot(slot_id) ON DELETE CASCADE
);

-- Payment Table
CREATE TABLE Payment (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    amount_paid DECIMAL(10,2) NOT NULL,
    ticket_id INT,
    user_id INT,
    paymentMethod ENUM('Cash', 'Card', 'Online') NOT NULL,
    paymentDate DATETIME NOT NULL,
    status ENUM('Pending', 'Completed', 'Failed') NOT NULL,
    FOREIGN KEY (ticket_id) REFERENCES Ticket(ticket_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

-- Admin Data
INSERT INTO Admin (FName, email, phone, password, Role) VALUES
('Alice', 'alice@admin.com', '1234567890', 'pass123', 'Manager'),
('Bob', 'bob@admin.com', '0987654321', 'pass456', 'Staff'),
('Charlie', 'charlie@admin.com', '1112223333', 'pass789', 'Manager');

-- User Data
INSERT INTO User (FName, Email, Phone, Password, UserType) VALUES
('John Doe', 'john@example.com', '5551112222', 'johnpass', 'Regular'),
('Jane Smith', 'jane@example.com', '5553334444', 'janepass', 'VIP'),
('Mike Brown', 'mike@example.com', '5556667777', 'mikepass', 'Regular'),
('Anna Lee', 'anna@example.com', '5558889999', 'annapass', 'VIP'),
('Chris Green', 'chris@example.com', '5550001111', 'chrispass', 'Regular');

-- Parking Slot Data
INSERT INTO ParkingSlot (location, admin_id, status) VALUES
('A1', 1, 'Available'),
('A2', 2, 'Occupied'),
('B1', 1, 'Reserved'),
('B2', 2, 'Available'),
('C1', 3, 'Occupied');

-- Reservation Data
INSERT INTO Reservation (reservationDate, booking_date, user_id) VALUES
(NOW(), NOW() + INTERVAL 1 DAY, 1),
(NOW(), NOW() + INTERVAL 2 DAY, 2),
(NOW(), NOW() + INTERVAL 3 DAY, 3),
(NOW(), NOW() + INTERVAL 4 DAY, 4),
(NOW(), NOW() + INTERVAL 5 DAY, 5);

-- Ticket Data
INSERT INTO Ticket (entryTime, duration, baseRate, penaltyRate, status, reservation_id, slot_id) VALUES
(NOW(), 60, 5.00, 2.00, 'Active', 1, 1),
(NOW(), 120, 10.00, 3.00, 'Paid', 2, 2),
(NOW(), 90, 7.50, 2.50, 'Expired', 3, 3),
(NOW(), 30, 2.50, 1.00, 'Active', 4, 4),
(NOW(), 45, 3.75, 1.50, 'Paid', 5, 5);

-- Payment Data
INSERT INTO Payment (amount_paid, ticket_id, user_id, paymentMethod, paymentDate, status) VALUES
(10.00, 2, 2, 'Card', NOW(), 'Completed'),
(7.50, 3, 3, 'Cash', NOW(), 'Completed'),
(2.50, 4, 4, 'Online', NOW(), 'Pending'),
(3.75, 5, 5, 'Card', NOW(), 'Completed'),
(5.00, 1, 1, 'Cash', NOW(), 'Failed');

REPORTS THAT CAN BE STORED AS VIEWS

-- View to get all users with reservations
CREATE VIEW UserReservations AS
SELECT u.FName, u.Email, r.reservationDate, r.booking_date
FROM User u
JOIN Reservation r ON u.user_id = r.user_id;

-- View to get active tickets with user details
CREATE VIEW ActiveTickets AS
SELECT t.ticket_id, u.FName, u.Email, t.entryTime, t.duration, t.status
FROM Ticket t
JOIN Reservation r ON t.reservation_id = r.reservation_id
JOIN User u ON r.user_id = u.user_id
WHERE t.status = 'Active';

-- View to get pending payments
CREATE VIEW PendingPayments AS
SELECT p.payment_id, u.FName, t.ticket_id, p.amount_paid, p.status
FROM Payment p
JOIN User u ON p.user_id = u.user_id
JOIN Ticket t ON p.ticket_id = t.ticket_id
WHERE p.status = 'Pending';



JOINS
-- Natural Join: Users with their reservations
SELECT * 
FROM User 
NATURAL JOIN Reservation;

-- Left Outer Join: All users and their reservations (including those without)
SELECT u.FName, u.Email, r.reservationDate
FROM User u
LEFT JOIN Reservation r ON u.user_id = r.user_id;

-- Right Outer Join: All reservations and their users (including orphaned reservations)
SELECT u.FName, u.Email, r.reservationDate
FROM User u
RIGHT JOIN Reservation r ON u.user_id = r.user_id;

-- Full Outer Join: Combine left and right joins (since MySQL doesn't support FULL JOIN)
SELECT u.FName, u.Email, r.reservationDate
FROM User u
LEFT JOIN Reservation r ON u.user_id = r.user_id
UNION
SELECT u.FName, u.Email, r.reservationDate
FROM User u
RIGHT JOIN Reservation r ON u.user_id = r.user_id;


CASE CONDITIONAL STATEMENTS
SELECT ticket_id, entryTime, duration, 
    CASE 
        WHEN duration <= 30 THEN 'Short Stay'
        WHEN duration BETWEEN 31 AND 90 THEN 'Medium Stay'
        ELSE 'Long Stay'
    END AS StayDurationCategory
FROM Ticket;

CONSTRAINTS

CREATE DATABASE ParkingSystem;
USE ParkingSystem;

-- Admin Table
CREATE TABLE Admin (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    FName VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    password VARCHAR(255) NOT NULL,
    Role ENUM('Manager', 'Staff') NOT NULL
);

-- User Table
CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    FName VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    Phone VARCHAR(20) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    UserType ENUM('Regular', 'VIP') NOT NULL
);

-- Parking Slot Table
CREATE TABLE ParkingSlot (
    slot_id INT PRIMARY KEY AUTO_INCREMENT,
    location VARCHAR(255) NOT NULL,
    admin_id INT,
    status ENUM('Available', 'Occupied', 'Reserved') NOT NULL DEFAULT 'Available'
);

-- Reservation Table
CREATE TABLE Reservation (
    reservation_id INT PRIMARY KEY AUTO_INCREMENT,
    reservationDate DATETIME NOT NULL DEFAULT NOW(),
    booking_date DATETIME NOT NULL,
    user_id INT NOT NULL
);

-- Ticket Table
CREATE TABLE Ticket (
    ticket_id INT PRIMARY KEY AUTO_INCREMENT,
    entryTime DATETIME NOT NULL DEFAULT NOW(),
    duration INT NOT NULL,
    baseRate DECIMAL(10,2) NOT NULL,
    penaltyRate DECIMAL(10,2) NOT NULL,
    status ENUM('Active', 'Expired', 'Paid') NOT NULL DEFAULT 'Active',
    reservation_id INT,
    slot_id INT NOT NULL
);

-- Payment Table
CREATE TABLE Payment (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    amount_paid DECIMAL(10,2) NOT NULL,
    ticket_id INT NOT NULL,
    user_id INT NOT NULL,
    paymentMethod ENUM('Cash', 'Card', 'Online') NOT NULL,
    paymentDate DATETIME NOT NULL DEFAULT NOW(),
    status ENUM('Pending', 'Completed', 'Failed') NOT NULL DEFAULT 'Pending'
);


DDL &B DML
UPDATE Ticket 
SET status = 'Paid' 
WHERE ticket_id = 1;

DELETE FROM Payment 
WHERE status = 'Failed';
