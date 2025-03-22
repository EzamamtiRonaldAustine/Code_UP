import React, { useState } from 'react';

/**
 * AddCourse component for adding new course details.
 * Manages state for course code, title, grade, and credit units.
 */
function AddCourse({ onAddCourse }) {
    // State for the new course details

    const [newCourse, setNewCourse] = useState({ course_code: '', course_title: '', grade: '', credit_units: '' });

    /**
     * Handles the addition of a new course.
     * Validates input and calls the onAddCourse function.
     */
    const handleAddCourse = () => {

        if (newCourse.course_code && newCourse.course_title && newCourse.grade && newCourse.credit_units) {
            onAddCourse(newCourse);
            setNewCourse({ course_code: '', course_title: '', grade: '', credit_units: '' });
        } else {
            alert("Please fill in all fields."); // Alert if any field is empty

        }
    };

    return (
        <div> {/* Main wrapper for the AddCourse component */}

            <h3>Add New Course</h3> {/* Header for the add course form */}

            <input 
                type="text" 
                placeholder="Course Code" 
                value={newCourse.course_code} 
                onChange={(e) => setNewCourse({ ...newCourse, course_code: e.target.value })} 
            />
            <input 
                type="text" 
                placeholder="Course Title" 
                value={newCourse.course_title} 
                onChange={(e) => setNewCourse({ ...newCourse, course_title: e.target.value })} 
            />
            <input 
                type="text" 
                placeholder="Grade" 
                value={newCourse.grade} 
                onChange={(e) => setNewCourse({ ...newCourse, grade: e.target.value })} 
            />
            <input 
                type="text" 
                placeholder="Credit Units" 
                value={newCourse.credit_units} 
                onChange={(e) => setNewCourse({ ...newCourse, credit_units: e.target.value })} 
            />
            <button onClick={handleAddCourse}>Submit</button> {/* Button to submit the new course */}

        </div>
    );
}

export default AddCourse;
