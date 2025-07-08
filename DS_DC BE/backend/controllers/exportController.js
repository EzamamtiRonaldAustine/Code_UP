import db from '../config/db.js';
import { format } from 'date-fns';
import { writeToStream } from 'fast-csv';

// Export fee records as CSV
export const exportFeesCSV = async (req, res) => {
  try {
    const [rows] = await db.query(
      `SELECT f.fee_id, c.full_name AS child_name, f.session_type, f.billed_amount, f.amount_paid, f.payment_status, f.payment_date
       FROM fees f
       JOIN children c ON f.child_id = c.child_id`
    );

    res.setHeader('Content-Disposition', `attachment; filename=fees_${format(new Date(), 'yyyyMMdd')}.csv`);
    res.setHeader('Content-Type', 'text/csv');

    writeToStream(res, rows, { headers: true });
  } catch (err) {
    console.error('Error exporting fees CSV:', err);
    res.status(500).json({ message: 'Failed to export fees CSV' });
  }
};

// Export babysitter payments as CSV
export const exportPaymentsCSV = async (req, res) => {
  try {
    const [rows] = await db.query(
      `SELECT p.payment_id, b.first_name, b.last_name, p.session_date, p.amount, p.status
       FROM payments p
       JOIN babysitters b ON p.babysitter_id = b.babysitter_id`
    );

    res.setHeader('Content-Disposition', `attachment; filename=payments_${format(new Date(), 'yyyyMMdd')}.csv`);
    res.setHeader('Content-Type', 'text/csv');

    writeToStream(res, rows, { headers: true });
  } catch (err) {
    console.error('Error exporting payments CSV:', err);
    res.status(500).json({ message: 'Failed to export payments CSV' });
  }
};