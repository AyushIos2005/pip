"""
1. Sum of First N Numbers

Problem:

Given N, compute the sum of numbers from 1 to N.

Input:

Integer N.

Output:

Single integer representing the sum.

Example:

Input: 5

Output:

15

"""

n = int(input("Enter a nth number : "))
sum = 0
print("Input : ",end=" ")
for i in range(1,n+1,1):
    print(i,end=" ")
    sum += i


print("\n Sum : ",sum)