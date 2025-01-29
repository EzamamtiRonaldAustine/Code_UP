-- Active: 1738051755016@@127.0.0.1@3306@aircraftfm
-- CREATE DATABASE aircraftfm;

-- USE DATABASE aircraftfm;

CREATE TABLE Aircraft (
    AircraftID INT AUTO_INCREMENT PRIMARY KEY,
    Model VARCHAR(50) NOT NULL,
    Manufacturer VARCHAR(50),
    Capacity INT,
    Status ENUM('Active','Ground', 'In Maintenance') DEFAULT 'Active'
);

CREATE TABLE Flight (
    FlightID INT AUTO_INCREMENT PRIMARY KEY,
    AircraftID INT NOT NULL,
    Route VARCHAR(100),
    DepartureTime DATETIME,
    ArrivalTime DATETIME,
    FOREIGN KEY(AircraftID) REFERENCES Aircraft(AircraftID)
);

CREATE TABLE Crew (
    CrewID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Role ENUM('Pilot','Co-Pilot', 'Flight Attendant', 'Ground Crew') NOT NULL,
    Certification VARCHAR(100),
    Contactinfo VARCHAR(100)
);

CREATE TABLE Passenger (
    PassengerID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Contactinfo VARCHAR(100),
    BookingReference VARCHAR(50)
);

CREATE TABLE Booking (
    BookingID INT AUTO_INCREMENT PRIMARY KEY,
    PassengerID INT NOT NULL,
    FlightID INT NOT NULL,
    SeatNumber VARCHAR(10),
    BookingStatus ENUM('Confirmed','Canceled') DEFAULT 'Confirmed',
    FOREIGN KEY(PassengerID) REFERENCES Passenger(PassengerID),
    FOREIGN KEY(FlightID) REFERENCES Flight(FlightID)
);

CREATE TABLE Maintenance (
    MaintenanceID INT AUTO_INCREMENT PRIMARY KEY,
    AircraftID INT NOT NULL,
    Description TEXT,
    MaintenanceDate DATETIME,
    TechnicianName VARCHAR(100),
    Status ENUM('Scheduled', 'Completed', 'Pending') DEFAULT'Scheduled',
    FOREIGN KEY(AircraftID) REFERENCES Aircraft(AircraftID)
);

CREATE TABLE FlightCrewAssignment (
    AssignmentID INT AUTO_INCREMENT PRIMARY KEY,
    FlightID INT NOT NULL,
    CrewID INT NOT NULL,
    Role ENUM('Pilot','Co-Pilot', 'Flight Attendant') NOT NULL,
    FOREIGN KEY(FlightID) REFERENCES Flight(FlightID),
    FOREIGN KEY(CrewID) REFERENCES Crew(CrewID)
);

show tables;

CREATE TABLE GroundCrewAssignment (
    AssignmentID INT AUTO_INCREMENT PRIMARY KEY,
    AircraftID INT NOT NULL,
    CrewID INT NOT NULL,
    Task ENUM('Fueling','Loading', 'Cleaning', 'Inspection') NOT NULL,
    FOREIGN KEY(AircraftID) REFERENCES Aircraft(AircraftID),
    FOREIGN KEY(CrewID) REFERENCES Crew(CrewID)
);








