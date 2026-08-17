import random
import string
import requests

phone_number= ""
def send_otp(otp):
    url = "https://www.fast2sms.com/dev/bulkV2"

    params = {
        "authorization": "sVTNnrbov1WO4xwtG0uKfM96LIm82U5ezgJHkyidQFEp3hCPD7TYsngivtacSoRpmf8xQwjM3qU1KCIr",   # 🔑 put your Fast2SMS API key
        "variables_values": otp,
        "route": "q",
        "numbers": phone_number
    }

    response = requests.get(url, params=params)

    print("OTP Sent Successfully")
    # print("Response:", response.text) 

def gernate_otp():
    num = random.randint(100000, 999999)
    return num
def get_number():
    global phone_number
    number  = input("Enter a mobile number : ")

    if number.isdigit() and len(number) == 10:
        phone_number = number
        x = gernate_otp()
        send_otp(x)
    else:
        print("Please Enter Correct number!!")            

# main
get_number()


