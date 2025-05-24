// === routes/financeRoutes.js ===
import express from 'express';
import { recordPayment, getPayments, generatePayments, confirmPayment } from '../controllers/financeController.js';
import { protect, managerOnly } from '../middleware/authMiddleware.js';

const router = express.Router();

router.post('/record', protect, managerOnly, recordPayment); // manual (if needed)
router.post('/generate', protect, managerOnly, generatePayments); // automated generation
router.patch('/confirm/:id', protect, managerOnly, confirmPayment); // manager confirms
router.get('/', protect, managerOnly, getPayments);

export default router;