# Create a class Fan with speed settings.

class Fan:
    def __init__(self):
        self.fan_speed = 0
    def set_speed(self,speed):
        if speed >= 0 and speed <= 4:
            self.fan_speed = speed
    def show_speed(self):
        if self.fan_speed == 0:
            return "OFF"
        elif self.fan_speed == 1:
            return "VERY LOW"
        elif self.fan_speed == 2:
            return "LOW"
        elif self.fan_speed == 3:
            return "MEDIUM"
        elif self.fan_speed == 4:
            return "HIGH"
u1 = Fan()
u2 = Fan()
u3 = Fan()
u4 = Fan()
u1.set_speed(7)
u2.set_speed(6)
u3.set_speed(1)
u4.set_speed(2)

print(f"Speed of User1 is {u1.show_speed()}")
print(f"Speed of User2 is {u2.show_speed()}")
print(f"Speed of User3 is {u3.show_speed()}")
print(f"Speed of User4 is {u4.show_speed()}")
        
