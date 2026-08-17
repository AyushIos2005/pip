price = float(input("Enter product price: "))
print("Customer Types: [R] for Regular or [P] for Premium")
cust_type = input("Enter type (R/P): ").upper() # Converts input to uppercase for easier checking

if price >= 5000:
    if cust_type == 'R':
        discount = price * 0.10  # 10% discount
        final_price = price - discount
        print(f"Regular Customer: 10% discount applied. Saved: ${discount:.2f}")
        print(f"Total to pay: ${final_price:.2f}")
        
    elif cust_type == 'P':
        discount = price * 0.35  # 35% discount
        final_price = price - discount
        print(f"Premium Customer: 35% discount applied. Saved: ${discount:.2f}")
        print(f"Total to pay: ${final_price:.2f}")
    else:
        print("Invalid customer type. Use 'R' or 'P'.")
else:
    print("No discount available for purchases under 5000.")
    print(f"Total to pay: ${price:.2f}")
