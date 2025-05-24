import express from 'express';
import { reportIncident, getIncidents } from '../controllers/incidentController.js';
import { protect, babysitterOnly, managerOnly } from '../middleware/authMiddleware.js';

const router = express.Router();

// Babysitter reports an incident
router.post('/report', protect, babysitterOnly, reportIncident);

// Manager views all incidents
router.get('/', protect, managerOnly, getIncidents);

export default router;
