// import { useState } from "react";
import ResultsComponent from "./app/resultscomponent.js";
import Profile_pic from "./app/Profile_pic.js";
import CareerGoals from "./app/Careergoals.js";
import MyHobbies from "./app/MyHobbies.js";
import "./App.css"; // Import your CSS file
// import "./style1.js"; // Import your JavaScript file if needed

function App() {
  return (
    <div>

      {/* Introduction */}
      <Introduction />
      <hr />

      {/* Personal Details */}
      <Personal_details />
      <hr />

      {/* Profile Picture */}
      <Profile_pic />
      <hr />

      {/* Hobbies */}
      <MyHobbies/>


      {/* Results */}
      <ResultsComponent />

      <hr />

      {/* Links */}
      <Links />
      <hr />
        
      {/* Contact Information */}
      <ContactInfo />
      
      <hr />

      {/* Career Goals */}
      <CareerGoals />
      <hr />
    </div>
  );
}

function Introduction() {
  return (
    <div>
      {/* Mode Toggle */}
      <div
        style={{
          position: "absolute",
          top: "10px",
          right: "10px",
          background: "white",
          padding: "5px",
          borderRadius: "5px",
          boxShadow: "0 0 5px rgba(0,0,0,0.3)",
          cursor: "pointer",
        }}
      >
        <span id="mode-toggle" style={{ color: "rgb(93, 92, 91)" }}>🌙</span>
      </div>
      {/* Introduction */}
      <h1 style={{ color: "rgb(93, 92, 91)" }}>Ezamamti Ronald Austine ✌️</h1>
      <p>
        Yo, welcome to my personal portfolio! <br /> I am a passionate student
        currently doing the Web Programming Course. <br />
        Here, you will learn more about me and my career goals.
      </p>
    </div>
  );
}


function Personal_details() {
  return (
    <div>
      {/* Personal Details */}
      <h2>Personal Details</h2>
      <ul>
        <li>
          <strong>Full Name:</strong> Ezamamti Ronald Austine
        </li>
        <br />
        <li>
          <strong>Student RegNo:</strong> S23B23/018
        </li>
        <br />
        <li>
          <strong>Course and Year:</strong> BSCS 2:2
        </li>
        <br />
        <li>
          <strong>Hobbies and Interests:</strong> Innovating, watching anime,
          pumping iron, and Gaming
        </li>
      </ul>
    </div>
  );
}


function ContactInfo() {
  return (
    <div>
      {/* Contact Information */}
      <h2>Contact Information</h2>
      <p>
        Email:{" "}
        <a href="mailto:austineblackezamati@gmail.com">
          austineblackezamati@gmail.com
        </a>
      </p>
      <p>
        Social Media:{" "}
        <a
          href="https://x.com/Ezamighty47?t=zdjYyDzl0QZgtV8ZeR_aRg&s=08"
          target="_blank"
          rel="noopener noreferrer"
        >
          Twitter
        </a>{" "}
        |{" "}
        <a
          href="https://github.com/EzamamtiRonaldAustine/Code_UP"
          target="_blank"
          rel="noopener noreferrer"
        >
          GitHub
        </a>
      </p>
    </div>
    );
}

function Links() {
  return (
    <div>
      {/* Links */}
      <h2>Links</h2>
      <ul>
        <li>
          <a
            href="https://www.youtube.com/results?search_query=bro+code"
            target="_blank"
            rel="noopener noreferrer"
          >
            My Favorite Website
          </a>
        </li>
        <li>
          <a
            href="https://cse-ucu.com"
            target="_blank"
            rel="noopener noreferrer"
          >
            UCU Computing Department Page
          </a>
        </li>
      </ul>
    </div>
  );
}


export default App;

