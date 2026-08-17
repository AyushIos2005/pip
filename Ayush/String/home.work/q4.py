# Problem: Count total consonants in string s

s = input("Enter String : ")
print("Input : ",s)

vowel = "aeiouAEIOU"

count = 0

for char in s:
    if char not in  vowel :
        count += 1

print("Count of consonant is : ",count)



