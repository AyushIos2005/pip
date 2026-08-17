# Problem: Reverse the order of words in a sentence.

s = input("Enter a String : ")

print("Input : ",s)
print("Output : "," ".join(s.split()[::-1]))