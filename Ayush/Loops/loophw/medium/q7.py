# 1. Sum of Even and Odd Separately

# Problem:

# Given N, compute sum of even and odd numbers from 1 to N separately

n = int(input("Enter a number(single digit) : "))
sum_e = 0
sum_o = 0
print("Input : ",end=" ")
for ele in range(1,n+1,1):
    print(ele,end=" ")
    if ele % 2 == 0:
        sum_e += ele
    else:
        sum_o += ele
print("\nEven Sum : ",sum_e)
print("Odd Sum : ",sum_o)            


