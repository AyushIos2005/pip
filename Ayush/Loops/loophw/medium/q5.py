n = int(input("Enter a number(only 3-digit) : "))
n1 = n
arm_sum = 0
for i in range(3):
     if n1 == 0:
          break
     temp = n1 % 10
     arm_sum += (temp ** 3)
     n1 //= 10
if n == arm_sum:
     print("It an armstrong number..")
else:
     print("It not an armstrong number..")     



