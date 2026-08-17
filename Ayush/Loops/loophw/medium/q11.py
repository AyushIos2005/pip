# 1. Strong Number

# Problem:

# Check if N is Strong number (sum of factorial of digits equals number).

# Input:

# Integer N.

# Output:

# True or False.

# Example:

# Input: 145

# Output:

# True

def fact(n):
    mul = 1
    for i in range(1,n+1):
        mul *= i
    return mul

def check_strong(k,w):
    temp = w
    sum = 0
    while w > 0:
        digit = w % 10
        sum += fact(digit)
        w //= 10

    if sum == temp:
        return "True"
    else:
        return "False"
n = int(input("Enter a number : "))
w = n
k = fact(w)
print(k)
print("Output : ",check_strong(k,w))