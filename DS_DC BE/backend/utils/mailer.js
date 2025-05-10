import nodemailer from 'nodemailer';
import dotenv from 'dotenv';
dotenv.config();

// Create reusable transporter object using Gmail and environment credentials
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER, // Handles emailing for the daycare web application
    pass: process.env.EMAIL_PASS  // Gmail App Password (not normal login password)
  },
});

// Function that handles sending the OTP code to reset password
// Takes in two parameters: recipient email and the OTP code
export const ResetEmail = async (email, otp) => {
  const mail = {
    from: process.env.EMAIL_USER,            // Sender
    to: email,                               // Receiver - user email
    subject: 'Password reset OTP code',      // Email subject
    text: `Your OTP code is: ${otp}`,        // Plaintext email body
  };

  try {
    await transporter.sendMail(mail);
    console.log('Email sent successfully to', email);
  } catch (err) {
    console.log(`Error in sending email: ${err}`);
  }
};
