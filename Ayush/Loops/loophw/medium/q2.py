# 1. Prime Check

# Problem:

# Determine if N is prime.

n = int(input("Enter a number : "))

if n < 2:
    print("Not Prime")
else:
    # Hum sirf square root tak check karte hain (efficiency ke liye)
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            print("Not Prime")
            break
    else:
        # Ye tab chalega jab loop pura khatam ho jaye bina break ke
        print("Prime Number")