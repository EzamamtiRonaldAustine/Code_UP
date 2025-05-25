import db from '../config/db.js';

// Extended table to include 'status' for confirmation by manager
const paymentTable = `CREATE TABLE IF NOT EXISTS payments (
  payment_id INT AUTO_INCREMENT PRIMARY KEY,
  babysitter_id INT,
  session_date DATE,
  amount DECIMAL(10,2),
  managed_by INT,
  status ENUM('pending', 'confirmed') DEFAULT 'pending',
  FOREIGN KEY (babysitter_id) REFERENCES babysitters(babysitter_id) ON DELETE CASCADE,
  FOREIGN KEY (managed_by) REFERENCES users(user_id) ON DELETE CASCADE
)`;

export const createPaymentTable = async () => {
  try {
    await db.query(paymentTable);
    console.log('Payments table created');
  } catch (err) {
    console.error(`Error creating payments table: ${err.message}`);
  }
};