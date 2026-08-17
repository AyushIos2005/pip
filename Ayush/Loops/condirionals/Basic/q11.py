# 11. Take a number and check if it is 1-digit, 2-digit, or 3-digit.

digit = int(input("Enter a number : "))

if (digit >= 0 and digit < 10):
    print(digit,"is 1-Digit")
elif (digit >=10 and digit < 100):
    print(digit,"is 2-digit")    
elif (digit >=100 and digit < 1000):
    print(digit,"is 3-digit")
else:
    print(digit,"Greater than 3-digit")
        
