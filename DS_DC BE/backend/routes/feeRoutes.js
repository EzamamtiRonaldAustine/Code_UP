import express from 'express';
import { recordFee, getAllFees } from '../controllers/feeController.js';
import { protect, managerOnly } from '../middleware/authMiddleware.js';

const router = express.Router();

router.post('/record', protect, managerOnly, recordFee);
router.get('/', protect, managerOnly, getAllFees);

export default router;
