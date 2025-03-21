import { RESULTS, RESULTS_2 } from '../util/ResultsData.js'; 
import React, { useState, useEffect } from 'react';
import AddCourse from './AddCourse'; // Import the AddCourse component

function ResultsComponent() {
    const [resultsList1, setResultsList1] = useState(RESULTS);
    const [resultsList2, setResultsList2] = useState(RESULTS_2);
    const [showAddCourse1, setShowAddCourse1] = useState(false);
    const [showAddCourse2, setShowAddCourse2] = useState(false);

    useEffect(() => {
        const storedResults1 = JSON.parse(localStorage.getItem('resultsList1'));
        const storedResults2 = JSON.parse(localStorage.getItem('resultsList2'));
        if (storedResults1) setResultsList1(storedResults1);
        if (storedResults2) setResultsList2(storedResults2);
    }, []);

    const handleAddCourse1 = (newCourse) => {
        const updatedResults = [...resultsList1, newCourse];
        setResultsList1(updatedResults);
        localStorage.setItem('resultsList1', JSON.stringify(updatedResults));
        setShowAddCourse1(false);
    };

    const handleAddCourse2 = (newCourse) => {
        const updatedResults = [...resultsList2, newCourse];
        setResultsList2(updatedResults);
        localStorage.setItem('resultsList2', JSON.stringify(updatedResults));
        setShowAddCourse2(false);
    };

    const toggleAddCourse1 = () => setShowAddCourse1(!showAddCourse1);
    const toggleAddCourse2 = () => setShowAddCourse2(!showAddCourse2);

    const handleDeleteCourse1 = (index) => {
        const updatedResults = resultsList1.filter((_, i) => i !== index);
        setResultsList1(updatedResults);
        localStorage.setItem('resultsList1', JSON.stringify(updatedResults));
    };

    const handleDeleteCourse2 = (index) => {
        const updatedResults = resultsList2.filter((_, i) => i !== index);
        setResultsList2(updatedResults);
        localStorage.setItem('resultsList2', JSON.stringify(updatedResults));
    };

    const handleResetTable1 = () => {
        setResultsList1(RESULTS);
        localStorage.setItem('resultsList1', JSON.stringify(RESULTS));
    };

    const handleResetTable2 = () => {
        setResultsList2(RESULTS_2);
        localStorage.setItem('resultsList2', JSON.stringify(RESULTS_2));
    };

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
        <div>
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
            <button onClick={toggleAddCourse1}>Add Course</button>
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
            <button onClick={toggleAddCourse2}>Add Course</button>
            {showAddCourse2 && <AddCourse onAddCourse={handleAddCourse2} />}
        </div>
    );
}

export default ResultsComponent;
