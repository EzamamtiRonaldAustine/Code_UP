import db from '../config/db.js';

// Manager assigns babysitter to a date and session duration
export const assignSchedule = async (req, res) => {
  const { babysitter_id, schedule_date, session } = req.body;

  if (!babysitter_id || !schedule_date || !session) {
    return res.status(400).json({ message: 'All fields are required' });
  }

  try {
    await db.query(
      'INSERT INTO babysitter_schedule (babysitter_id, schedule_date, session) VALUES (?, ?, ?)',
      [babysitter_id, schedule_date, session]
    );
    res.status(201).json({ message: 'Schedule assigned successfully' });
  } catch (err) {
    if (err.code === 'ER_DUP_ENTRY') {
      return res.status(400).json({ message: 'Babysitter already scheduled for this date' });
    }
    console.error(err);
    res.status(500).json({ message: 'Failed to assign schedule' });
  }
};

// Get all babysitter schedules
export const getSchedule = async (req, res) => {
  try {
    const [rows] = await db.query(
      `SELECT s.schedule_id, b.first_name, b.last_name, s.schedule_date, s.session
       FROM babysitter_schedule s
       JOIN babysitters b ON s.babysitter_id = b.babysitter_id
       ORDER BY s.schedule_date DESC`
    );
    res.status(200).json(rows);
  } catch (err) {
    console.error('Failed to fetch schedule:', err);
    res.status(500).json({ message: 'Error retrieving schedule' });
  }
};