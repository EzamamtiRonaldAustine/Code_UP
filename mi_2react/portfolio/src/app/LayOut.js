import { Outlet, Link } from "react-router-dom";

function LayOut() {
    return (
    <>
    <nav>
        <h1>My Portfolio</h1>
        <ul>
            <li><Link to="/home">Home</Link></li>
            <li><Link to="/results">Results</Link></li>
            <li><Link to="/hobbies">Hobbies</Link></li>
            <li><Link to="/contact">Contact</Link></li> 

        </ul>
    </nav>
    <Outlet />
    
    </>
    );
    
}
export default LayOut;