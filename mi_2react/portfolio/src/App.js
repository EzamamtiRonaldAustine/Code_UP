import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ResultsComponent from './app/resultscomponent.js';
import ProfilePic from './app/Profile_pic.js';
import CareerGoals from './app/Careergoals.js';
import MyHobbies from './app/MyHobbies.js';
import Introduction from './app/Introduction.js';
import Login from './app/Login.js';
import PersonalDetails from './app/PersonalDetails.js';
import ContactInfo from './app/ContactInfo.js';
import Links from './app/Links.js';
import './App.css';

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    return (
        <div className="paper-container">
            <Router>
                <Routes>
                    <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
                    <Route 
                        path="/profile" 
                        element={isAuthenticated ? <ProfilePage /> : <Navigate to="/login" />} 
                    />
                    <Route path="/" element={<Navigate to="/login" />} />
                </Routes>
            </Router>
        </div>
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

export default App;
