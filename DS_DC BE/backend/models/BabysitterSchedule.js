import db from '../config/db.js';

// Table to track daily shift assignments for babysitters
const babysitterScheduleTable = `CREATE TABLE IF NOT EXISTS babysitter_schedule (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    babysitter_id INT NOT NULL,
    schedule_date DATE NOT NULL,
    session ENUM('half-day', 'full-day') NOT NULL,
    UNIQUE(babysitter_id, schedule_date),
    FOREIGN KEY (babysitter_id) REFERENCES babysitters(babysitter_id) ON DELETE CASCADE
  )`;
  
  export const createBabysitterScheduleTable = async () => {
    try {
      await db.query(babysitterScheduleTable);
      console.log('Babysitter schedule table created');
    } catch (err) {
      console.error(`Error creating schedule table: ${err.message}`);
    }
  };
  
