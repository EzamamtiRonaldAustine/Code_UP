import db from '../config/db.js';

// Billing rates per session
const SESSION_RATES = {
  'half-day': 2000,
  'full-day': 5000
};

export const recordFee = async (req, res) => {
  const { child_id, session_type, amount_paid, payment_date } = req.body;

  if (!child_id || !session_type || !amount_paid || !payment_date) {
    return res.status(400).json({ message: 'All fields are required' });
  }

  const billed_amount = SESSION_RATES[session_type];

  const payment_status =
    Number(amount_paid) < billed_amount ? 'pending' : 'paid';

  try {
    await db.query(
      'INSERT INTO fees (child_id, session_type, billed_amount, amount_paid, payment_status, payment_date) VALUES (?, ?, ?, ?, ?, ?)',
      [child_id, session_type, billed_amount, amount_paid, payment_status, payment_date]
    );
    res.status(201).json({ message: 'Fee recorded successfully' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Error recording fee' });
  }
};

export const getAllFees = async (req, res) => {
  try {
    const [fees] = await db.query(
      `SELECT f.*, c.full_name FROM fees f 
       JOIN children c ON f.child_id = c.child_id`
    );
    res.status(200).json(fees);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Error retrieving fee records' });
  }
};