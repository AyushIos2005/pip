'''
1. Find Maximum Element
    
    Problem: Return the largest element in the list.
'''
nums_size = int(input("Enter a size of List : "))

nums = []
print("Enter element of list : ")
for i in range(nums_size):
    item = int(input())

    nums.append(item) 

print("List : ",nums)

max_v = nums[0]

idx = -1
for i in range(1,len(nums)):
    if nums[i] > max_v:
        max_v = nums[i]
        idx = i

print("Maximum value : ",max_v,"\nAt index : ",idx)
  

