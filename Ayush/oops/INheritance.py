# base class

class Payment:
    def __init__(self,amount):
        self.amount = amount
    def pay(self):
        print("Processing Payment of : ",self.amount) 
class CreditcardPayment(Payment):
    pass
class UPIPayment(Payment):
    pass

p1 = CreditcardPayment(100)
p1.pay()

p2 = UPIPayment(1000)
p2.pay()
