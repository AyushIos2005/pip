"""
6. Take character input and check:
    - uppercase
    - lowercase
    - digit
    - special character
"""
char = input("Enter an any character : ")
if char.isupper() :
    print("UpperCase")
elif char.islower():
    print("LowerCase")
elif char.isdigit():
    print("Digit")
else:
    print("Special Character")             