const express = require('express');

const app = express();

const port = 8080;

app.get(`/`, (req, res)=>{
    res.send(`Hello world uso `);
})

app.listen(port, ()=>{
    console.log(`The server os running on port ${port}`);
})