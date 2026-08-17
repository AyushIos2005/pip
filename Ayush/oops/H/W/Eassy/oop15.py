class BankAccount:
    def __init__(self, amount):
        # We use self.__balance to keep it private
        self.__balance = amount

    def deposit(self, amt):
        if amt > 0:
            self.__balance += amt
            print(f"{amt} is successfully credited to your account!!")
        else:
            print("Invalid deposit amount.")

    def withdraw(self, amt):
        # Question 17: Prevent withdrawal if balance is insufficient
        if amt <= self.__balance:
            self.__balance -= amt
            print(f"{amt} has been withdrawn from your account.")
        else:
            print("Insufficient balance!")

    def get_balance(self):
        return self.__balance

# --- Execution ---
initial_amt = int(input("Enter initial balance to open account: "))
a1 = BankAccount(initial_amt)            

amt = int(input("Enter an amount for deposit: "))
a1.deposit(amt)

g = input("Do you want to withdraw? (y/n): ").lower()

if g == 'y':
    n = int(input("Enter withdraw amount: "))
    a1.withdraw(n)

print(f"Final Balance: {a1.get_balance()}")