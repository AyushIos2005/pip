# 1. Factorial

# Problem:

# Compute factorial of N using loop.

n = int(input("Enter a number to calculate factorial : "))
fact = 1
for ele in range(1,n+1,1):
    if n == 0:
        break
    fact *= ele
print(n,"! = ",fact)    