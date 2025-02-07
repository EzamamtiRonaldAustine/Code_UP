-- -- Create the Database
-- CREATE DATABASE SIPMS;
-- USE SIPMS;

-- Admin Table
CREATE TABLE Admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    FName VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('Super Admin', 'Manager') NOT NULL
);

-- User Table (Updated with user_type)
CREATE TABLE User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    FName VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_type ENUM('Reserver', 'Walk-in') NOT NULL DEFAULT 'Walk-in'
);

-- ParkingSlot Table
CREATE TABLE ParkingSlot (
    slot_id INT AUTO_INCREMENT PRIMARY KEY,
    location VARCHAR(255) NOT NULL,
    admin_id INT,
    status ENUM('Available', 'Reserved', 'Occupied') DEFAULT 'Available',
    FOREIGN KEY (admin_id) REFERENCES Admin(admin_id) ON DELETE SET NULL
);

-- Reservation Table
CREATE TABLE Reservation (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    reservation_date DATE NOT NULL,
    booking_date DATE NOT NULL,
    user_id INT NOT NULL,
    slot_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (slot_id) REFERENCES ParkingSlot(slot_id) ON DELETE CASCADE
);

-- Ticket Table
CREATE TABLE Ticket (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    EntryTime DATETIME NOT NULL,
    Duration INT NOT NULL,
    BaseRate DECIMAL(10,2) NOT NULL,
    PenaltyRate DECIMAL(10,2) NOT NULL,
    Status ENUM('Active', 'Expired') DEFAULT 'Active',
    reservation_id INT,
    FOREIGN KEY (reservation_id) REFERENCES Reservation(reservation_id) ON DELETE CASCADE
);

-- Payment Table
CREATE TABLE Payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    amount_paid DECIMAL(10,2) NOT NULL,
    payment_mtd ENUM('Card', 'Mobile Money', 'Cash') NOT NULL,
    ticket_id INT NOT NULL,
    user_id INT NOT NULL,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Completed', 'Pending') DEFAULT 'Pending',
    FOREIGN KEY (ticket_id) REFERENCES Ticket(ticket_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);
