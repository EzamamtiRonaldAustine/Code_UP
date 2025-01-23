//single line comment
/**
 * Multi line
 */

//Variables

//const
const PI = 3.14;//float

// PI = 3.023
console.log(PI)

//let
let num_one = 3;//int

let num_two = 5;


//var
var num_three = 6;

var name = "Mark1"; //string

function addnums(){
    let num_four = 34;
    console.log(num_four)
}

console.log(num_one)

/**
 * DataTypes
 */

//Int
var num1 = 6;
var num2 = 4;
console.log(num1 + num2)
console.log(num1 - num2)
console.log(num1 * num2)

var num1 = 3;
var num2 = 5;

add = num1 + num2
console.log(add)


//Strings

let firstName = 'John';
let lastName = "Wick";

let welcome = `Welcome back ${firstName} 👊`;
console.log(welcome)
console.log(firstName.toLowerCase());
console.log(firstName.toUpperCase());
console.log(firstName.length);

let IsStudent = true;
let IsinHall = false;
console.log(IsStudent && IsinHall)
console.log(IsStudent || IsinHall)

//Arrays

let fruits = ["mangoes", "oranges", "grapes"]
console.log(fruits);

//appending items 
fruits.push("apples");
fruits.push("pineapples");

//removing values from the array
fruits.pop()
console.log(fruits)

//Objects 
let credentials = {
    "email": "chmuganga@ucu.ac.ug",
    "password": "123456"
}

let signUp = {
    "name": "John Wick",
    "age" : "35",
    "country": "USA",
    "city": "New York",
    "email" : "johnwick@gmail.com",
    "password" : 123456,
    "contact" : "12345678"
}

console.log(signUp.email);
console.log(signUp);
signUp["username"] = "Boogieman"
signUp["confirmPassword"] = "123456"
console.log(signUp);
console.log(signUp.name);

//comparison operators
console.log(signUp.password == signUp.confirmPassword)
console.log(signUp.password === signUp.confirmPassword)

// for in loop
// for(initialization in storage){
//     results
// }
for(n in fruits) {
    console.log(fruits[n]);
}

// for of loop
// for(initialization of storage){
//     results
// }
for(n of fruits) {
    console.log(n);
}
