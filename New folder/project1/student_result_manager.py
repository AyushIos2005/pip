student = {}

while True:
    print("\n------STUDENT MANAGER APP-------")
    print("1. Add Student")
    print("2. View Student")
    print("3. Check Result")
    # print("4. Entry marks")
    print("4. Exit")


    choice = input("Enter your choice : ")
    if choice == '1':
        name = input("Enter a name of Student : ").capitalize()
        marks = int(input("Enter marks : "))
        student[name] = marks
        print(f'{name} Successfully Added')
    elif choice == '2':
        if not student:
            print("Not Student Record Found")
        else:
            for name,marks in student.items():
                print(name," : ",marks)        
    elif choice == '3':
        name = input("Enter student name : ").capitalize()

        if name in student:
            marks = student[name]

            if marks >= 40:
                print("Status : PASS")
            else:
                print("Status : FAIL")
        else:
            print("Student Record Not Found!")
    elif choice == "4":
        print("Exiting...")
        exit()   
    else:
        print("Invalid Choice!!\nTry Again!!")                     