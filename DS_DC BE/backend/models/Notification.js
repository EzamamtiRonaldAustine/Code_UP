import db from '../config/db.js';

const notificationTable = `CREATE TABLE IF NOT EXISTS notifications (
  notification_id INT AUTO_INCREMENT PRIMARY KEY,
  recipient_email VARCHAR(255) NOT NULL,
  subject VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)`;

export const createNotificationTable = async () => {
  try {
    await db.query(notificationTable);
    console.log('Notifications table created');
  } catch (err) {
    console.error(`Error creating notifications table: ${err.message}`);
  }
};