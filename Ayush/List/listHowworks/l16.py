'''
1. Check if List is Palindrome
    
    Problem: Return true if list reads same forward and backward.
'''

nums = [1,2,3,2,1]

if nums == nums[::-1]:
    print("Palinodrome")
else:
    print("Not Palinodrome")    
