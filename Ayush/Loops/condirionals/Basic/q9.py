# Take a character and check if it is a vowel or consonant

char = input("Enter a character: ")

if (char >= 'A' and char <= 'Z') or (char >= 'a' and char <= 'z'):
    
    if char in ['A','E','I','O','U','a','e','i','o','u']:
        print(char, "is a vowel")
    else:
        print(char, "is a consonant")

else:
    print("Not an alphabet")