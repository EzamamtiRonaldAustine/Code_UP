document.addEventListener("DOMContentLoaded", function() {
    const background = document.getElementById('mode-toggle'); // Get the toggle button
    const body = document.body;

    background.onclick = function() {
        if (background.innerHTML == "🌙") {
            body.classList.add('dark-mode'); // Add dark mode class
            background.innerHTML = "☀️"; // Change button to sun icon
        } else {
            body.classList.remove('dark-mode'); // Remove dark mode class
            background.innerHTML = "🌙"; // Change button to moon icon
        }
    }
});