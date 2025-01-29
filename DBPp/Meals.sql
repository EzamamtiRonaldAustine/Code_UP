-- Active: 1738051755016@@127.0.0.1@3306@resturant
-- Create USER table
CREATE TABLE USER (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Create STUDENT table
CREATE TABLE STUDENT (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    tokens_remaining INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES USER(user_id) ON DELETE CASCADE
);

-- Create RESTAURANT_OWNER table
CREATE TABLE RESTAURANT_OWNER (
    owner_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES USER(user_id) ON DELETE CASCADE
);

-- Create SYSTEM_MANAGER table
CREATE TABLE SYSTEM_MANAGER (
    manager_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES USER(user_id) ON DELETE CASCADE
);

-- Create SUBSCRIPTION table
CREATE TABLE SUBSCRIPTION (
    subscription_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    tokens_allocated INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES STUDENT(student_id) ON DELETE CASCADE
);

-- Create MEAL table
CREATE TABLE MEAL (
    meal_id INT PRIMARY KEY AUTO_INCREMENT,
    meal_name VARCHAR(255) NOT NULL,
    meal_price FLOAT NOT NULL
);

-- Create PURCHASE table
CREATE TABLE PURCHASE (
    purchase_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    meal_id INT NOT NULL,
    purchase_date DATE NOT NULL,
    tokens_deducted INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES STUDENT(student_id) ON DELETE CASCADE,
    FOREIGN KEY (meal_id) REFERENCES MEAL(meal_id) ON DELETE CASCADE
);

-- Create NOTIFICATION table
CREATE TABLE NOTIFICATION (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES STUDENT(student_id) ON DELETE CASCADE
);
