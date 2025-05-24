import express from 'express';
import { registerChild, getAllChildren } from '../controllers/childController.js';
import { protect, managerOnly } from '../middleware/authMiddleware.js';

const router = express.Router();

router.post('/register', protect, managerOnly, registerChild);
router.get('/', protect, managerOnly, getAllChildren);

export default router;