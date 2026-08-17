'''
3. Take age and print:
    - "Child" if age < 13
    - "Teen" if age 13–19
    - "Adult" otherwise
'''

age = int(input("Enter a age : "))

if age < 13:
    print("You are Child")
elif (age >= 13 and age <= 19 ):
    print("You are Teen")
else:
    print("You are Adult")      