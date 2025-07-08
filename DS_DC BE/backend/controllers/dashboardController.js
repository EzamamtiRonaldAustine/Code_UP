import db from '../config/db.js';

// Budget threshold constant in UGX
const MIN_BALANCE_THRESHOLD = 100000;

// Get financial and operational summary for dashboard
export const getDashboardSummary = async (req, res) => {
  try {
    const [[{ total_income }]] = await db.query('SELECT SUM(amount_paid) AS total_income FROM fees');
    const [[{ total_expenses }]] = await db.query('SELECT SUM(amount) AS total_expenses FROM payments WHERE status = "confirmed"');
    const [[{ total_children }]] = await db.query('SELECT COUNT(*) AS total_children FROM children');
    const [[{ total_babysitters }]] = await db.query('SELECT COUNT(*) AS total_babysitters FROM babysitters');
    const [[{ total_attendance }]] = await db.query('SELECT COUNT(*) AS total_attendance FROM attendance');

    const income = total_income || 0;
    const expenses = total_expenses || 0;
    const net_balance = income - expenses;

    const lowBalanceAlert = net_balance < MIN_BALANCE_THRESHOLD;

    res.status(200).json({
      income,
      expenses,
      net_balance,
      lowBalanceAlert,
      total_children,
      total_babysitters,
      total_attendance
    });
  } catch (err) {
    console.error('Dashboard summary error:', err);
    res.status(500).json({ message: 'Failed to load dashboard summary' });
  }
};
