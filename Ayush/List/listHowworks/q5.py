# 1. Reverse a List
    
#     Problem: Return the reversed list.

list_size = int(input("Enter a size of List : "))

list = []
print("Enter a List element : ")
for ele in range(list_size):
    item = int(input())
    list.append(item)

print("Original List : ",list)
print("Reverse List : ",list[::-1])




