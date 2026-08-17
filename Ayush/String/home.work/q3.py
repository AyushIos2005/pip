# Problem: Count total vowels in string s

s = input("Enter String : ")
print("Input : ",s)

vowel = "aeiouAEIOU"

count = 0

for char in s:
    if char in  vowel :
        count += 1

print("Count of Vowel is : ",count)



