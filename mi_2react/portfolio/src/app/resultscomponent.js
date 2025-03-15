import {RESULTS} from '../util/ResultsData.js';
function ResultsComponent() {
    console.log("My Results",RESULTS);

    const resultsList = RESULTS.map(result => 
        <tr>
            <td>{result.course_code}</td>
            <td>{result.course_title}</td>
            <td>{result.grade}</td>
            <td>{result.credit_units}</td>
        </tr>
    );

    console.log("My Results data",resultsList);

    return (
      <div>
        {/* Semester Results */}
        <h2>Year 1 Semester 1 Results</h2>
        <table>
          
            <tr>
              <th>Course Code Test</th>
              <th>Course Title</th>
              <th>Grade</th>
              <th>Credit Units</th>
            </tr>
          
          {resultsList}
        </table>
      </div>
    );
  }

export default ResultsComponent;