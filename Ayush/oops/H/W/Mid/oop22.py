# Create a class Product with discount calculation.
class Product_Discount_Cal:
     def __init__(self, price, discount):
        self.price = price
        self.discount = discount
     def calcluate(self):
         return self.price - (self.price * self.discount / 100)


# main 
product_prices = float(input("Enter a product price : "))
disconut = float(input("Enter a discount(%) : "))
p1 = Product_Discount_Cal(product_prices,disconut)
# p2 = Product_Discount_Cal()
# p3 = Product_Discount_Cal()
print("Gross Price is : ₹",p1.calcluate())
