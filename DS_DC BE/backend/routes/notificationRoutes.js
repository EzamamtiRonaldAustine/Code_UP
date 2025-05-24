import express from 'express';
import { sendNotification, getAllNotifications } from '../controllers/notificationController.js';
import { protect, managerOnly } from '../middleware/authMiddleware.js';

const router = express.Router();

router.post('/send', protect, managerOnly, sendNotification);
router.get('/', protect, managerOnly, getAllNotifications);

export default router;
