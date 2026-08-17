# Take a number and check if it is divisible by 3, 5, or both

num = int(input("Enter a number: "))

if (num % 3 == 0) and (num % 5 == 0):
    print("Number is divisible by 3 and 5 both")

elif (num % 3 == 0):
    print("Number is divisible by 3 only")

elif (num % 5 == 0):
    print("Number is divisible by 5 only")

else:
    print("Number is not divisible by 3 or 5")