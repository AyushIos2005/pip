''''
try
except
else
finally

'''

# x = int(input("Enter number : "))

try:
    x = int(input("Enter number : "))
    res = 10/x
except ZeroDivisionError:
    print("Something wrong happend!!")
except TypeError:
    print("You cannot divide with string")
except ValueError:
    print("Provide right value")
    
else:
    print("Result : ",res) 
finally:
    print("Program excuition done")           
