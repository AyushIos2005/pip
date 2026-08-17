# Create a class Light with on/off functionality
class Light:
    def __init__(self):
        self.function = 0
    def set_function(self,mode):
        if mode >= 0 and mode <= 1:
            self.function = mode
        else:
            print("Error")
    def show_function(self):
        if self.function == 1:
            return "ON"
        else:
            return "OFF"
u1 = Light()
u2 = Light()
u3 = Light()
u4 = Light()
u1.set_function(0)
u2.set_function(1)
u3.set_function(1)
u4.set_function(1)

print(f"Mode of light  of User1 is {u1.show_function()}")
print(f"Mode of light  of User2 is {u2.show_function()}")
print(f"Mode of light  of User3 is {u3.show_function()}")
print(f"Mode of light  of User4 is {u4.show_function()}")
        
                    
