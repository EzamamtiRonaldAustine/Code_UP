import db from '../config/db.js';

// Register a new child
export const registerChild = async (req, res) => {
  const {
    full_name,
    age,
    guardian_name,
    guardian_phone,
    special_needs,
    session
  } = req.body;

  if (!full_name || !age || !guardian_name || !guardian_phone || !session) {
    return res.status(400).json({ message: 'All required fields must be filled' });
  }

  try {
    await db.query(
      'INSERT INTO children (full_name, age, guardian_name, guardian_phone, special_needs, session) VALUES (?, ?, ?, ?, ?, ?)',
      [full_name, age, guardian_name, guardian_phone, special_needs, session]
    );
    res.status(201).json({ message: 'Child registered successfully' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Error registering child' });
  }
};

// Get all registered children
export const getAllChildren = async (req, res) => {
  try {
    const [children] = await db.query('SELECT * FROM children');
    res.status(200).json(children);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Error retrieving children' });
  }
};
