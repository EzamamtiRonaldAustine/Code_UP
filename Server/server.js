const express = require('express');

const app = express();

const port = 3000;

app.get(`/hello`, (req, res)=>{
    res.send(`Hello world uso `);
})

app.listen(port, ()=>{
    console.log(`The server os running on port ${port}`);
})