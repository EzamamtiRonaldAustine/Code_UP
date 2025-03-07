const express = require('express');
const db = require('./config.js');

const app = express();

app.use(express.json());

const port = 8080;

const sql = `CREATE TABLE IF NOT EXISTS users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL
)`;
db.query(sql, (error, results) => {
    if (error) throw error;
    console.log('Table created');
});


app.get(`/hello`, (req, res)=>{
    res.send(`Hello world uso `);
});

app.post(`/addUser`, (req, res)=>{
    const {name, email} = req.body;
    const sql = `INSERT INTO users (name, email) VALUES (?, ?)`;
    db.query(sql, [name,email], (err, res)=>{
        if (err) throw err;
        res.send('User is added successfully');
    });
});


app.get(`/users`, (req, res)=>{
    const sql = `SELECT * FROM users`;
    db.query(sql, (err, result)=>{
        if (err) throw err;
        res.send(result);
    });
});

app.listen(port, ()=>{
    console.log(`The server os running on port ${port}`)
});