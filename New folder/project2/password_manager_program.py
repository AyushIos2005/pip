import random
import string

passwords = {}
passkey = ""

# Load saved passwords
try:
    with open("Password.txt", "r") as file:
        for line in file:
            site, pwd = line.strip().split(":")
            passwords[site] = pwd
except:
    pass

# Generate password
def generate_password():
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(8))

while True:
    print("\n--------PERSONAL PASSWORD MANAGER----------")
    print("1. Save Password")
    print("2. View Passwords")
    print("3. Generate Password")
    print("4. Exit")

    choice = input("Enter a choice : ")

    if choice == '1':
        site = input("Enter website name : ")
        pwd = input("Enter password : ")

        passwords[site] = pwd

        with open("Password.txt", "a") as file:
            file.write(f"{site}:{pwd}\n")

        print("Password saved successfully!")

    elif choice == '2':
        if passkey == "":
            passkey = input("Set your passkey (first time): ")

        p = input("Enter your passkey : ")

        if passkey == p:
            if not passwords:
                print("No Data Found!!")
            else:
                for site, pwd in passwords.items():
                    print(f"{site} => {pwd}")
        else:
            print("Access Denined!")

    elif choice == '3':
        print("Generated Password:", generate_password())

    elif choice == '4':
        print("Exiting....")
        break

    else:
        print("Invalid Input")