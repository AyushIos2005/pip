# 1. Largest Digit

# Problem:

# Find largest digit in N.

# Input:

# Integer N.

# Output:

# Largest digit.

# Example:

# Input: 5482

# Output:

# 8

n = input("Enter a number : ")

max_digi = 0

for i in n:
    digit = int(i)
    if digit > max_digi:
        max_digi = digit 
print("Largest Digit : ",max_digi)        