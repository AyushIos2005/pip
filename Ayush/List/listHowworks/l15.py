'''
1. Flatten 2D List
    
    Problem: Convert 2D list into 1D list.
'''

matrix = [[1,2],[3,4]]

arr=[]
for i in matrix:
    # arr.append(i)
    for j in i:
        arr.append(j)

print(arr)
