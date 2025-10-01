// Include the iostream library for input and output operations
#include <iostream>

int main() {
    // Define the constant value of pi
    const double pi = 3.14159;
    int choice;
    double radius;

    do {
        // Display menu
        std::cout << "\nCircle and Sphere Calculator\n";
        std::cout << "1. Calculate Area of Circle\n";
        std::cout << "2. Calculate Circumference of Circle\n";
        std::cout << "3. Calculate Volume of Sphere\n";
        std::cout << "4. Exit\n";
        std::cout << "Enter your choice (1-4): ";
        std::cin >> choice;

        if (choice >= 1 && choice <= 3) {
            // Prompt for radius with validation
            do {
                std::cout << "Enter the radius (must be positive): ";
                std::cin >> radius;
                if (radius <= 0) {
                    std::cout << "Radius must be positive. Please try again.\n";
                }
            } while (radius <= 0);

            switch (choice) {
                case 1: {
                    // Calculate the area of the circle
                    double area = pi * radius * radius;
                    std::cout << "The area of the circle is: " << area << std::endl;
                    break;
                }
                case 2: {
                    // Calculate the circumference of the circle
                    double circumference = 2 * pi * radius;
                    std::cout << "The circumference of the circle is: " << circumference << std::endl;
                    break;
                }
                case 3: {
                    // Calculate the volume of the sphere
                    double volume = (4.0 / 3.0) * pi * radius * radius * radius;
                    std::cout << "The volume of the sphere is: " << volume << std::endl;
                    break;
                }
            }
        } else if (choice != 4) {
            std::cout << "Invalid choice. Please select 1-4.\n";
        }
    } while (choice != 4);

    std::cout << "Exiting the program.\n";
    // Return 0 to indicate successful program execution
    return 0;
}
