# 1. Count Digits

# Problem:

# Given an integer N, count how many digits it contains.

n = int(input("Enter a number : "))
count = 0

for i in range(1,n+1):
    if n == 0:
        break
    n //= 10
    count += 1

print(count)