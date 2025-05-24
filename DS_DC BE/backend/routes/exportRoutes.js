import express from 'express';
import { exportFeesCSV, exportPaymentsCSV } from '../controllers/exportController.js';
import { protect, managerOnly } from '../middleware/authMiddleware.js';

const router = express.Router();

router.get('/fees', protect, managerOnly, exportFeesCSV);
router.get('/payments', protect, managerOnly, exportPaymentsCSV);

export default router;
