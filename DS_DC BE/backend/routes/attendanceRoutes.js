// Description: Routes for attendance management in the babysitting application
import express from 'express';
import { markAttendance, getAttendance } from '../controllers/attendanceController.js';
import { protect, managerOnly, babysitterOnly } from '../middleware/authMiddleware.js';

const router = express.Router();

// Babysitters mark attendance
router.post('/mark', protect, babysitterOnly, markAttendance);

// Managers view all attendance
router.get('/', protect, managerOnly, getAttendance);

export default router;
