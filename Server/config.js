const mysql = require('mysql');
require('dotenv').config();
const db = mysql.createConnection({
    host: process.env.HOST,
    user: process.env.USER,
    password: process.env.PASSWORD,
    port: process.env.PORT,
    database: process.env.DATABASE
});

db.connect((error) => {
    if (error) throw error;
    console.log('Connected to database');
});

module.exports = db;