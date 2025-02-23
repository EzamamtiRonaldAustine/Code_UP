// 1
let temperature = 25; 

if (temperature > 30) {
    console.log("It's too hot!");
} else if (temperature >= 20 && temperature <= 30) {
    console.log("It's moderate.");
} else {
    console.log("It's cold.");
}

// 2
let score = 55; 

if (score >= 70) {
    console.log("Eligible for Admission.");
} else if (score >= 50 && score < 70) {
    console.log("Admission on Probation.");
} else {
    console.log("Not Eligible for Admission.");

}


// 3
let waterAvailable = 300; // You can change this value to test different water availability

if (waterAvailable > 500) {
    console.log("Enough Water.");
} else if (waterAvailable >= 200 && waterAvailable <= 500) {
    console.log("Water is limited.");
} else {
    console.log("Water shortage.");
}

// 4
let expired = false; 
let quality = 7; 

if (expired) {
    console.log("Do not use.");
} else {
    if (quality > 8) {
        console.log("Good Quality.");
    } else if (quality >= 5 && quality <= 8) {
        console.log("Average Quality.");
    } else {
        console.log("Poor Quality.");
    }
}