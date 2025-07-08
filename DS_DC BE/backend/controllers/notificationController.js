import db from '../config/db.js';
import { ResetEmail } from '../utils/mailer.js';

export const sendNotification = async (req, res) => {
  const { recipient_email, subject, message } = req.body;

  if (!recipient_email || !subject || !message) {
    return res.status(400).json({ message: 'All fields are required' });
  }

  try {
    await ResetEmail(recipient_email, message, subject);
    await db.query(
      'INSERT INTO notifications (recipient_email, subject, message) VALUES (?, ?, ?)',
      [recipient_email, subject, message]
    );
    res.status(200).json({ message: 'Notification sent and logged successfully' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Failed to send notification' });
  }
};

export const getAllNotifications = async (req, res) => {
  try {
    const [rows] = await db.query('SELECT * FROM notifications ORDER BY sent_at DESC');
    res.status(200).json(rows);
  } catch (err) {
    res.status(500).json({ message: 'Error retrieving notifications' });
  }
};