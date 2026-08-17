# school management system
# it is bad coding...

s1_name = "Aman"
s1_marks = 85
s1_attendance = 90

s2_name = "Titu"
s2_marks = 89
s2_attendance = 88



def calculate_grade(marks):
    if marks >= 90:
        return "A"
    elif marks >= 75:
        return "B"
    else:
        return "c"

def update_mark(old_marks,new_marks):
    return  new_marks



print("Student : ",s1_name)
print("Marks: ",s1_marks)
print("Grade : ",calculate_grade(s1_marks))
print("Attendance : ",s1_attendance)
print()

print("Student : ",s2_name)
print("Marks: ",s2_marks)
print("Grade : ",calculate_grade(s2_marks))
print("Attendance : ",s2_attendance)
print()

s1_marks  = update_mark(s1_marks,90)
print("After update")
print("Student : ",s1_name)
print("Marks: ",s1_marks)
print("Grade : ",calculate_grade(s1_marks))
print("Attendance : ",s1_attendance)
print()



