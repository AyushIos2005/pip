# Total BILL AMOUNT WITH GST
price = float(input("Enter a price of product: "))
qty = int(input("Enter a qty of product : "))

total_price = price*qty
gst = total_price * 18/100

final_amount = total_price + gst
print("Total price : ",final_amount)