a = int(input("Enter a number1 : "))
b = int(input("Enter a number2 : "))

if a >= 0 and b >= 0:
    print(a," and ",b," both are Positive number.")
elif a < 0 and b < 0:
    print(a," and ",b," both are Negative number.")
else:
    print(a," and ",b," are mixed number.")
