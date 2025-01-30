# Part a: 
def add_student(student_list, student_id, name, age, course):
    for student in student_list:
        if student['id'] == student_id:
            raise ValueError("Error: Student ID already exists.")
    student_list.append({'id': student_id, 'name': name, 'age': age, 'course': course})

# Part b: 
def find_student_by_id(student_list, student_id):
    for student in student_list:
        if student['id'] == student_id:
            return student
    raise ValueError("Error: Student not found.")

def remove_student_by_id(student_list, student_id):
    for student in student_list:
        if student['id'] == student_id:
            student_list.remove(student)
            print("Student removed successfully.")
            return
    raise ValueError("Error: Student not found.")

# Part c: 
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"{self.name}, Age: {self.age}"

class Student(Person):
    def __init__(self, name, age, course):
        super().__init__(name, age)
        self.course = course

    def study(self):
        print(f"{self.name} is studying {self.course}.")

class Instructor(Person):
    def __init__(self, name, age, subject):
        super().__init__(name, age)
        self.subject = subject

    def teach(self):
        print(f"{self.name} is teaching {self.subject}.")

# Polymorphism Demonstration
def demonstrate_polymorphism(person):
    print(person)
    if isinstance(person, Student):
        person.study()
    elif isinstance(person, Instructor):
        person.teach()

# Part d: sort_students Function
def sort_students(student_list, key_function):
    return sorted(student_list, key=key_function)


if __name__ == "__main__":
    # Initialize an empty student list
    students = []

    # Add students
    try:
        add_student(students, 1, "Ali", 22, "English")
        add_student(students, 2, "Bob", 20, "Mathematics")
        add_student(students, 3, "Charlie", 23, "Biology")
    except ValueError as e:
        print(e)

    # Find a student
    try:
        found_student = find_student_by_id(students, 2)
        print("Found student:", found_student)
    except ValueError as e:
        print(e)

    # Remove a student
    try:
        remove_student_by_id(students, 1)
    except ValueError as e:
        print(e)

    # Display remaining students
    print("Remaining students:", students)

    # Sort and display students
    students_by_age = sort_students(students, lambda student: student['age'])
    print("Sorted by age:", students_by_age)

    # Create instances of Student and Instructor
    student_instance = Student("Jane", 20, "Mathematics")
    instructor_instance = Instructor("Mr. John", 40, "Physics")

    # Demonstrate polymorphism
    demonstrate_polymorphism(student_instance)
    demonstrate_polymorphism(instructor_instance)