'''
1. Check Element Exists
    
    Problem: Return true if target exists in list.
'''

li_size = int(input("Enter a list Size : "))

list = []

print("Enter a element of List : ")
for ele in range(li_size):
    list.append(int(input()))

print("List : ",list)

target = int(input("Enter a target : "))

found = 0
idx = 0
for i in range(li_size):
    if target == list[i]:
        found = 1
        idx = i
        break

if found == 1:
    print(target,"found at index ",idx)
else:
    print(target,"Not found !!")    