import db from '../config/db.js';

const attendanceTable = `CREATE TABLE IF NOT EXISTS attendance (
  attendance_id INT AUTO_INCREMENT PRIMARY KEY,
  child_id INT NOT NULL,
  babysitter_id INT NOT NULL,
  session_date DATE NOT NULL,
  session ENUM('half-day', 'full-day') NOT NULL,
  status ENUM('present', 'absent') NOT NULL,
  FOREIGN KEY (child_id) REFERENCES children(child_id) ON DELETE CASCADE,
  FOREIGN KEY (babysitter_id) REFERENCES babysitters(babysitter_id) ON DELETE CASCADE
)`;

export const createAttendanceTable = async () => {
  try {
    await db.query(attendanceTable);
    console.log('Attendance table created');
  } catch (err) {
    console.error(`Error creating attendance table: ${err.message}`);
  }
};
