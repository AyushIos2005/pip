# Create a class Laptop with brand and price.

class Laptop:
    def showcase(self,brand,price):
        print(brand)
        print(price)

    def user_input(self):    
        brand = input("Enter a brand : ")
        price = int(input("Enter a price : "))
        self.showcase(brand,price)

# main function

obj = Laptop()
obj.user_input()