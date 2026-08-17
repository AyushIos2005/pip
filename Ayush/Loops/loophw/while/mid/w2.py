

def check_palindrome():
     num = int(input("Enter a number : "))

     k = num
     rev = 0   
     while k > 0:
          digit = k % 10
          rev = rev*10 + digit
          k //= 10
     if rev == num:
          print("True")
     else:
          print("False")           
def armstrong():
     num = int(input("Enter a number : "))

     k = num 
     sum = 0

     while num > 0:
          digit = num % 10
          sum += (digit ** 3)
          num //=10
     if k == sum:
          print("True")
     else:
          print("False")
def fibonacci():
     num = int(input("Enter a n-th term : "))
     print("Fibonacci series : ",end=" ")
     a,b = 0,1
     i = 0 
     result =""
     while i < num:
          result += str(a)
          a,b = b,a+b
          i += 1  
     print(result,end=" ")      
def is_prime(num):
    i = 2
    is_pr = True 

    while i * i <= num:
         if num % i == 0:
              is_pr = False
              break
         i += 1
    if is_pr:
         print(f"{num} is a prime number")
    else:
         print(f"{num} is not a prime number")
def all_factor():
     num = int(input("Enter a number : "))
     i = 1
     print("All Factor : ",end=" ")
     while i <= num:
          if num % i == 0:
               print(i,end="")
          i += 1
     print("\n")      

def largest_number(n):
      h = list(n)
    #   i = 0
      print("Largest number is : ",max(h))
def count_frequeny():
     num = input("Enter a number : ")
     s =tuple(num)
     k = input("Enter a digit that want to count :  ")
     print("Count : ",s.count(k))        
def power():
     base = int(input("Enter a Base value : "))
     power = int(input("Enter a Power value : "))
     pow = power
     mul = 1 
     while power > 0:
          mul *= base
          power -= 1
     print(base,"^",pow," = ",mul)          
def dec_bin(n):
    bin = ""
    while n > 0:
        rem = n % 2
        bin = str(rem) + bin
        n = n // 2
    print("Binary : ",bin if bin else "0") 
print("\t---Menu---")
print("1.Check if number is palindrome")
print("2.Check if number is Armstrong(3-digit)")
print("3.Print Fibonacci series upto N terms")
print("4.Check Prime number")
print("5.Print all factor")
print("6.Find largest digit in number")
print("7.Count frequency of a digit in number ")
print("8.Calculate power without using ** operator")
print("9.Convert decimal to binary")
print("10.Print this pattern(using while)")
print("11.Exit")

while True:
    choice = int(input("Enter your choice : "))

    if choice == 1:
        check_palindrome()
    elif choice == 2:
         armstrong()
    elif choice == 3:
         fibonacci()
    elif choice == 4:
         num = int(input("Enter a number for prime check : "))

         is_prime(num)
    elif choice == 5:
         all_factor()
    elif choice == 6:
         n = input("Enter a number : ")
         largest_number(n)
    elif choice == 7:
         count_frequeny()
    elif choice == 8:
         power()
    elif choice == 9:
         n = int(input("Enter a number : "))
         dec_bin(n)
    elif choice == 10:
         pattern()
    elif choice == 11:
         print("Program exited..")
         exit()     
    else:
         print("Try Again ") 
