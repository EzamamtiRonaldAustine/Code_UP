import React, { useState } from 'react';

function AddCourse({ onAddCourse }) {
    const [newCourse, setNewCourse] = useState({ course_code: '', course_title: '', grade: '', credit_units: '' });

    const handleAddCourse = () => {
        if (newCourse.course_code && newCourse.course_title && newCourse.grade && newCourse.credit_units) {
            onAddCourse(newCourse);
            setNewCourse({ course_code: '', course_title: '', grade: '', credit_units: '' });
        } else {
            alert("Please fill in all fields.");
        }
    };

    return (
        <div>
            <h3>Add New Course</h3>
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
            <button onClick={handleAddCourse}>Submit</button>
        </div>
    );
}

export default AddCourse;
