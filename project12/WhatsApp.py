# import pywhatkit as pyw
 
# pyw.sendwhatmsg(['+9170*****','+91891*****'],'Welcome to CodeHub',16,19)

import pywhatkit as pyw 
import time
numbers = [
    '+917044726076',
    '+918910330373',
    '+918145241653'
    ]

message = "How are you!!"

hr = 16
m = 27

for number in numbers:
    pyw.sendwhatmsg_instantly(number,message,wait_time=15)
    time.sleep(2) 