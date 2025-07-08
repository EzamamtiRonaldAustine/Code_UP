import db from '../config/db.js';

// Babysitter reports an incident
export const reportIncident = async (req, res) => {
  const { child_id, description, severity } = req.body;
  const babysitter_id = req.user.userId;

  if (!child_id || !description || !severity) {
    return res.status(400).json({ message: 'All fields are required' });
  }

  try {
    await db.query(
      'INSERT INTO incidents (child_id, babysitter_id, description, severity) VALUES (?, ?, ?, ?)',
      [child_id, babysitter_id, description, severity]
    );
    res.status(201).json({ message: 'Incident reported successfully' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Error reporting incident' });
  }
};

// Manager retrieves all incidents
export const getIncidents = async (req, res) => {
  try {
    const [incidents] = await db.query('SELECT * FROM incidents');
    res.status(200).json(incidents);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Error fetching incidents' });
  }
};
