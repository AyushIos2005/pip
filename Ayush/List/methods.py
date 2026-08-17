# my_list = [10,20,30,40,50]

# print(my_list[-1])
# print(my_list[0])

'''
user input = list [10 - 12 items]
target element = input

serach , 1 by 1 element
else not found

'''

list = []

print("Enter atleast 10 element : ")

for i in range(10):
    item = input()
    list.append(item)

print("List : ",list)
target = input("Enter a target element : ")

ele = 0
idx = 0
for i in range(len(list)):
    if list[i] == target:
        ele = 1
        idx = i
        break
    else:
        ele = -1

if ele == 1:
    print("Found at ",idx)
else:
    print("Not Found")    




    
