import db from '../config/db.js';

const feeTable = `CREATE TABLE IF NOT EXISTS fees (
  fee_id INT AUTO_INCREMENT PRIMARY KEY,
  child_id INT NOT NULL,
  session_type ENUM('half-day', 'full-day') NOT NULL,
  billed_amount DECIMAL(10,2) NOT NULL,
  amount_paid DECIMAL(10,2) NOT NULL,
  payment_status ENUM('paid', 'pending', 'overdue') DEFAULT 'paid',
  payment_date DATE NOT NULL,
  FOREIGN KEY (child_id) REFERENCES children(child_id) ON DELETE CASCADE
)`;

export const createFeeTable = async () => {
  try {
    await db.query(feeTable);
    console.log('Fees table created');
  } catch (err) {
    console.error(`Error creating fees table: ${err.message}`);
  }
};