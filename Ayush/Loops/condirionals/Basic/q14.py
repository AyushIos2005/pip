# # Take password and check if it matches "python123".

# password = input("Enter a Password : ")

# if password == "ayush123":
#     print("Matched Access Accepted")
# else:
#     print("Access Deined")    


correct_password = "python123"

for i in range(3):
    password = input("Enter Password: ")

    if password == correct_password:
        print("Access Accepted")
        break
    else:
        print("Wrong Password")

else:
    print("Account Locked")