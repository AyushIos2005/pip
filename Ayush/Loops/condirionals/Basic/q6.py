'''
6. Take salary and classify:
    - Low (< 30000)
    - Medium (30000–70000)
    - High (> 70000)
'''

salary = int(input("Enter a Salary : "))

if(salary < 30000):
    print("Low")
elif(salary >=30000 and salary <= 70000):
    print("Medium")
else:
    print("High")