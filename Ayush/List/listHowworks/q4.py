'''
1. Count Even Numbers
    
    Problem: Count how many even numbers are present in the list.
'''


nums_size = int(input("Enter a size of List : "))

li = []
print("Enter element of list : ")
for i in range(nums_size):
    item = int(input())

    li.append(item) 

print("List : ",li)

count = 0

for ele in range(nums_size):
    if li[ele] % 2 == 0:
        count += 1

print("Count of Even in List : ",count)
