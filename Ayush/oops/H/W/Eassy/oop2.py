# Create a class Student with name and marks. Add a method to display details.

class Student:

    def __init__(self,name,mark):
        # self.__password == 8777
        self.name = name
        self.mark = mark
    def calculate_avg(self,mark):
        sum = 0
        for i in range(len(self.mark)):
            sum += mark[i]
        print("Avg marks obtain is : ",sum)
        print("Percentage obtain : ",sum/5,"%")         
    def display_marks_by_name(self,name,mark):
        print("The name of student is : "+self.name)
        print("Marks of Hindi : ",self.mark[0])
        print("Marks of English : ",self.mark[1])
        print("Marks of Phy : ",self.mark[2])
        print("Marks of Chem : ",self.mark[3])
        print("Marks of Comp : ",self.mark[4])
        x=input("Did you want to calculate avg(y/n) : ")
        if x == 'y' or x == 'Y':
            self.calculate_avg(self.mark)
        else:
            print("Thank You!!")    
name = input("Enter a name of student : ")
li = []
print("Enter a marks(hindi,eng,phy,chem,comp): ")
for i in range(0,5):
    x=int(input())
    li.append(x)
s1 = Student(name,li) 
s1.display_marks_by_name(name,li)   

        
            