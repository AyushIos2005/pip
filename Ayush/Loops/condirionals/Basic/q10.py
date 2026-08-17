# Take a year and check if it is leap year or not.

# year = int(input("Enter a Year : "))
for year in range(2000,2101):
    if(year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
         print(year,"is Leap Year")
    else:
        print(year,"is Not Leap Year")

