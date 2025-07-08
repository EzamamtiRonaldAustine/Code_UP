import db from '../config/db.js';

// Mark child attendance for a session (performed by babysitter)
export const markAttendance = async (req, res) => {
  const { child_id, session_date, session, status } = req.body;
  const babysitter_id = req.user.userId;

  if (!child_id || !session_date || !session || !status) {
    return res.status(400).json({ message: 'All fields are required' });
  }

  try {
    await db.query(
      'INSERT INTO attendance (child_id, babysitter_id, session_date, session, status) VALUES (?, ?, ?, ?, ?)',
      [child_id, babysitter_id, session_date, session, status]
    );
    res.status(201).json({ message: 'Attendance recorded successfully' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Error recording attendance' });
  }
};

// Get all attendance records (manager only)
export const getAttendance = async (req, res) => {
  try {
    const [records] = await db.query('SELECT * FROM attendance');
    res.status(200).json(records);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Error fetching attendance records' });
  }
};
