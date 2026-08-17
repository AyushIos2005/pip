# 1. Print All Factors

# Problem:

# Print all factors of N.

n = int(input("Enter a number : "))

for ele in range(1,n+1,1):
    if n % ele == 0:
        print(ele,end=" ")