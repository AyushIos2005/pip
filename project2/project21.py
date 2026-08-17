# Email Checker Using RegEx 
import regex as re 

email_condition="^[a-z]+[\._]?[a-z 0-9]+[@]\w+[.]\w{2,3}$"
user_email=input('Enter a email : ')

if re.search(email_condition,user_email) :
    print("Right ")
else:
    print("Oops Something is Worng")

