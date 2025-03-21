import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../login.css';

function Login({ setIsAuthenticated }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log("Attempting to log in with:", email, password);

        // Replace with an API call in production
        if (email === 'ronald@gmail.com' && password === 'password') {
            setIsAuthenticated(true);
            navigate('/profile');
        } else {
            setError('Invalid credentials, please try again.');
        }
    };

    return (
        <div className="login-page"> {/* New wrapper div */}
            <div className="login-container">



            <h2>Login</h2>
            <p className="welcome-message">Welcome to your portfolio! Please log in to continue.</p>
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="email">Email:</label>
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
                    <label htmlFor="password">Password:</label>
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
                {error && <div className="error">{error}</div>}
                <button type="submit">Login</button>
            </form>
            </div>
        </div>
    );
}




export default Login;
