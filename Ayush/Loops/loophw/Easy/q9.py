# 1. Count Vowels

# Problem:

# Given a string S, count number of vowels.

s = input("Enter a string : ")

vowel ="aeiouAEIOU"
count = 0
for i in s:
    if i in vowel :
        count += 1
print("Count of Vowel : ",count)
