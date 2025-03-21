import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ResultsComponent from './app/resultscomponent.js';
import ProfilePic from './app/Profile_pic.js';
import CareerGoals from './app/Careergoals.js';
import MyHobbies from './app/MyHobbies.js';
import Introduction from './app/Introduction.js';
import Login from './app/Login.js';
import PersonalDetails from './app/PersonalDetails.js'; // Separate file
// import ContactInfo from './app/ContactInfo.js'; // Separate file
// import Links from './app/Links.js'; // Separate file
import './App.css';
import './login.css';

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    return (
        <Router>
            <Routes>
                <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
                <Route 
                    path="/profile" 
                    element={isAuthenticated ? <ProfilePage setIsAuthenticated={setIsAuthenticated} /> : <Navigate to="/login" />} 
                />
                <Route path="/" element={<Navigate to="/login" />} />
            </Routes>
        </Router>
    );
}

function ProfilePage() {
    return (
        <div>
            <Introduction />
            <hr />
            <PersonalDetails />
            <hr />
            <ProfilePic />
            <hr />
            <MyHobbies />
            <hr />
            <ResultsComponent />
            <hr />
            <Links />
            <hr />
            <ContactInfo />
            <hr />
            <CareerGoals />
            <hr />
        </div>
    );
}

function ContactInfo() {
    return (
        <div>
            <h2>Contact Information</h2>
            <p>
                Email: <a href="mailto:austineblackezamati@gmail.com">austineblackezamati@gmail.com</a>
            </p>
            <p>
                Social Media:{" "}
                <a href="https://x.com/Ezamighty47?t=zdjYyDzl0QZgtV8ZeR_aRg&s=08" target="_blank" rel="noopener noreferrer">
                    Twitter
                </a>{" "}
                |{" "}
                <a href="https://github.com/EzamamtiRonaldAustine/Code_UP" target="_blank" rel="noopener noreferrer">
                    GitHub
                </a>
            </p>
        </div>
    );
}

function Links() {
    return (
        <div>
            <h2>Links</h2>
            <ul>
                <li>
                    <a href="https://www.youtube.com/results?search_query=bro+code" target="_blank" rel="noopener noreferrer">
                        My Favorite Website
                    </a>
                </li>
                <li>
                    <a href="https://cse-ucu.com" target="_blank" rel="noopener noreferrer">
                        UCU Computing Department Page
                    </a>
                </li>
            </ul>
        </div>
    );
}

export default App;
