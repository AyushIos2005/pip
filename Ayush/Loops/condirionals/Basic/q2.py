# Take a number and check if it is even or odd.

num = int(input("Enter a number : "))

if num > 0:
    if num % 2 == 0:
        print("Number is Even")
    elif num % 2 != 0:
        print("Number is Odd")
elif num < 0 or num == 0:
    if(num < 0) :
        print("It Negative Number")
    else:
        print("Number is Zero")    

