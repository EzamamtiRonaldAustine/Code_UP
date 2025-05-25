import db from '../config/db.js';

const babysitterTable = `CREATE TABLE IF NOT EXISTS babysitters (
  babysitter_id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email VARCHAR(255),
  phone_number VARCHAR(15) NOT NULL,
  nin VARCHAR(20) NOT NULL UNIQUE,
  age INT NOT NULL CHECK (age BETWEEN 21 AND 35),
  next_of_kin_name VARCHAR(255) NOT NULL,
  next_of_kin_phone VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)`;

export const createBabysitterTable = async () => {
  try {
    await db.query(babysitterTable);
    console.log('Babysitters table created');
  } catch (err) {
    console.error(`Error creating babysitters table: ${err.message}`);
  }
};