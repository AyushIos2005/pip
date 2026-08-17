'''
--> Encapsulation

'''
class BankAccount:
    def __init__(self,name,balance):
        self.name = name
        self.__balance = balance #now balnce is private

    def deposit(self,amount):
        if amount > 0:
            self.__balance += amount
    def withdrawal(self,amount):
        if 0 < amount <= self.__balance:
            self.__balance -= amount
        else:
            print("Invalid Withdrawl")    
    def get_balance(self):
        return self.__balance       


acc1 = BankAccount("Pappu",1000)
# acc1.balance = 1000000
print("1st : ",acc1.get_balance())
acc1.deposit(20000)
# acc1.__balance = 1000000 no change...
print("2nd : ",acc1.get_balance())
acc1.withdrawal(5000)
print("3rd : ",acc1.get_balance())


