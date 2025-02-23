document.addEventListener('DOMContentLoaded', function() { 
    // Wait for the DOM to fully load before executing

    document.getElementById('changeColorButton').onclick = changeColor;

    function changeColor() { 
        // Change the background color based on user input or color picker

        const userColor = document.getElementById('colorInput').value; // Get user input
        const colorPickerValue = document.getElementById('colorPicker').value; // Get color picker value

        // Check if user input is valid and change background color accordingly

        if (isValidColor(userColor)) {
            document.body.style.backgroundColor = userColor; // Use user-defined color
        } else if (isValidColor(colorPickerValue)) {
            document.body.style.backgroundColor = colorPickerValue; // Use color picker value
        } else {
            document.body.style.backgroundColor = '#BA55D3'; // Default color if no valid input
        }
    }

    function isValidColor(color) { 
        // Validate the color input

        const s = new Option().style;
        s.color = color;
        return s.color !== ''; // Check if the color is valid
    }

    // function getRandomColor() { 
    // This function generates a random color (currently not in use)

    //     const letters = '0123456789ABCDEF';
    //     let color = '#';
    //     for (let i = 0; i < 6; i++) {
    //         color += letters[Math.floor(Math.random() * 16)];
    //     }
    //     return color;
    // }
});


function Changetext() { 
    // Toggle the text content of the paragraph element

    const textElement = document.getElementById('text');
    if (textElement.innerHTML === 'This is the first HTML, CSS and Javascript') {
        textElement.innerHTML = 'I am testing in line JS';
    } else {
        textElement.innerHTML = 'This is the first HTML, CSS and Javascript';
    }
}

function greet() {
    alert("Welcome Ezamamti Ronald A"); 
    // Display a welcome message when the page loads

}
