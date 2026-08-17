'''
1. Find Common Elements
    
    Problem: Return common elements between two lists.
'''

a = [1,2,3]
b = [2,3,4]

s1 = set(a)
s2 = set(b)

print("Common value are : ",s1 & s2)

