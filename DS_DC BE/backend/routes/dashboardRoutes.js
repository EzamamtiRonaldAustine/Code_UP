import express from 'express';
import { getDashboardSummary } from '../controllers/dashboardController.js';
import { protect, managerOnly } from '../middleware/authMiddleware.js';

const router = express.Router();

router.get('/', protect, managerOnly, getDashboardSummary);

export default router;
