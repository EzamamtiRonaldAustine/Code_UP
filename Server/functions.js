// a function with a return statement
// function name(){
//     return;
// }

// const name = (param) =>{
//     return param;
// }

// //a void function
// function name(){
//     console.log();
// }

// const name = () =>{
//     console.log();
// }

// function Greeting(){
//     return welcome = `Welcome back ${firstName} 👊`;   
// }

// let firstName = "Max";
// console.log(Greeting());

function Greeting(firstName){
    let message = "Welcome back";
    console.log(`${message} ${firstName} 👊`); 
}

Greeting("Jack")