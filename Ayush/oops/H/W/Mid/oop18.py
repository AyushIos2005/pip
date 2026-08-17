import math

# Base Class
class Shape:
    def area(self):
        # Default implementation (to be overridden)
        return 0

# Derived Class for Circle
class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * (self.radius ** 2)

# Derived Class for Square
class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2

# --- Example Usage ---
shapes = [Circle(5), Square(4)]

for s in shapes:
    print(f"The area of the {type(s).__name__} is: {s.area():.2 bomb}")