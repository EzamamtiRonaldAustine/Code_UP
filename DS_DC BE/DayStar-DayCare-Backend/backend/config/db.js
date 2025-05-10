// config/db.js
const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false, // Needed for Neon
  },
  max: 20,             // max number of clients in the pool
  idleTimeoutMillis: 30000, // how long a client is allowed to remain idle before being closed
  connectionTimeoutMillis: 5000 // time to wait before timing out a new connection
});

// Optional: basic test on first load
(async () => {
  try {
    const client = await pool.connect();
    console.log('Connected to Neon PostgreSQL!');
    client.release();
  } catch (err) {
    console.error('Initial DB connection failed. Retrying...', err);
  }
})();

// Handle global errors
pool.on('error', (err, client) => {
  console.error('Unexpected error on idle client', err);
  // App should ideally notify or restart based on the severity
});

module.exports = pool;
