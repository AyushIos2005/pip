# 1. Count Uppercase and Lowercase

# Problem:

# Given string S, count uppercase and lowercase characters.


s = input("Enter a string : ")
count_l = 0
count_u =0 
for char in s:
    if char.islower():
        count_l += 1
    elif char.isupper():
        count_u += 1

print("Uppercase : ",count_u)
print("LowerCase : ",count_l)
