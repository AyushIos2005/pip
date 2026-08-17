'''
14. Take username and check:
    - "admin" → Admin Access
    - "guest" → Guest Access
    - otherwise → Invalid User
'''

user_name = input("Enter a Username : ")

if user_name == "admin" :
    print("Admin Access")
elif user_name == "guest":
    print("Guest Access")
else:
    print("Invalid Username")

