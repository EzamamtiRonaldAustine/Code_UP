console.log(`put the water to boil`);
console.log(`Water is boiling`);
setTimeout(()=>{
    console.log(`The water is ready`);
}, 5000)

console.log(`Doing other things`);


// async function fetchUserData(){
//     console.log("Fetching Data ...");
//     let response =await fetch("url");
//     let data = await response.json();
//     console.log(data);
// }

// fetchUserData();
// console.log("Other tasks");



// async function test(){
//     return "";
// }

// test().then(result=> 
//     console.log(result)

// issues
// async function fetchData(){
//     const response = await new Promise((resolve) =>{
//         setTimeout(() => {
//             resolve("Data");
//     })
// }