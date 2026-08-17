class Student:
    def __init__(self,name,marks,attendance):
        self.name = name
        self.marks=marks
        self.attendance = attendance

    def calculate_grade(self):
        if self.marks >= 90:
            return "A"
        elif self.marks >= 75:
            return "B"
        else:
            return "C"

s1 = Student("Rohit",85,90)
s2 = Student("Karan",60,20)
# print(s1.name)
# print(s1.marks)
# print(s2.name)
# print(s2.marks)
print(s1.calculate_grade())





