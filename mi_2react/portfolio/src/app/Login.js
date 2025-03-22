import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../login.css';

/**
 * Login component for user authentication.
 * Manages email and password state, handles form submission,
 * and redirects to the profile page upon successful login.
 */
function Login({ setIsAuthenticated }) {
    // State variables for email, password, and error messages

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    /**
     * Handles form submission for login.
     * Validates credentials and updates authentication state.
     */
    const handleSubmit = (e) => {

        e.preventDefault();
        console.log("Attempting to log in with:", email, password); // Log the login attempt for debugging


        // Replace with an API call in production
        if (email === 'ronald@gmail.com' && password === 'password') {
            setIsAuthenticated(true);
            navigate('/profile');
        } else {
            setError('Invalid credentials, please try again.');
        }
    };

    return (
        <div className="login-page"> {/* Main wrapper for the login page */}

            <div className="login-container">



            <h1>Login Page</h1> {/* Title of the login page */}

            <p className="welcome-message">Aloha welcome 👋! <br/>Please log in to continue.</p> {/* Welcome message */}

            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="email">Email:</label> {/* Email input label */}

                    <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(e) => {
                            setEmail(e.target.value);
                            setError(''); // Clear error on input change
                        }}
                        required
                        placeholder="ronald@gmail.com"
                    />
                </div>
                <div>
                    <label htmlFor="password">Password:</label> {/* Password input label */}

                    <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(e) => {
                            setPassword(e.target.value);
                            setError(''); // Clear error on input change
                        }}
                        required
                        placeholder="password"
                    />
                </div>
                {error && <div className="error">{error}</div>} {/* Display error message if exists */}

                <button type="submit">Login</button>
            </form> {/* End of the login form */}

            </div>
        </div>
    );
}




export default Login;
