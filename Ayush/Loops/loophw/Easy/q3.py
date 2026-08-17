# Given an integer N, print its multiplication table up to 10.

n = int(input("Enter a number to  create table : "))

print("Table of ",n)
for i in range(1,11,1):
    print(n," X ",i," = ",n*i)

