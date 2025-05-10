// models/User.js
const pool = require('../config/db');

const createTables = async () => {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      email VARCHAR(255) UNIQUE NOT NULL,
      password TEXT NOT NULL,
      role VARCHAR(50) CHECK (role IN ('manager', 'babysitter')) NOT NULL
    );
  `);

  await pool.query(`
    CREATE TABLE IF NOT EXISTS babysitters (
      id SERIAL PRIMARY KEY,
      user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
      first_name VARCHAR(100),
      last_name VARCHAR(100),
      phone_number VARCHAR(20),
      nin VARCHAR(50),
      age INTEGER,
      next_of_kin_name VARCHAR(100),
      next_of_kin_relationship VARCHAR(100),
      next_of_kin_phone VARCHAR(20)
    );
  `);

  await pool.query(`
    CREATE TABLE IF NOT EXISTS babies (
      id SERIAL PRIMARY KEY,
      name VARCHAR(100),
      age INTEGER,
      parent_name VARCHAR(100),
      parent_phone VARCHAR(20),
      special_needs TEXT,
      duration VARCHAR(50)
    );
  `);
};

module.exports = { pool, createTables };

