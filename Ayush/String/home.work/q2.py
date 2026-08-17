"""
Problem: Determine whether a string s is a palindrome.
"""

s = input("Enter String : ")
print("Input : ",s)

li = s[::-1]

if li == s:
    print("It a palindrome")
else:
    print("It not a palindrome")    