// Include the iostream library for input and output operations
#include <iostream>

int main() {
    // Declare a variable to store the radius of the circle
    double radius;
    // Define the constant value of pi
    const double pi = 3.14159;

    // Prompt the user to enter the radius
    std::cout << "Enter the radius of the circle: ";
    // Read the radius value from user input
    std::cin >> radius;

    // Calculate the area of the circle using the formula: area = pi * radius * radius
    double area = pi * radius * radius;

    // Display the calculated area to the user
    std::cout << "The area of the circle is: " << area << std::endl;

    // Return 0 to indicate successful program execution
    return 0;
}
