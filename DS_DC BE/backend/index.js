import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import cookieParser from 'cookie-parser';
 
import authRoutes from './routes/authRoutes.js';
import babysitterRoutes from './routes/babysitterRoutes.js';
import childRoutes from './routes/childRoutes.js';
import financeRoutes from './routes/financeRoutes.js';
import notificationRoutes from './routes/notificationRoutes.js';
import errorHandler from './middleware/errorHandle.js';

// Load env vars
dotenv.config();

const app = express();

// Middleware
app.use(cors({
    origin: 'http://localhost:5173',
    credentials: true
  }));
app.use(cookieParser());
app.use(express.json()); // Parse JSON bodies

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/babysitters', babysitterRoutes);
app.use('/api/children', childRoutes);
app.use('/api/finance', financeRoutes);
app.use('/api/notify', notificationRoutes);

// Error Handler
app.use(errorHandler);

// Start server
const PORT =  process.env.WEB_PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
