const pool = require('../config/db');

const Incident = {
  create: async (incidentData) => {
    const {
      child_name,
      incident_type,
      date,
      time,
      description,
      severity,
      babysitter_id
    } = incidentData;

    const query = `
      INSERT INTO incident_reports
      (child_name, incident_type, date, time, description, severity, babysitter_id)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING *;
    `;
    const values = [
      child_name,
      incident_type,
      date,
      time,
      description,
      severity,
      babysitter_id
    ];

    const { rows } = await pool.query(query, values);
    return rows[0];
  },

  getAll: async () => {
    const { rows } = await pool.query(`
      SELECT ir.*, b.first_name || ' ' || b.last_name AS babysitter_name
      FROM incident_reports ir
      LEFT JOIN babysitters b ON ir.babysitter_id = b.id
      ORDER BY ir.created_at DESC
    `);
    return rows;
  }
};

module.exports = Incident;
