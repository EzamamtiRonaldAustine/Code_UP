import { useState, useEffect } from "react";

function Introduction() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add("dark-mode");
    } else {
      document.body.classList.remove("dark-mode");
    }
  }, [isDarkMode]);

  return (
    <div style={{ padding: "20px" }}>
      {/* Mode Toggle */}
      <div
        onClick={() => setIsDarkMode(!isDarkMode)}
        style={{
          position: "absolute",
          top: "10px",
          right: "10px",
          background: isDarkMode ? "#333" : "white",
          padding: "10px",
          borderRadius: "5px",
          boxShadow: "0 0 5px rgba(0,0,0,0.3)",
          cursor: "pointer",
        }}
      >
        <span style={{ color: isDarkMode ? "white" : "rgb(93, 92, 91)" }}>
          {isDarkMode ? "☀️" : "🌙"}
        </span>
      </div>

      {/* Introduction */}
      <h1 style={{ color: isDarkMode ? "white" : "rgb(93, 92, 91)" }}>
        Ezamamti Ronald Austine ✌️
      </h1>
      <p style={{ color: isDarkMode ? "#ddd" : "#333" }}>
        Yo, welcome to my personal portfolio! <br /> I am a passionate student
        currently doing the Web Programming Course. <br />
        Here, you will learn more about me and my career goals.
      </p>
    </div>
  );
}

export default Introduction;
