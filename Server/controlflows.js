//if statements 
/*
if (condition){

}else if(condition){

}else{

}
*/
var age = 28;
if (age <=18 & age >=15){
    console.log("You are a teenager");
}else if (age <15){
    console.log("You are a child");
}else if(age >18 & age<=30){
    console.log("You are a Youth");    
}else{
    console.log("You are an Adult");
}


//for loop
/*
for(initialization, condition, increment){
    results
}
*/

//while loop
/*
initialization
while(condition){
    results
    increment
}
*/

for(k=1; k<=100; k++){
    console.log(k);
}

// n = 1
// while(n <= 100){
//     console.log(n);
//     n++;
// }

//switch
/*
switch(param){
    case:
    break;

    case:
    break;

    default:
}
*/

var day = 3;
switch(day){
    case 1:
        console.log("Monday");
        break;
    case 2:
        console.log("Tuesday");
        break;
    case 3:
        console.log("Wednesday");
        break;
    case 4:
        console.log("Thursday");
        break;
    case 5:
        console.log("Friday");
        break;
    case 6:
        console.log("Saturday");
        break;
    case 7:
        console.log("Sunday");
        break;
    default:
        console.log("Sleep day");
    }