import express from 'express';
import { assignSchedule, getSchedule } from '../controllers/scheduleController.js';
import { protect, managerOnly } from '../middleware/authMiddleware.js';

const router = express.Router();

router.post('/assign', protect, managerOnly, assignSchedule);
router.get('/', protect, managerOnly, getSchedule);

export default router;