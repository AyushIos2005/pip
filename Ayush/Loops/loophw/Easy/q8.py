# 1. Sum of Digits

# Problem:

# Given N, find sum of its digits.
print("---Sum of Digit---")
n = int(input("Enter a any number : "))

sum = 0

for i in range(1,n+1,1):
    if n == 0:
        break
    temp = n % 10
    sum += temp
    n //=10

print("Sum : ",sum)