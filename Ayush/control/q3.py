while(True):
    amt = int(input("Enter total amount: "))

    if amt >= 5000:
        print("Choose Payment Way")

        print("Press 1 for UPI,NetBanking")
        print("Press 2 for Card")
        print("Press 3 for Cash")
        payment = int(input("Enter number : "))
        if(payment == 1 or payment == 3):
            print("Thank You Visit Again \n Not Egilible for Discount")
        else:
            print("Thank You Visit Again \n Egiglible for Discount")    
    elif (amt > 0) and (amt < 5000):
        print("Not Eligible for discount")
    else:
        print("Please purchase items above 5000 to eligible")        