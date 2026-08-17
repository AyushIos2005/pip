'''
4. Take marks and print:
    - "Fail" if < 35
    - "Pass" if 35–59
    - "First Class" if 60–79
    - "Distinction" if 80+
'''

marks = int(input("Enter a marks : "))

if marks < 35:
    print("Fail")
elif marks >= 35 and marks <= 59:
    print("Pass")
elif marks >= 60 and marks <= 79:
    print("First Class")
else:
    print("Distinction")    
