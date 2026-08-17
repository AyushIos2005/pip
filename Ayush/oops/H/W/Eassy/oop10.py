# Add a method to check if a person is adult (age ≥ 18).
class Person:
    def check(self,age):
        if age.isdigit():
            if age> "12" and age < "18":
                print("Teenage")
            elif age >= "18":
                print("Adult")
            else:
                print("YOU are baby")
        else:
            print("Wrong")
p1 = Person()
while True:
    age = input("Enter your age : ")
    p1.check(age)
    option = input("Did you check again (y/n): ")
    if option == 'n' or option == 'N' :
        exit()

