import db from '../config/db.js';

const childTable = `CREATE TABLE IF NOT EXISTS children (
  child_id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(255) NOT NULL,
  age INT NOT NULL,
  guardian_name VARCHAR(255) NOT NULL,
  guardian_phone VARCHAR(20) NOT NULL,
  special_needs TEXT,
  session ENUM('half-day', 'full-day') NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)`;

export const createChildTable = async () => {
  try {
    await db.query(childTable);
    console.log('Children table created');
  } catch (err) {
    console.error(`Error creating children table: ${err.message}`);
  }
};