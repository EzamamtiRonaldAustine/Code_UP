// calling fs, bcrypt, users modules
const fs = require('fs');
const bcrypt = require('bcrypt');

const usersFile = 'users.json';

// loading users from the JSON file
function loadUsers() {
    if (!fs.existsSync(usersFile)) {
        // If file doesn't exist, create it with an empty array
        fs.writeFileSync(usersFile, JSON.stringify([]));
    }
    
    try {
        // Reading and parsing the file
        const data = fs.readFileSync(usersFile, 'utf8');
        return data ? JSON.parse(data) : []; // Return empty array if file is empty
    } catch (error) {
        console.error("Error reading users file:", error);
        return []; // Return empty array
    }
}

// saving users to the JSON file
function saveUsers(users) {
    fs.writeFileSync(usersFile, JSON.stringify(users, null, 2));
}

// user registration
function register(rl, mainMenu) {
    rl.question('Enter your name: ', (name) => {
        rl.question('Enter your email: ', (email) => {
            rl.question('Enter your password: ', async (password) => {
                let users = loadUsers();
                if (users.some(user => user.email === email)) {
                    console.log('Email already exists! Try logging in.');
                    return mainMenu();
                }
                const hashedPassword = await bcrypt.hash(password, 10);
                users.push({ name, email, password: hashedPassword });
                saveUsers(users);
                console.log('Registration successful!👋');
                mainMenu();// Return to main menu
            });
        });
    });
}

// user login handler
function login(rl, userMenu, mainMenu) {
    rl.question('Enter your email: ', (email) => {
        rl.question('Enter your password: ', async (password) => {
            let users = loadUsers();
            let user = users.find(user => user.email === email);
            
            // password verification
            if (user && await bcrypt.compare(password, user.password)) {
                console.log('Login successful!👋');
                userMenu(user);// returns to user menu
            } else {
                console.log('Invalid credentials.');
                mainMenu();// Return to main menu if login fails
            }
        });
    });
}


// Exporting functions to be used in another module 
module.exports = {  
    loadUsers, 
    saveUsers, 
    register, 
    login 
};
