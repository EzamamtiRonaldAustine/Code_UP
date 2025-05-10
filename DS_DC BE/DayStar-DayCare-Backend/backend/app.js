require('dotenv').config();

const express = require('express');
const cors = require('cors');  
const app = express();
const userRoutes = require('./routes/userRoutes');
const babysitterRoutes = require('./routes/babysitterRoutes');
const babyRoutes = require('./routes/babyRoutes');
const auth = require('./middleware/auth');
const incidentRoutes = require('./routes/incidentRoutes');
const scheduleRoutes = require('./routes/scheduleRoutes');
const paymentRoutes = require('./routes/paymentRoutes');

// Middleware for parsing incoming requests
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Enable CORS for all origins (or specify your allowed origins)
app.use(cors(
    ["http://localhost:3000", "https://daystarfrontend.vercel.app", "http://localhost:3001"]
));

// Middleware for authentication (if needed for all routes)
// app.use(auth.verifyManager); // Uncomment if you want to apply auth globally
// Routes for user management
app.use('/api/users', userRoutes);
// Routes for babysitter management
app.use('/api/babysitters', babysitterRoutes);


// Routes for baby management
app.use('/api/babies', babyRoutes);
// Routes for incident management
app.use('/api/incidents', incidentRoutes);

// Routes for schedule management
app.use('/api/schedules', scheduleRoutes);
// Routes for payment management
app.use('/api/payments', paymentRoutes);



// Use the port from the environment variable or default to 8000
const port = process.env.PORT || 8000;

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
