# Create a class Rectangle to calculate area.

class Rectangle:
    def Calculate_Rec_AREA(self,length,breadth):
        return length*breadth

r1=Rectangle()
print("\t Welcome to Area Calculate")
length = int(input("Enter a length : "))
breath = int(input("Enter a breath : ")) 
x=r1.Calculate_Rec_AREA(length,breath)
print("Area of Rectangle is ",x)   