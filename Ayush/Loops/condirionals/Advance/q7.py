num = int(input("Enter a number : "))

size = len(str(num))

temp = num 
sum = 0

while temp > 0:
    digit = temp % 10
    sum += digit ** size
    temp //= 10

if num == sum:
    print(num," is an Armstrong Number")
else:
    print(num," is not an Armstrong Number")    