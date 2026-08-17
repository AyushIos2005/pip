def num_print():
    n = int(input("Enter a Nth number : "))
    i = 1
    print("Output = ",end=" ")
    while i <= n:
        print(i,end="")
        i += 1
    print("\n")

def num_print_rev():
    n = int(input("Enter a Nth number : "))
    i = n
    print("Output : ",end=" ")
    while i >= 1:
        print(i,end="")
        i -= 1
    print("\n")    
def even():
    n = int(input("Enter a N-th number :  "))
    i = 1
    print("All Even number are : ",end=" ")
    while i <= n:
        if i % 2 == 0:
            print(i,end="")
        i += 1    
    print("\n")
def odd():
    n = int(input("Enter a N-th number :  "))
    i = 1
    print("All Even number are : ",end=" ")
    while i <= n:
        if i % 2 != 0:
            print(i,end="")
        i += 1    
    print("\n")
def sum_n(n):
    i = 1
    sum = 0
    while i <= n:
        sum += i
        i += 1
    return sum   
def multiple():
    n = int(input("Enter a Nth number to create table : "))
    i = 1
    while i <= 10:
        print(n,"X",i," = ",n * i)
        i += 1
    print("\n")
def count(n):
    # i = 1
    count = 0
    while n > 0:
        digit = n % 10
        count += 1
        n //= 10
        # i += 1  
    return count          
def reverse():
    n = int(input("Enter a value : "))
    rev = 0
    while n > 0:
        digit = n % 10
        rev = rev*10 + digit
        n //= 10
    print(rev)
def sum_digits(n):
    sum = 0
    while n > 0:
        digit = n % 10
        sum += digit
        n //= 10
    return sum     
def factorial(n):
    mul = 1
    i = 1
    while i <= n :
        mul *= i
        i += 1
    return mul
    

print("\t-----Menu-----")
print("1.Print number from 1 to N ")
print("2.Print number from N to 1 ")
print("3.Print all even numbers up to N")
print("4.Print all odd numbers up to N")
print("5.Find sum from 1 to N")
print("6.Print multiplication table of N")
print("7.Count digits in a number")
print("8.Reverse a number")
print("9.Sum of digits")
print("10.Print factorial of N")
print("11.Exit")


while(True):
    choice = int(input("Please Enter a Choice : "))

    if choice == 1:
        num_print()
    elif choice == 2:
        num_print_rev()
    elif choice == 3:
        even()
    elif choice == 4:
        odd()
    elif choice == 5:
        n = int(input("Enter a Nth number : "))
        print("Sum of 1 to ",n," = ",sum_n(n))
    elif choice == 6:
        multiple()
    elif choice == 7:
        n = int(input("Enter a number : "))

        print("Count of Digit : ",count(n))
    elif choice == 8:
        reverse() 
    elif choice == 9:
        n = int(input("Enter value : "))

        print("Sum of all digit of value : ",sum_digits(n))
    elif choice == 10:
        n = int(input("Enter any number : "))

        print(n,"! = ",factorial(n))  
    elif choice == 11:
        exit()
    else:
        print("Invalid Input")                         




    

    
    


