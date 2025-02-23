const readline = require('readline');

// Create an interface for input and output
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

let userInput;

function askQuestion() {
    rl.question("Enter a number between 1 and 10: ", (input) => {
        userInput = parseInt(input); // Convert input to an integer

        if (userInput >= 1 && userInput <= 10) {
            console.log("Valid number entered:", userInput);
            rl.close(); // Close the readline interface
        } else {
            console.log("Invalid number. Please try again.");
            askQuestion(); // Ask again if the input is invalid
        }
    });
}

// Start the question loop
askQuestion();