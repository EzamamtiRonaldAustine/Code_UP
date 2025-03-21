import { RESULTS, RESULTS_2 } from '../util/ResultsData.js';
import React, { useState, useEffect } from 'react';
import AddCourse from './AddCourse'; // Import the AddCourse component

function ResultsComponent() {
    const [resultsList1, setResultsList1] = useState(RESULTS);
    const [resultsList2, setResultsList2] = useState(RESULTS_2);
    const [showAddCourse1, setShowAddCourse1] = useState(false);
    const [showAddCourse2, setShowAddCourse2] = useState(false);

    // Load results from local storage when the component mounts
    useEffect(() => {
        const storedResults1 = JSON.parse(localStorage.getItem('resultsList1'));
        const storedResults2 = JSON.parse(localStorage.getItem('resultsList2'));
        if (storedResults1) setResultsList1(storedResults1);
        if (storedResults2) setResultsList2(storedResults2);
    }, []);

    // Handle adding new course to the respective results array
    const handleAddCourse1 = (newCourse) => {
        const updatedResults = [...resultsList1, newCourse];
        setResultsList1(updatedResults);
        localStorage.setItem('resultsList1', JSON.stringify(updatedResults));
        setShowAddCourse1(false); // Hide AddCourse form after adding
    };

    const handleAddCourse2 = (newCourse) => {
        const updatedResults = [...resultsList2, newCourse];
        setResultsList2(updatedResults);
        localStorage.setItem('resultsList2', JSON.stringify(updatedResults));
        setShowAddCourse2(false); // Hide AddCourse form after adding
    };

    const toggleAddCourse1 = () => {
        setShowAddCourse1(!showAddCourse1);
    };

    const toggleAddCourse2 = () => {
        setShowAddCourse2(!showAddCourse2);
    };

    // Function to generate the results table
    const resultsTable = (results, key) => (
        <table key={key}>
            <thead>
                <tr>
                    <th>Course Code</th>
                    <th>Course Title</th>
                    <th>Grade</th>
                    <th>Credit Units</th>
                </tr>
            </thead>
            <tbody>
                {results.map((result, index) => (
                    <tr key={index}>
                        <td>{result.course_code}</td>
                        <td>{result.course_title}</td>
                        <td>{result.grade}</td>
                        <td>{result.credit_units}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    );

    return (
        <div>
            {/* Semester Results 1 */}
            <h2>Year 1 Semester 1 Results</h2>
            {resultsTable(resultsList1, 1)}
            <button onClick={toggleAddCourse1}>Add Course</button>
            {showAddCourse1 && <AddCourse onAddCourse={handleAddCourse1} />}

            {/* Semester Results 2 */}
            <h2>Year 1 Semester 2 Results</h2>
            {resultsTable(resultsList2, 2)}
            <button onClick={toggleAddCourse2}>Add Course</button>
            {showAddCourse2 && <AddCourse onAddCourse={handleAddCourse2} />}
        </div>
    );
}

export default ResultsComponent;
