import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ResultsComponent from './resultscomponent.js';
import ProfilePic from './Profile_pic.js';
import CareerGoals from './Careergoals.js';
import MyHobbies from './MyHobbies.js';
import Introduction from './Introduction.js';
import Login from './Login.js';
import PersonalDetails from './PersonalDetails.js';
import ContactInfo from './ContactInfo.js';
import Links from './Links.js';
import '../App.css';

function Home() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    return (
        <div className="paper-container">
            <BrowserRouter>
                <Routes>
                    <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
                    <Route 
                        path="/profile" 
                        element={isAuthenticated ? <ProfilePage /> : <Navigate to="/login" />} 
                    />
                    <Route path="/" element={<Navigate to="/login" />} />
                </Routes>
            </BrowserRouter>
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

export default Home;
