#  Create a class Student with grade calculation logic

class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def calculate_grade(self):
        # Logic for grade calculation
        if self.marks < 35:
            return 'D'
        elif 35 <= self.marks < 55:
            return 'C'
        elif 55 <= self.marks < 65:
            return 'B'
        else:
            return 'A'

    def display_result(self):
        grade = self.calculate_grade()
        print(f"Student: {self.name} | Marks: {self.marks} | Grade: {grade}")

# --- Main Program ---
name = input("Enter student name: ")
mark = int(input("Enter marks: "))

# Creating the instance
s1 = Student(name, mark)
s1.display_result()