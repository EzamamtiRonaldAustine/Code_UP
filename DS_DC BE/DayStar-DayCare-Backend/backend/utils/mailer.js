// This is to help in acccessing email service from other files
const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USERNAME,
    pass: process.env.EMAIL_PASSWORD,
  },
});

const sendEmail = async ({ to, subject, text, html }) => {
  const mailOptions = {
    from: process.env.EMAIL_USERNAME,
    to,
    subject,
    text,
    html,
  };

  return transporter.sendMail(mailOptions);
};

module.exports = { sendEmail };
