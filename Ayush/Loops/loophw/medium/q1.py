# 1. Reverse a Number

# Problem:

# Reverse digits of integer N.a

n = int(input("Enter a number : "))
rev = 0
for i in range(0,n+1,1):
    if n == 0:
        break
    last_digit = n % 10
    rev = rev *10+last_digit
    n //= 10 

print("Reversed : ",rev)