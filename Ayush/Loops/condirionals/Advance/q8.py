# Take balance and withdrawal amount. Check if transaction is allowed.

balance = 100000

withdrawal = int(input("Enter Withdrawal Amount : "))
 
if withdrawal <= 0:
    print("Invalid amount. Please enter a postive value")
elif withdrawal <= balance:
    balance -= withdrawal
    print("Transaction Complete")
    print("Remaining Balance : ",balance)
else:
    print("Transaction failed.Insufficinet Funds")    

