import React from 'react';
import ResultsComponent from './resultscomponent';
import ProfilePic from './Profile_pic';
import CareerGoals from './Careergoals';
import MyHobbies from './MyHobbies';
import Introduction from './Introduction';
import PersonalDetails from './PersonalDetails';
import ContactInfo from './ContactInfo';
import Links from './Links';
import '../App.css';

function Home() {
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
