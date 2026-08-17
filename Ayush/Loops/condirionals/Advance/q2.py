'''
Take age and gender and check special ticket discount eligibility.
'''
age = int(input("Enter Your Age : "))
gender = input("Enter Your Gender : ")

if gender == "F" or gender == 'f' :
    if age >= 16 and age < 21:
        print("Eligible for Special ticket discount of 10%!!")
    elif age >= 21 and age <25:
        print("Eligible for Special Bridal discount of 25%!!")
    else:
        print("Not Eligible for Discount!!")
elif gender == "M" or gender == 'm':
    print("Not Eligible for any Discount!!")
else:
    print("Wrong Input!!")                   
