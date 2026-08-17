'''
1. Print Numbers from 1 to N

Problem:

Given an integer N, print numbers from 1 to N using a for loop.

Input:

An integer N.

Output:

Numbers from 1 to N (space separated).

Example:

Input: 5

Output:

1 2 3 4 5
'''

n = int(input("Enter a number : "))

for i in range(1,n+1,1):
    print(i,end=" ")



