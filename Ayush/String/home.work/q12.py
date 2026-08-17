# Problem: Check whether strings s1 and s2 are anagrams.

s1 = "listen"
s2 = "silent"

f1 = sorted(s1)
f2 = sorted(s2)

if f1 == f2 :
    print("Is Anagram")
else:
    print("Not an Anagram")    
          