# Take salary and experience and classify promotion eligibility.
sal = int(input("Enter a Salary : "))
exp = int(input("Enter a Experience : "))

if sal >= 60000 and exp >= 3:
    print("Promotion Desired")
else:
    print("Better Luck Next Time")
        
