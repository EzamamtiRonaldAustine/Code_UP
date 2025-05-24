// Description: Routes for babysitter management, including registration and retrieval of all babysitters.
import express from 'express';
import { registerBabysitter, getAllBabysitters } from '../controllers/babysitterController.js';
import { protect, managerOnly } from '../middleware/authMiddleware.js';

const router = express.Router();

// Routes restricted to manager only
router.post('/register', protect, managerOnly, registerBabysitter);
router.get('/', protect, managerOnly, getAllBabysitters);

export default router;
