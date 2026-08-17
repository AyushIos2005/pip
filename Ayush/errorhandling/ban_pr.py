class InsufficientBalanceError(Exception):
    pass

class BankAccount:
    def __init__(self,balance):
        self.balance = balance
    def withdrawal(self,amount):
        if amount > self.balance:
            raise InsufficientBalanceError("Not engough balance")
        else:
            self.balance -= amount
            print("Withdraw Succesfull")
try:
    acc = BankAccount(2000)
    acc.withdrawal(0)
except InsufficientBalanceError as e:
    print("Transaction failed",e)


          