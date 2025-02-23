// Print numbers from 1 to 10 using a for loop
for (let i = 1; i <= 10; i++) {
    console.log(i);
}


// Print the multiplication table of 5 using a for loop
let number = 5;
for (let i = 1; i <= 10; i++) {
    console.log(`${number} x ${i} = ${number * i}`);
}

// Use a while loop to find the sum of numbers from 1 to 100
let sum = 0;
let count = 1;

while (count <= 100) {
    sum += count; // Add the current count to sum
    count++; // Increment count
}

console.log("Sum of numbers from 1 to 100 is:", sum);


// Print numbers from 1 to 10, but stop when it reaches 7
for (let i = 1; i <= 10; i++) {
    if (i === 7) {
        break; // Exit the loop when i is 7
    }
    console.log(i);
}

// Print numbers from 1 to 10, but stop when it reaches 7
for (let i = 1; i <= 10; i++) {
    if (i === 7) {
        break; // Exit the loop when i is 7
    }
    console.log(i);
}

// Use nested loops to print a right-angled triangle pattern
for (let i = 1; i <= 5; i++) {
    let row = '';
    for (let j = 1; j <= i; j++) {
        row += '*'; // Append '*' to the row
    }
    console.log(row); // Print the current row
}
