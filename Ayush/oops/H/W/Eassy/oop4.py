# Create a class Circle to calculate circumference and area.
import math
class Circle:
    def area_circle(self,radius):
        return math.pi * (radius ** 2)
    def cum_circle(self,radius):
        return math.pi * 2 * radius
    def user_input_radius(self):
        radius = int(input("Enter a radius : "))
        area = self.area_circle(radius)
        cum = self.cum_circle(radius)
        print("Area of Circle : ",area)
        print("Circumference of Circle : ",cum)
c1 = Circle()
c1.user_input_radius()