# # 1. Reverse Counting

# Problem:

# Print numbers from N down to 1.

n = int(input("Enter a any number for reverse counting : "))

for i in range(n,0,-1):
    print(i,end=" ")