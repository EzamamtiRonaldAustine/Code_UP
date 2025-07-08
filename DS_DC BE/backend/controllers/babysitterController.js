import db from '../config/db.js';

// Register a babysitter (Only manager can do this)
export const registerBabysitter = async (req, res) => {
  const {
    first_name,
    last_name,
    email,
    phone_number,
    nin,
    age,
    next_of_kin_name,
    next_of_kin_phone
  } = req.body;

  if (!first_name || !last_name || !phone_number || !nin || !age || !next_of_kin_name || !next_of_kin_phone) {
    return res.status(400).json({ message: 'Please fill in all required fields' });
  }

  if (age < 21 || age > 35) {
    return res.status(400).json({ message: 'Babysitter age must be between 21 and 35 years' });
  }

  try {
    await db.query(
      'INSERT INTO babysitters (first_name, last_name, email, phone_number, nin, age, next_of_kin_name, next_of_kin_phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
      [first_name, last_name, email, phone_number, nin, age, next_of_kin_name, next_of_kin_phone]
    );
    res.status(201).json({ message: 'Babysitter registered successfully' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Error registering babysitter' });
  }
};

// Get all babysitters (Only manager)
export const getAllBabysitters = async (req, res) => {
  try {
    const [babysitters] = await db.query('SELECT * FROM babysitters');
    res.status(200).json(babysitters);
  } catch (err) {
    res.status(500).json({ message: 'Error retrieving babysitters' });
  }
};