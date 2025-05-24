
// routes/users.js
const express = require('express');
const router = express.Router();
const db = require('../db');

// GET all users
router.get('/', async (req, res) => {
  try {
    const [results] = await db.query('SELECT * FROM Users');
    res.json(results);
  } catch (err) {
    console.error('Error fetching users:', err);
    res.status(500).json({ error: 'Database error', details: err.message });
  }
});

// POST new user
router.post('/', async (req, res) => {
  try {
    // Changed to use password_hash instead of password to match DB schema
    const { name, email, password_hash, role, phone } = req.body;
    
    // Validate role enum values
    if (!['Manager', 'Babysitter', 'Parent'].includes(role)) {
      return res.status(400).json({ 
        error: 'Invalid role', 
        message: 'Role must be either Manager, Babysitter, or Parent' 
      });
    }

    const sql = `
      INSERT INTO Users 
        (name, email, password_hash, role, phone) 
      VALUES 
        (?, ?, ?, ?, ?)
    `;
    
    const values = [name, email, password_hash, role, phone];
    console.log('Executing SQL:', sql);
    console.log('With values:', values);

    const [result] = await db.query(sql, values);
    
    res.status(201).json({ 
      message: 'User created successfully',
      userId: result.insertId 
    });
  } catch (err) {
    console.error('Error creating user:', err);
    console.error('SQL Error:', err.message);
    res.status(500).json({ 
      error: 'Database error', 
      details: err.message,
      sql: err.sql 
    });
  }
});

module.exports = router;