hours = int(input("Enter a time in hours (0 to 24): "))

if 0 <= hours <= 3 or hours == 24:
    print("Mid-night")
elif 4 <= hours <= 11:
    print("Morning")
elif 12 <= hours <= 15:
    print("Afternoon")
elif 16 <= hours <= 19:
    print("Evening")
elif 20 <= hours < 24:
    print("Night")
else:
    print("Invalid input! Please enter a value between 0 and 24.")
