"""
5. Take number and check if it lies in:
    - 0–50
    - 51–100
    - 101–200
    - above 200
"""
while(True):
    num = int(input("Enter a number : "))

    if num >= 0:
        if num >= 0 and num <= 50:
            print(num," is lies in b/w 0 to 50")
        elif num >= 50 and num <= 100:
            print(num," is lies in b/w 51 to 100") 
        elif num >= 101 and num <=200 :
            print(num," is lies in b/w 101 to 200")
        else:
            print(num," is lies above 200")
    elif num == " ":
        exit(0)        
    else:
        print("Try Again!!")
                        