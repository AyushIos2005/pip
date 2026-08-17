#  Create a class Password validator.
import string
class Password:
    def validator(self,password):
        if len(self.password) > 8:
            # print("Password Must be atleast more than 8 character")
            return 'weak'
        else:
           return 'oKay'    
        
#Main
password = input("Enter a password : ")
obj = Password()
print("Password Validator : ",obj.validator())