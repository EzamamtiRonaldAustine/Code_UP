import mysql from 'mysql2/promise'; 
import dotenv from 'dotenv';
dotenv.config();

const db = await mysql.createConnection({
  host: process.env.HOST,
  user: process.env.USER,
  password: process.env.PASSWORD,
  port: process.env.PORT || 3000 ,
  database: process.env.DATABASE,
});

console.log('✅ Connected to MySQL Database');
export default db;
