import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
// import securelocalStorage from 'react-secure-storage';
import '../login.css';

/**
 * Login component for user authentication.
 * Manages email and password state, handles form submission,
 * and redirects to the home page upon successful login.
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
        console.log("Attempting to log in with:", email, password); // Debugging log

        // Replace with an API call in production
        if (email === 'ronald@gmail.com' && password === 'password') {
            setIsAuthenticated(true);
            navigate('/home'); // Redirect to home after login
        } else {
            setError('Invalid credentials, please try again.');
        }
    };

    return (
        <div className="login-page">
            <div className="login-container">
                <h1>Login Page</h1>
                <p className="welcome-message">Aloha! 👋 Welcome. <br/> Please log in to continue.</p>

                <form onSubmit={handleSubmit}>
                    <div>
                        <label htmlFor="email">Email:</label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => {
                                setEmail(e.target.value);
                                if (error) setError(''); // Clear error only if it exists
                            }}
                            required
                            placeholder="ronald@gmail.com"
                        />
                    </div>

                    <div>
                        <label htmlFor="password">Password:</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => {
                                setPassword(e.target.value);
                                if (error) setError('');
                            }}
                            required
                            placeholder="password"
                        />
                    </div>

                    {error && <div className="error">{error}</div>} {/* Display error if exists */}

                    <button type="submit">Login</button>
                </form>
            </div>
        </div>
    );
}

export default Login;
