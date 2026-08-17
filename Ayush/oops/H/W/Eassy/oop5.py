class Employee:
    
    def __init__(self, sal):
        self.sal = sal

    def display_yearly(self):
        return self.sal * 12


sal = int(input("Enter a Monthly Salary: "))
e1 = Employee(sal)

x = e1.display_yearly()
print("Yearly Salary:", x)