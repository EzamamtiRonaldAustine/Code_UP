👥 Group 3 Team Members 
Ezamamti Austine Ronald (Project Manager, Backend & API Lead)
Namaganda Wakabi Precious (Database Head)
Mucunguzi Godfrey (Documentation Head)
Agaba Itungo (Presentation Lead)
Kisa Emmanuel (UI Lead)
Lakica Leticia (Business Analyst)

📘 Daystar Daycare Management System – Backend by Group 3

This is the backend API for the Daystar Daycare Management System, built with Node.js, 
Express.js, and PostgreSQL (Neon). It powers the server-side operations such as user authentication, 
child and babysitter management, attendance tracking, incidents, and payments.

📂 Project Structurebackend/
├── app.js                  Entry point of the application
├── config/
│   └── db.js               Database connection config (PostgreSQL + Neon)
├── controllers/            Logic for each API route
├── middlewares/            JWT token validation and auth middleware
├── models/                 Database models 
├── routes/                 Route definitions (e.g /child, /babysitter)
├── utils/                  Utility functions (e.g mail)
├── .env                    Environment variables 
└──package.json             Project metadata and dependencies

Functionalities
Babysitter(not well implemented) and child registration
Attendance and incident tracking
Email notifications (via Nodemailer)
PostgreSQL database with connection pooling
Secure routing and middleware logic

RESTful API structure
⚙️ Setup Instructions1. 
Clone the Repositorygit clonehttps://github.com/EzamamtiRonaldAustine/DayStar-DayCare-Backend
cd DayStar-Daycare-Backend. 
Install Dependencies npm install. 
Create a .env File
Create a .env file in the root directory:
DATABASE_URL=postgresql://neondb_owner:npg_C7sqwhzadDM8@ep-late-king-a4mcma48-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
PORT=8000
JWT_SECRET='daystar'
EMAIL_USER=your_email@example.com
EMAIL_PASS=your_email_password 

Running the Backend
npm start
The server will be available at: http://localhost:8000

📌 Core Routes 
MethodRouteDescription:
POST/loginUser login (returns JWT token)
POST/add-babysitterAdd a new babysitterPOST/add-childRegister a new child
GET/babysittersFetch all babysitters
GET/childrenList all children
POST/attendanceSubmit attendance records
GET/incident/:idGet specific incident
PUT/babysitter/:id/statusUpdate babysitter availability
DELETE/baby/:idDelete a child recordSome routes are protected and require a valid JWT in the Authorization header.

🔐 AuthenticationOn login, users receive a JWT token.
Protected routes use middleware to verify and decode the token.
Different roles (e.g., manager, babysitter) control access to certain endpoints.

📂 PostgreSQL (Neon)
The system uses a Neon-hosted PostgreSQL database.
Connection pooling is handled using the pg library. 
Connection info is stored in the .env variable DATABASE_URL.
SSL is enabled with:
ssl: { rejectUnauthorized: false }

📧 Email IntegrationUses Nodemailer to send notification emails. 
Configured SMTP settings in the .env file:
EMAIL_USER=your_email@example.com
EMAIL_PASS=your_email_password

🔧 Tips 
Used Thunder Client to test your APIs.
Restart the server with nodemon during development.
Check .env values carefully if connection errors occur.

📈 Deployment NotesBackend can be deployed to Render, Railway, or Heroku.
Use CI/CD pipelines for seamless updates.
Make sure to enable SSL for production database connections.

This project is open-source and free to use for academic and research purposes.
📌 Related Links
🔗 Frontend Repo: https://github.com/Kisaemmanuel/front-end-UI-
🔗 Backend Repo: https://github.com/EzamamtiRonaldAustine/DayStar-DayCare-Backend
🔗 Deployed app: https://daystarfrontend.vercel.app/
 
