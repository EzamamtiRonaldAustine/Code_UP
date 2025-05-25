import db from '../config/db.js';

const incidentTable = `CREATE TABLE IF NOT EXISTS incidents (
  incident_id INT AUTO_INCREMENT PRIMARY KEY,
  child_id INT NOT NULL,
  babysitter_id INT NOT NULL,
  description TEXT NOT NULL,
  severity ENUM('low', 'medium', 'high') NOT NULL,
  reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (child_id) REFERENCES children(child_id) ON DELETE CASCADE,
  FOREIGN KEY (babysitter_id) REFERENCES babysitters(babysitter_id) ON DELETE CASCADE
)`;

export const createIncidentTable = async () => {
  try {
    await db.query(incidentTable);
    console.log('Incidents table created');
  } catch (err) {
    console.error(`Error creating incidents table: ${err.message}`);
  }
};