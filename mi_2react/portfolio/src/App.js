import React, { useState } from 'react';
import {BrowserRouter, Routes, Route, Navigate} from 'react-router-dom';
import Login from './app/Login.js';
import Home from './app/Home.js';
import ResultsComponent from './app/resultscomponent.js';
// import ProfilePic from './app/Profile_pic.js';
// import CareerGoals from './app/Careergoals.js';
// import MyHobbies from './app/MyHobbies.js';
// import Introduction from './app/Introduction.js';
// import PersonalDetails from './app/PersonalDetails.js';
// import ContactInfo from './app/ContactInfo.js';
// import Links from './app/Links.js';
import './App.css';

function App() {
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
        <BrowserRouter>
            <Routes>
                <Route path='/home' element={<Home/>}></Route>
                <Route path='/results' element={<ResultsComponent/>}></Route>
            </Routes>
        </BrowserRouter>
    );
}

export default App;
