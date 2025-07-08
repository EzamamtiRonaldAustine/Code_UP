// Description: This file contains the controller functions for managing babysitter payments.
import db from '../config/db.js';

// Session rates per child per session type
const SESSION_RATES = {
  'half-day': 2000,
  'full-day': 5000
};

// Automatically calculate payments for each babysitter based on attendance
export const generatePayments = async (req, res) => {
  const session_date = req.body.session_date || new Date().toISOString().split('T')[0];

  try {
    // Fetch all attendance entries grouped by babysitter and session type
    const [rows] = await db.query(
      `SELECT babysitter_id, session, COUNT(*) as count
       FROM attendance
       WHERE session_date = ?
       GROUP BY babysitter_id, session`,
      [session_date]
    );

    const managerId = req.user.userId;
    const payments = [];

    for (const row of rows) {
      const amount = row.count * SESSION_RATES[row.session];
      await db.query(
        'INSERT INTO payments (babysitter_id, session_date, amount, managed_by, status) VALUES (?, ?, ?, ?, ?)',
        [row.babysitter_id, session_date, amount, managerId, 'pending']
      );
      payments.push({ babysitter_id: row.babysitter_id, session: row.session, count: row.count, amount });
    }

    res.status(201).json({ message: 'Payments generated', payments });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Error generating payments' });
  }
};

// Confirm a pending payment by ID
export const confirmPayment = async (req, res) => {
  const { id } = req.params;
  try {
    await db.query('UPDATE payments SET status = ? WHERE payment_id = ?', ['confirmed', id]);
    res.status(200).json({ message: 'Payment confirmed' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Failed to confirm payment' });
  }
};

// Get all payments including status
export const getPayments = async (req, res) => {
  try {
    const [payments] = await db.query(
      `SELECT p.*, b.first_name, b.last_name, u.username AS manager_name 
       FROM payments p 
       JOIN babysitters b ON p.babysitter_id = b.babysitter_id 
       JOIN users u ON p.managed_by = u.user_id`
    );
    res.status(200).json(payments);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Error fetching payments' });
  }
};

// Get payments for a specific babysitter
export const recordPayment = async (req, res) => {
  const { babysitter_id, session_date, amount } = req.body;
  const managerId = req.user.userId;

  try {
    await db.query(
      'INSERT INTO payments (babysitter_id, session_date, amount, managed_by, status) VALUES (?, ?, ?, ?, ?)',
      [babysitter_id, session_date, amount, managerId, 'pending']
    );
    res.status(201).json({ message: 'Payment recorded manually' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Failed to record payment' });
  }
};
