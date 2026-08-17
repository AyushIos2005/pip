# # class Payment():
# #     def pay(self):
# #         print("Processing Payment")

# # p = Payment()
# # p.pay()


# class Animal():
#     def sound(self):
#         print("Animal Makes Sound")
# class Dog(Animal):
#     def sound(self):
#         print("Brake")
        
# class Cat(Animal):
#     def sound(self):
#         print("Meowoo")


# animals = [Dog(),Cat()]

# for a in animals:
#     a.sound()



from abc import ABC,abstractmethod


class Animal(ABC):
    @abstractmethod
    def sound(self):
        pass
class Dog(Animal):
    pass

