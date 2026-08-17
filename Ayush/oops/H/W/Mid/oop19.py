from datetime import *
import time
import sys
class Library:
    def __init__(self):
        self.book = {}
        self.fine_per_day = 1.5

    def issue(self, u_id, book_list):
        issue_date = datetime.now()
        return_date = issue_date + timedelta(days=25)

        if u_id not in self.book:
            self.book[u_id] = []

        for book_name in book_list:
            self.book[u_id].append({
                "name": book_name,
                "date": issue_date
            })

        print("✅ Books Issued Successfully")
        print("📅 Return before:", return_date.strftime("%Y-%m-%d"))

    def return_b(self, u_id, book_name):
        if u_id not in self.book:
            print("⚠️ User not found")
            return

        for b in self.book[u_id]:
            if b["name"] == book_name:
                return_date = datetime.now()
                issue_date = b["date"]

                days = (return_date - issue_date).days

                if days > 25:
                    fine = (days - 25) * self.fine_per_day
                    print(f"⚠️ Late return! Days: {days}")
                    print(f"💰 Fine = ₹{fine}")
                else:
                    print(f"✅ Returned in {days} days (No fine)")

                self.book[u_id].remove(b)

                if len(self.book[u_id]) == 0:
                    del self.book[u_id]

                return

        print("⚠️ Book not found for this user")


# main
l1 = Library()

while True:
    print("\nX=================================X")
    print("X\t\t 1.Issue \t\tX")
    print("X\t\t 2.Return \t\tX")
    print("X\t\t 3.Exit \t\tX")
    print("X=================================X")

    choice = input("Enter a Choice : ")

    if choice == '1':
        u_id = int(input("Enter a u_id : "))
        total_no_book = int(input("Enter number of books: "))

        book_list = []
        for i in range(total_no_book):
            book_name = input(f"Enter book {i+1} name: ")
            book_list.append(book_name)

        l1.issue(u_id, book_list)

    elif choice == '2':
        u_id = int(input("Enter a u_id : "))
        book_name = input("Enter book name : ")
        l1.return_b(u_id, book_name)

    elif choice == '3':
        for i in range(5, 0, -1):
             sys.stdout.write(f"\r⏳ Exiting in {i}... ")
             sys.stdout.flush()
             time.sleep(1)
        
        exit()

    else:
        print("⚠️ Invalid Choice!!")