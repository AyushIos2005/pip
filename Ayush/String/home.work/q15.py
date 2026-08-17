'''
1. Replace Vowels
    
    Problem: Replace all vowels in `s` with '*'.
'''

s = input("Enter a String : ")

vowel = "aeiouAEIOU"


for i in vowel:
    s = s.replace(i,"*")
  


print(s)




