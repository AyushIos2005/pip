# 1. Pattern Printing – Increasing Stars

# Problem:

# Print pattern:

# Input: 4

# Output:

# *

# **

n = 4

for i in range(1,n+1,1):
    for j in range(1,i+1,1):
        if (j % 2 == 0) and (i % 2 == 0):
            print("*",end=" ")

    print()        