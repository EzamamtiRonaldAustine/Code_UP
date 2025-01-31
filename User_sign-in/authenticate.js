// Calling the modules using require
const readline = require('readline');
const { register, login } = require('./functions');

// Creating readline interface for user input
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});


// Displaying user menu after login
function userMenu(user) {
    console.log(`\nWelcome, ${user.name}!`);
    console.log('1. View Profile');
    console.log('2. Logout');
    console.log('3. Exit');
    rl.question('Choose an option: ', (option) => {
        if (option === '1') {
            console.log(`Name: ${user.name}, Email: ${user.email}`);
            userMenu(user);
        } else if (option === '2') {
            console.log('Logged out.👍');
            mainMenu();
        } else if (option === '3') {
            console.log('Goodbye!🤚');
            rl.close();
        } else {
            console.log('Invalid option. Try again.');
            userMenu(user);
        }
    });
}

// Displaying main menu
function mainMenu() {
    console.log('\n1. Register');
    console.log('2. Login');
    console.log('3. Exit');
    rl.question('Choose an option: ', (option) => {
        if (option === '1') register(rl, mainMenu);// calling register func
        else if (option === '2') login(rl, userMenu, mainMenu);// calling login func
        else if (option === '3') {
            console.log('Goodbye!🤚');
            rl.close();
        } else {
            console.log('Invalid option. Try again.');
            mainMenu();
        }
    });
}

// Starting the authentication system 
mainMenu();
