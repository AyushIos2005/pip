"""
1. Count Uppercase & Lowercase
    
    Problem: Count uppercase and lowercase letters.
"""

s = input("Enter any string : ")
count_1 = 0
count_0 = 0

for i in s:
    if i.islower():
        count_1 += 1
        
    elif i.isupper():
        count_0 += 1
    
print("Count of UpperCase : ",count_0)
print("Count of Lowercase : ",count_1)