import db from '../config/db.js';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';//research on this
import { generateTokenAndSetCookie } from '../utils/tokenGenerator.js';
import { ResetEmail } from '../utils/mailer.js';

export const register = async (req, res) => {
  try {
    const { username, email, password, role } = req.body;

    if (!username || !email || !password) {
      return res.status(400).json({ message: 'All fields are required' });
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({ message: 'Invalid email' });
    }

    const [existingUsers] = await db.query('SELECT * FROM users WHERE email = ?', [email]);
    if (existingUsers.length > 0) {
      return res.status(400).json({ message: 'User already exists' });
    }

    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);
    const userRole = role || 'babysitter';

    const [result] = await db.query(
      'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
      [username, email, hashedPassword, userRole]
    );

    generateTokenAndSetCookie(result.insertId, userRole, res);
    res.status(201).json({ message: 'User registered successfully' });
  } catch (error) {
    console.log(`Error in registering user: ${error.message}`);
    res.status(500).json({ message: 'Error in registering new user' });
  }
};

export const login = async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      return res.status(400).json({ message: 'Please enter both email and password' });
    }

    const [users] = await db.query('SELECT * FROM users WHERE email = ?', [email]);
    if (!users.length) {
      return res.status(400).json({ message: 'Invalid email or password' });
    }

    const user = users[0];
    const isPasswordMatch = await bcrypt.compare(password, user.password);
    if (!isPasswordMatch) {
      return res.status(400).json({ message: 'Invalid password' });
    }

    generateTokenAndSetCookie(user.user_id, user.role, res);
    
    // Send user info in response
    res.status(200).json({ 
      message: 'User logged in successfully',
      userId: user.user_id,
      role: user.role,
      email: user.email
    });
  } catch (error) {
    console.log(`Error in logging in user: ${error}`);
    res.status(500).json({ message: 'Error in logging in user' });
  }
};

export const logout = async (req, res) => {
  try {
    res.clearCookie('jwt');
    res.status(200).json({ message: 'User logged out successfully' });
  } catch (error) {
    console.log(`Error in logging out user: ${error}`);
    res.status(500).json({ message: 'Error in logging out user' });
  }
};

export const forgotPassword = async (req, res) => {
  try {
    const { email } = req.body;
    if (!email) {
      return res.status(400).json({ message: 'Please enter your email' });
    }

    const [user] = await db.query('SELECT * FROM users WHERE email = ?', [email]);
    if (!user.length) {
      return res.status(400).json({ message: 'Error finding user' });
    }

    const otp = Math.floor(10000 + Math.random() * 90000);
    const otpExpires = new Date(Date.now() + 10 * 60 * 1000);

    await db.query('UPDATE users SET otp_code = ?, otp_expires = ? WHERE email = ?', [otp, otpExpires, email]);
    await ResetEmail(email, otp);
    res.status(200).json({ message: 'OTP code sent successfully' });
  } catch (error) {
    console.log(`Forgot password error: ${error}`);
    res.status(500).json({ message: 'Error in forgot password' });
  }
};

export const verifyOTP = async (req, res) => {
  try {
    const { email, otp } = req.body;
    if (!email || !otp) {
      return res.status(400).json({ message: 'Please enter your email and OTP code' });
    }

    const [user] = await db.query('SELECT * FROM users WHERE email = ? AND otp_code = ?', [email, otp]);
    if (!user.length) {
      return res.status(400).json({ message: 'Invalid OTP code' });
    }

    const { otp_expires } = user[0];
    if (new Date() > new Date(otp_expires)) {
      return res.status(400).json({ message: 'OTP code has expired' });
    }
    res.status(200).json({ message: 'OTP code verified successfully' });
  } catch (error) {
    console.log(`Error in verifying OTP: ${error}`);
    res.status(500).json({ message: 'Error in verifying OTP' });
  }
};

export const resetPassword = async (req, res) => {
  try {
    const { email, newPassword } = req.body;
    if (!email || !newPassword) {
      return res.status(400).json({ message: 'Please enter your email and new password' });
    }

    const [user] = await db.query('SELECT * FROM users WHERE email = ?', [email]);
    if (!user.length) {
      return res.status(400).json({ message: 'Error finding user' });
    }

    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(newPassword, salt);
    await db.query('UPDATE users SET password = ?, otp_code = NULL, otp_expires = NULL WHERE email = ?', [hashedPassword, email]);

    res.status(200).json({ message: 'Password reset successfully. Please login with your new password' });
  } catch (error) {
    console.log(`Error in resetting password: ${error}`);
    res.status(500).json({ message: 'Error in resetting password' });
  }
};
// Middleware to verify JWT from cookie and attach user to request
export const getCurrentUser = (req, res) => {
  if (!req.user) {
    return res.status(401).json({ message: 'Unauthorized. No user info.' });
  }

  res.status(200).json({
    message: 'User verified',
    user: req.user
  });
};