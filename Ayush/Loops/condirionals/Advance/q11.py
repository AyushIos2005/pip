# Take two numbers and check if they are both even, both odd, or mixed.

a = int(input("Enter a number 1 : "))
b = int(input("Enter a number 2 : "))

if (a % 2 == 0) and (b % 2 == 0) :
    print(f"Both {a} and {b} are Even")
elif (a % 2 != 0) and (b % 2 != 0):
    print(f"Both {a} and {b} are Odd")
else:
    print("Mixed Value")        

    