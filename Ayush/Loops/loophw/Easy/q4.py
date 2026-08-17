# Given N, count how many even numbers exist between 1 and N.

n =int(input("Enter any number : "))
count = 0
for i in range(1,n+1,1):
    if i % 2 == 0:
        count += 1
        print(i,end=" ")
print("\nCount of Even number are : ",count)    