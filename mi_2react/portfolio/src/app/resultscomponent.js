import { RESULTS, RESULTS_2 } from '../util/ResultsData.js'; 
import React, { useState, useEffect } from 'react';
import AddCourse from './AddCourse'; // Import the AddCourse component

/**
 * ResultsComponent manages two lists of course results.
 * It allows users to add, delete, and reset courses,
 * and persists data in local storage.
 */
function ResultsComponent() {
    // State variables for two lists of results and visibility of add course forms

    const [resultsList1, setResultsList1] = useState(RESULTS);
    const [resultsList2, setResultsList2] = useState(RESULTS_2);
    const [showAddCourse1, setShowAddCourse1] = useState(false);
    const [showAddCourse2, setShowAddCourse2] = useState(false);

    /**
     * useEffect hook to retrieve stored results from local storage
     * when the component mounts.
     */
    useEffect(() => {

        const storedResults1 = JSON.parse(localStorage.getItem('resultsList1'));
        const storedResults2 = JSON.parse(localStorage.getItem('resultsList2'));
        if (storedResults1) setResultsList1(storedResults1);
        if (storedResults2) setResultsList2(storedResults2);
    }, []);

    /**
     * Handles adding a new course to the first results list.
     * Updates state and local storage with the new course.
     */
    const handleAddCourse1 = (newCourse) => {

        const updatedResults = [...resultsList1, newCourse];
        setResultsList1(updatedResults);
        localStorage.setItem('resultsList1', JSON.stringify(updatedResults));
        setShowAddCourse1(false);
    };

    /**
     * Handles adding a new course to the second results list.
     * Updates state and local storage with the new course.
     */
    const handleAddCourse2 = (newCourse) => {

        const updatedResults = [...resultsList2, newCourse];
        setResultsList2(updatedResults);
        localStorage.setItem('resultsList2', JSON.stringify(updatedResults));
        setShowAddCourse2(false);
    };

    const toggleAddCourse1 = () => setShowAddCourse1(!showAddCourse1);
    const toggleAddCourse2 = () => setShowAddCourse2(!showAddCourse2);

    /**
     * Handles deleting a course from the first results list.
     * Updates state and local storage after deletion.
     */
    const handleDeleteCourse1 = (index) => {

        const updatedResults = resultsList1.filter((_, i) => i !== index);
        setResultsList1(updatedResults);
        localStorage.setItem('resultsList1', JSON.stringify(updatedResults));
    };

    /**
     * Handles deleting a course from the second results list.
     * Updates state and local storage after deletion.
     */
    const handleDeleteCourse2 = (index) => {

        const updatedResults = resultsList2.filter((_, i) => i !== index);
        setResultsList2(updatedResults);
        localStorage.setItem('resultsList2', JSON.stringify(updatedResults));
    };

    /**
     * Resets the first results list to the initial state.
     * Updates local storage with the default results.
     */
    const handleResetTable1 = () => {

        setResultsList1(RESULTS);
        localStorage.setItem('resultsList1', JSON.stringify(RESULTS));
    };

    /**
     * Resets the second results list to the initial state.
     * Updates local storage with the default results.
     */
    const handleResetTable2 = () => {

        setResultsList2(RESULTS_2);
        localStorage.setItem('resultsList2', JSON.stringify(RESULTS_2));
    };

    /**
     * Renders a table of results.
     * Displays course details and provides a delete action.
     */
    const resultsTable = (results, handleDelete) => (

        <table>
            <thead>
                <tr>
                    <th>Course Code</th>
                    <th>Course Title</th>
                    <th>Grade</th>
                    <th>Credit Units</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {results.map((result, index) => (
                    <tr key={index}>
                        <td>{result.course_code}</td>
                        <td>{result.course_title}</td>
                        <td>{result.grade}</td>
                        <td>{result.credit_units}</td>
                        <td>
                            <button onClick={() => handleDelete(index)}>Delete</button>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );

    return (
        <div> {/* Main wrapper for the results component */}

            {/* Semester Results 1 */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <h2>Year 1 Semester 1 Results</h2>
                <button 
                    onClick={handleResetTable1} 
                    style={{
                        backgroundColor: '#ff4d4d',
                        color: 'white',
                        border: 'none',
                        padding: '8px 15px',
                        cursor: 'pointer',
                        borderRadius: '5px',
                        fontWeight: 'bold',
                        transition: 'background-color 0.3s ease-in-out'
                    }}
                    onMouseEnter={(e) => e.target.style.backgroundColor = '#cc0000'}
                    onMouseLeave={(e) => e.target.style.backgroundColor = '#ff4d4d'}
                >
                    Reset Table
                </button>
            </div>
            {resultsTable(resultsList1, handleDeleteCourse1)}
            <button onClick={toggleAddCourse1}>Add Course</button> {/* Button to toggle adding a course to the first results list */}

            {showAddCourse1 && <AddCourse onAddCourse={handleAddCourse1} />}

            {/* Semester Results 2 */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <h2>Year 1 Semester 2 Results</h2>
                <button 
                    onClick={handleResetTable2} 
                    style={{
                        backgroundColor: '#ff4d4d',
                        color: 'white',
                        border: 'none',
                        padding: '8px 15px',
                        cursor: 'pointer',
                        borderRadius: '5px',
                        fontWeight: 'bold',
                        transition: 'background-color 0.3s ease-in-out'
                    }}
                    onMouseEnter={(e) => e.target.style.backgroundColor = '#cc0000'}
                    onMouseLeave={(e) => e.target.style.backgroundColor = '#ff4d4d'}
                >
                    Reset Table
                </button>
            </div>
            {resultsTable(resultsList2, handleDeleteCourse2)}
            <button onClick={toggleAddCourse2}>Add Course</button> {/* Button to toggle adding a course to the second results list */}

            {showAddCourse2 && <AddCourse onAddCourse={handleAddCourse2} />}
        </div>
    );
}

export default ResultsComponent;
