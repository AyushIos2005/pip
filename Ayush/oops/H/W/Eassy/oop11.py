# Create a class Temperature to convert Celsius to Fahrenheit.
class Temperature:
    def convert(self,celsius):
        fahrenheit = (celsius * (9/5)) + 32
        return fahrenheit
def user_input():
    print("Welcome to Celsius to Fahrenheit")
    celsius = int(input("Enter a temperature in Celsius : "))
    obj1 = Temperature()
    k = obj1.convert(celsius)
    print(f"{celsius}oC in Fahrenheit {k}F")

user_input()            
    