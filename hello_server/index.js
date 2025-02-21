const express = require('express');

const app = express();

const port = 8080;

function requestLogger(request, response, next){
    console.log(`Request Method: ${request.method}, URL: ${request.url}`);
    next();
}

app.use(requestLogger);
app.get(`/`, (req, res)=>{
    res.send(`Hello world uso `);
})

app.listen(port, ()=>{
    console.log(`The server os running on port ${port}`);
})