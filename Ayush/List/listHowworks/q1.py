'''
Problem: Given a list of integers, return the sum of all elements.

Input:
nums= [1,2,3,4]

Output:
10

'''

n = int(input("Enter a length of list : "))
li=[]
print("Enter a element of List : ")
for ele in range(n):
    x = int(input())
    li.append(x)
print("List : ",li)

sum = 0

for ele in range(len(li)):
    sum += li[ele]

print("Sum of list elements are : ",sum)


