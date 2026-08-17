

class ShoppingCart:
    def __init__(self):
        self.cart = {}
    def add(self,item,count): 
        if item in self.cart:
            self.cart[item] += count
        else:
            self.cart[item] = count    
        print("Item is add successfully")
    def remove_cart(self,item):
        if item in self.cart:
            del self.cart[item]
            print("Item is Successfully Removed")
        else:
            print("Not Found")
    def display(self):
        if not self.cart:
            print("Your Cart is Empty")
        else:
            print("Your Cart items : ") 
            for item,count in self.cart.items():

                print(f"{item} : {count}x")
s1 = ShoppingCart()
while True:
    print("1. Add Item")
    print("2. Remove Item")
    print("3. Display Cart")
    print("4. Exit")
    choice = input("Enter a choice : ")
    if choice == '1':
        item = input("Enter a items : ")
        count = int(input("Enter no. of count : "))
        if count == 0:
            count = 1 
        s1.add(item,count)
    elif choice == '2':
        item = input("Enter a item : ")
        s1.remove_cart(item)
    elif choice == '3':
        s1.display()
    elif choice == '4':
        exit()
    else:
        print("Invalid Choice!!")



         

        