
'''
5. Take temperature and print:
    - "Cold" if < 15
    - "Warm" if 15–30
    - "Hot" if > 
    

'''

temp = int(input("Enter a Temperature : "))

if temp < 15 :
    print("Cold")
elif temp >= 15 and temp <= 30:
    print("Warm")
else:
    print("Hot")    

