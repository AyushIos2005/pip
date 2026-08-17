import qrcode as qr

def QRMaker(link,filename):
    img = qr.make(link)
    img.save(filename+".png")
        
while(1):
    print("Press 1 for make QR Code")
    print("Press 2 for exit")
    choice = int(input("Enter a choice : "))
    
    if choice == 1 :
        link=input("Enter a link : ")
        filename = input("Enter a filename : ")
        QRMaker(link,filename)
    elif choice == 2 :
        print("Thank You for using....") 
        exit();
    else:
        print("Try Again...")
 
               




