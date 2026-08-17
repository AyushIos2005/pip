"""
15. Take a number and check:
    - Less than 0
    - Between 0 and 100
    - Greater than 100
    - Exactly 100
"""

num = int(input("ENter a number : "))

if num < 0:
    print(f"{num} Less than 0")
elif num >= 0 and num < 100:
    print(f"{num} is lies in b/w 0 to 100")
elif num > 100:
    print(f"{num} is Greater than 100")
else:
    print(f"{num} is Exactly 100")  

