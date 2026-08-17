# Easy level
d = {}
def create_dictionary():
    n = int(input("Enter number of people : "))

    for i in range(n):
        name = input('Enter name : ')
        age = int(input("Enter age : "))

        d[name] = age

    
def display():
    print("Dictionary : ",d)

def access_value():
    key = input("Enter a key : ")

    print(f"Value at key {key} is {d[key]}")
def Check_key_exists(d):
    key = input("Enter a key : ")
    if key in d:
        return "True"
    else:
        return "False"    
def Count_Key():
    return len(d)
def Sum_Of_Value(d):
    return sum(d.values())        
def update_Value():
    key = input("Enter key to update : ")

    if key in d:
        value = int(input("Enter new age : "))
        d[key] = value
        print("Update successfully")
    else:
        print("Key not found")
def delete_key():
    key = input("Enter key to delete : ")

    if key in d:
        del d[key]
        print("Deleted Successfully")
    else:
        print("Key not found")
def Get_all_Keys():
       print("Keys : ",list(d.keys()))                 
def Get_all_Value():
    print("Value : ",list(d.values()))
def Merge_Two_Dictionaries():
    d2 = {}

    n = int(input("Enter number of element for second dictionary : "))
    for i in range(n):
        key = input("Enter key : ")
        value = int(input("Enter value : "))
        d2[key] = value

    d.update(d2)
    print("Merged Dictionary : ",d)
    
print("1.Create a dictionary with keys as names and values as ages. Return the dictionary.")
print("2.Return value of given key from dictionary.")
print("3.Return true if key exists in dictionary.")
print("4.Return total number of keys in dictionary.")
print("5.Return sum of all dictionary values.")
print("6.Update value of a given key.")
print("7.Remove a key from dictionary.")
print("8.Return list of all keys.")
print("9.Return list of all values.")
print("10.Merge two dictionaries into one.")
print("11.Display Dictionary ")
print("12.Exiting Program..")

while True:
    choice = int(input("Enter a  choice : "))

    if choice == 1:
        create_dictionary()
    elif choice == 2:
        access_value()
    elif choice == 3:
        print(Check_key_exists(d))
    elif choice == 4:
        print("Count of key is : ",Count_Key(d))
    elif choice == 5:
        print("Sum of Values in dictionary : ",Sum_Of_Value(d))
    elif choice == 6:
        update_Value()
    elif choice == 7:
        delete_key()
    elif choice == 8:
        Get_all_Keys()
    elif choice == 9:
        Get_all_Value()
    elif choice == 10:
        Merge_Two_Dictionaries()
    elif choice == 11:
        display()    
    elif choice == 12:
        exit()
    else:
        print("Try Again!!")




