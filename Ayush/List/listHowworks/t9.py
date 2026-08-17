'''
1. Access Tuple Element
    
    Problem: Return element at index k in tuple.
'''
t = (5,10,5)
print("Tuple: ",t)

idx = int(input("Enter a index to get tuple :  "))

if idx < len(t):
    print(t[idx])
else:
    print("Out of boundary!")    
